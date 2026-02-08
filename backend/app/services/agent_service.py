"""
OpenAI Agent Service for Task Management
Handles natural language interactions with the task system via MCP tools.
"""
from openai import OpenAI
import os
import json
import httpx
from typing import List, Dict, Any, Optional


class TaskAgent:
    """
    AI Agent that manages tasks through natural language using OpenAI's API.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        self.mcp_server_url = "http://localhost:8002"

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define the tools available to the agent.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Retrieve all tasks for the user. Can optionally filter by status (pending, in-progress, completed).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in-progress", "completed"],
                                "description": "Filter tasks by status"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task with a title, optional description, and priority level.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of the task"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Priority level of the task"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task's title, description, status, or priority.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the task"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in-progress", "completed"],
                                "description": "New status for the task"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New priority for the task"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_priority",
                    "description": "Analyze all tasks and recommend what the user should work on first based on priority, status, and deadlines.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute a tool by calling the MCP server.
        """
        try:
            # Add user_id to arguments
            arguments["user_id"] = user_id

            # Special handling for summarize_priority
            if tool_name == "summarize_priority":
                # First get all tasks
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.mcp_server_url}/tools/call",
                        json={"tool": "get_tasks", "arguments": {"user_id": user_id}}
                    )
                    result = response.json()

                    if result.get("success"):
                        tasks = result.get("data", [])
                        # Return tasks for the AI to analyze
                        return {
                            "success": True,
                            "data": {
                                "tasks": tasks,
                                "message": "Analyze these tasks and provide recommendations"
                            }
                        }
                    return result

            # Call MCP server for other tools
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/tools/call",
                    json={"tool": tool_name, "arguments": arguments}
                )
                return response.json()

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def chat(
        self,
        message: str,
        user_id: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a chat message and return the agent's response.
        Handles tool calls automatically.
        """
        if history is None:
            history = []

        # Build messages with system prompt
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant that manages tasks for users.
You can help users:
- View their tasks (get_tasks)
- Create new tasks (create_task)
- Update existing tasks (update_task)
- Get recommendations on what to work on first (summarize_priority)

When users ask about their tasks, use the appropriate tools to help them.
Be conversational and helpful. When creating tasks, extract relevant details from the user's message.
For example, if they say "meeting with Bilal at 5pm", create a task with title "Meeting with Bilal" and include "5pm" in the description."""
            }
        ] + history + [{"role": "user", "content": message}]

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.get_tools(),
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            # Add assistant message with tool calls to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the tool
                tool_result = await self.execute_tool(
                    function_name,
                    function_args,
                    user_id
                )

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Get final response from the model
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return final_response.choices[0].message.content

        # No tool calls, return direct response
        return assistant_message.content or "I'm here to help with your tasks!"
