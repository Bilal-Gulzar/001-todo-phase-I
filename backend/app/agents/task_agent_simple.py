"""
Task Agent - Simple Implementation
Uses OpenAI chat completions API directly with OpenRouter GPT-4o-mini (no Agents SDK)
"""
from openai import AsyncOpenAI
from sqlmodel import Session
import json
from ..database import engine
from ..services.task_service import create_task as create_task_service, get_all_tasks, update_task as update_task_service
from ..models.task import TaskCreate, TaskUpdate
from ..config import settings


async def run_agent(user_message: str, user_id: str) -> str:
    """
    Run the agent with a user message and return the response.
    Uses direct OpenAI chat completions API with function calling.
    """
    try:
        # Get OpenAI API key
        openai_api_key = settings.openai_api_key
        if not openai_api_key:
            return "⚠️ AI Agent not configured: OPENAI_API_KEY not set"

        # Create OpenAI client for OpenRouter
        client = AsyncOpenAI(
            api_key=openai_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Define available functions
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_my_tasks_args",
                    "description": "Retrieve and display all tasks for the current user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Optional filter (currently ignored)",
                                "nullable": True
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The task title"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Task priority",
                                "default": "medium"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove",
                    "description": "Delete a task by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The task name to remove"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update",
                    "description": "Update a task's status or priority",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The task name to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["completed", "pending"],
                                "description": "New status",
                                "nullable": True
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New priority",
                                "nullable": True
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        ]

        # System message
        system_message = """You are a task manager assistant. You can ONLY perform these actions:

1. list_my_tasks_args - List all tasks (call with filter=None)
2. add - Create a new task (requires name, optional priority)
3. remove - Delete a task (requires name)
4. update - Update task status or priority (requires name, optional status/priority)

FORMATTING: Display tasks as:
1. [ ] Task Name (priority: medium)
2. [✓] Completed Task (priority: high)

Always show tool results to the user. Be friendly and conversational."""

        # Call the API with GPT-4o-mini
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # If no tool calls, return the message
        if not message.tool_calls:
            return message.content or "I'm here to help with your tasks!"

        # Execute tool calls
        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Execute the function
            result = await execute_function(function_name, arguments, user_id)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": result
            })

        # Get final response with tool results using GPT-4o-mini
        final_response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
                message,
                *tool_results
            ]
        )

        return final_response.choices[0].message.content or "Done!"

    except Exception as e:
        error_msg = str(e)
        print(f"Agent error: {error_msg}")

        # Return friendly error message
        if "429" in error_msg or "quota" in error_msg.lower():
            return "⚠️ API quota exceeded. Please try again in a moment."
        elif "404" in error_msg:
            return "⚠️ Service temporarily unavailable. Please try again."
        else:
            return "I had trouble processing that request. Try: 'list tasks', 'add task [name]', 'mark [task] done', or 'delete [task]'."


async def execute_function(function_name: str, arguments: dict, user_id: str) -> str:
    """Execute a tool function and return the result."""
    try:
        with Session(engine) as session:
            if function_name == "list_my_tasks_args":
                tasks = get_all_tasks(session, user_id)
                if not tasks:
                    return "No tasks found."

                lines = ["📋 **Your Tasks:**\n"]
                for i, t in enumerate(tasks, 1):
                    checkbox = "✓" if t.status == "completed" else " "
                    priority = t.priority if t.priority else "medium"
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
                    lines.append(f"{i}. [{checkbox}] {t.title} {priority_emoji} ({priority})")

                lines.append("\n💡 You can add, update, or remove tasks anytime!")
                return "\n".join(lines)

            elif function_name == "add":
                name = arguments.get("name")
                priority = arguments.get("priority", "medium")
                task_data = TaskCreate(title=name, description="", priority=priority)
                task = create_task_service(session, task_data, user_id)
                # Service already commits - no need for extra commit
                return f"✅ Added task: **{task.title}** (priority: {priority})"

            elif function_name == "remove":
                name = arguments.get("name")
                tasks = get_all_tasks(session, user_id)
                task = None
                for t in tasks:
                    if name.lower() in t.title.lower():
                        task = t
                        break

                if not task:
                    return f"❌ Task not found: '{name}'"

                task_title = task.title
                session.delete(task)
                session.commit()
                return f"🗑️ Removed task: **{task_title}**"

            elif function_name == "update":
                name = arguments.get("name")
                status = arguments.get("status")
                priority = arguments.get("priority")

                tasks = get_all_tasks(session, user_id)
                task = None
                for t in tasks:
                    if name.lower() in t.title.lower():
                        task = t
                        break

                if not task:
                    return f"❌ Task not found: '{name}'"

                update_dict = {}
                if status:
                    update_dict["status"] = status
                if priority:
                    update_dict["priority"] = priority

                if not update_dict:
                    return "⚠️ No updates provided. Specify status or priority."

                update_data = TaskUpdate(**update_dict)
                updated_task = update_task_service(session, str(task.id), update_data, user_id)
                # Service already commits - no need for extra commit

                if not updated_task:
                    return f"❌ Failed to update task: '{name}'"

                changes = []
                if status:
                    changes.append(f"status: {status}")
                if priority:
                    changes.append(f"priority: {priority}")
                return f"✏️ Updated **{updated_task.title}** - {', '.join(changes)}"

            else:
                return f"❌ Unknown function: {function_name}"

    except Exception as e:
        print(f"Error in execute_function: {str(e)}")
        return f"❌ Error executing {function_name}: {str(e)}"
