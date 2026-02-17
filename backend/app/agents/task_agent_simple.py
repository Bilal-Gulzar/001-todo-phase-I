"""
Task Agent - Simple Implementation
Uses OpenAI chat completions API with OpenRouter (GPT-4o-mini via OpenRouter)
"""
from openai import AsyncOpenAI
from sqlmodel import Session
import json
from ..database import engine
from ..services.task_service import create_task as create_task_service, get_all_tasks, update_task as update_task_service, delete_task as delete_task_service
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

        # Preprocess: Detect rename intent and make it explicit
        import re
        rename_patterns = [
            r'rename\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'change\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'update\s+(?:the\s+)?name\s+of\s+(.+?)\s+to\s+(.+)',
            r'call\s+(.+?)\s+(?:as\s+)?(.+)'
        ]

        for pattern in rename_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                # Add explicit instruction to use rename function
                user_message = f"{user_message}\n\n[SYSTEM INSTRUCTION: This is a RENAME request. You MUST use the 'rename' function with current_name='{match.group(1).strip()}' and new_name='{match.group(2).strip()}'. DO NOT suggest removing and adding.]"
                break

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
                    "description": "Update a task's status or priority (NOT for renaming - use rename function instead)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The current task name to update"
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
            },
            {
                "type": "function",
                "function": {
                    "name": "rename",
                    "description": "RENAME A TASK - Use this function whenever the user wants to change a task's name. Trigger phrases: 'rename X to Y', 'change X to Y', 'update name of X to Y', 'call X as Y'. Example: User says 'rename clean house to kitchen' -> call rename(current_name='clean house', new_name='kitchen'). DO NOT suggest removing and adding - just call this function.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "current_name": {
                                "type": "string",
                                "description": "The current task name to be renamed"
                            },
                            "new_name": {
                                "type": "string",
                                "description": "The new name for the task"
                            }
                        },
                        "required": ["current_name", "new_name"]
                    }
                }
            }
        ]

        # System message with explicit rename instructions
        system_message = """You are a task manager assistant.

AVAILABLE FUNCTIONS:
1. list_my_tasks_args - List all tasks
2. add - Create a new task (name, priority)
3. remove - Delete a task (name)
4. update - Change task status or priority ONLY
5. rename - Change a task's name (current_name, new_name)

CRITICAL: When user wants to change a task's name, you MUST use the 'rename' function.
DO NOT suggest removing and adding a new task. ALWAYS use rename.

Trigger words for rename: "rename", "change name", "update name", "call it"

FORMATTING: Display tasks as:
1. [ ] Task Name (priority: medium)
2. [✓] Completed Task (priority: high)

Be friendly and conversational."""

        # Call the API with GPT-4o-mini via OpenRouter
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            tools=tools,
            tool_choice="auto",
            extra_headers={
                "HTTP-Referer": "http://localhost:8001",
                "X-Title": "Todo App AI Agent"
            }
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

        # Get final response with tool results
        final_response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
                message,
                *tool_results
            ],
            extra_headers={
                "HTTP-Referer": "http://localhost:8001",
                "X-Title": "Todo App AI Agent"
            }
        )

        return final_response.choices[0].message.content or "Done!"

    except Exception as e:
        error_msg = str(e)
        print(f"Agent error: {error_msg}")
        import traceback
        traceback.print_exc()

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

                task_id = str(task.id)
                success = delete_task_service(session, task_id, user_id)

                if success:
                    return f"🗑️ Removed task: **{task.title}**"
                else:
                    return f"❌ Failed to remove task: '{name}'"

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

            elif function_name == "rename":
                current_name = arguments.get("current_name")
                new_name = arguments.get("new_name")

                tasks = get_all_tasks(session, user_id)
                task = None
                for t in tasks:
                    if current_name.lower() in t.title.lower():
                        task = t
                        break

                if not task:
                    return f"❌ Task not found: '{current_name}'"

                update_data = TaskUpdate(title=new_name)
                updated_task = update_task_service(session, str(task.id), update_data, user_id)
                # Service already commits - no need for extra commit

                if not updated_task:
                    return f"❌ Failed to rename task: '{current_name}'"

                return f"✏️ Renamed task from '**{current_name}**' to '**{updated_task.title}**'"

            else:
                return f"❌ Unknown function: {function_name}"

    except Exception as e:
        print(f"Error in execute_function: {str(e)}")
        return f"❌ Error executing {function_name}: {str(e)}"
