"""
Task Agent - Clean Version Without Tracing
Uses OpenAI Agents SDK with OpenRouter (GPT-4o-mini), flat tool names, and error handling.
"""
from agents import Agent, Runner, function_tool, RunConfig, OpenAIProvider
from openai import AsyncOpenAI
from sqlmodel import Session
from ..database import engine
from ..services.task_service import create_task as create_task_service, get_all_tasks, update_task as update_task_service, delete_task as delete_task_service
from ..models.task import TaskCreate, TaskUpdate
from ..config import settings


async def run_agent(user_message: str, user_id: str) -> str:
    """
    Run the agent with a user message and return the response.

    Args:
        user_message: The user's input message
        user_id: The ID of the current user

    Returns:
        The agent's response (always a friendly string, never technical errors)
    """
    try:
        # Get OpenAI API key from environment
        openai_api_key = settings.openai_api_key

        if not openai_api_key:
            return "⚠️ AI Agent not configured: OPENAI_API_KEY not set"

        # Create custom AsyncOpenAI client for OpenRouter
        openai_client = AsyncOpenAI(
            api_key=openai_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Create OpenAI provider with custom client
        model_provider = OpenAIProvider(openai_client=openai_client)

        # Define tools - NO **kwargs to avoid Pydantic schema errors

        @function_tool
        def list_my_tasks_args(filter: str = None) -> str:
            """
            Retrieve and display all tasks for the current user.

            This is the ONLY tool for listing tasks. Always return the full task list.

            Args:
                filter: Optional filter parameter (currently ignored, accepts null)

            Returns:
                Formatted markdown list of all tasks with checkboxes
            """
            try:
                with Session(engine) as session:
                    tasks = get_all_tasks(session, user_id)
                    if not tasks:
                        return "No tasks found."

                    lines = ["Here are your tasks:\n"]
                    for i, t in enumerate(tasks, 1):
                        checkbox = "[✓]" if t.status == "completed" else "[ ]"
                        priority = t.priority if t.priority else "medium"
                        lines.append(f"{i}. {checkbox} {t.title} (priority: {priority})")

                    return "\n".join(lines)
            except Exception as e:
                return "Error fetching tasks."

        @function_tool
        def add(name: str, priority: str = "medium") -> str:
            """
            Create a new task with the specified name and priority.

            Args:
                name: The title/name of the task to create
                priority: Task priority level (low, medium, high). Defaults to medium

            Returns:
                Confirmation message with the created task name
            """
            try:
                with Session(engine) as session:
                    task_data = TaskCreate(title=name, description="", priority=priority)
                    task = create_task_service(session, task_data, user_id)
                    return f"✓ Added task: '{task.title}' with {priority} priority"
            except Exception as e:
                return "Error adding task."

        @function_tool
        def remove(name: str) -> str:
            """
            Delete a task by searching for its name.

            Args:
                name: The name of the task to remove (partial match supported)

            Returns:
                Confirmation message with the removed task name
            """
            try:
                with Session(engine) as session:
                    tasks = get_all_tasks(session, user_id)
                    if not tasks:
                        return "No tasks found."

                    task = None
                    for t in tasks:
                        if name.lower() in t.title.lower():
                            task = t
                            break

                    if not task:
                        return f"Task not found: '{name}'"

                    task_title = task.title
                    session.delete(task)
                    session.commit()

                    return f"✓ Removed task: '{task_title}'"
            except Exception as e:
                return "Error removing task."

        @function_tool
        def update(name: str, status: str = None, priority: str = None) -> str:
            """
            Update a task's status or priority by searching for its name.

            Args:
                name: The name of the task to update (partial match supported)
                status: New status for the task (e.g., "completed", "pending")
                priority: New priority for the task (e.g., "low", "medium", "high")

            Returns:
                Confirmation message with the updated task details
            """
            try:
                with Session(engine) as session:
                    tasks = get_all_tasks(session, user_id)
                    if not tasks:
                        return "No tasks found."

                    task = None
                    for t in tasks:
                        if name.lower() in t.title.lower():
                            task = t
                            break

                    if not task:
                        return f"Task not found: '{name}'"

                    # Build update data based on what was provided
                    update_dict = {}
                    if status is not None:
                        update_dict["status"] = status
                    if priority is not None:
                        update_dict["priority"] = priority

                    if not update_dict:
                        return "No updates provided. Specify status or priority."

                    update_data = TaskUpdate(**update_dict)
                    updated_task = update_task_service(session, str(task.id), update_data, user_id)

                    if updated_task:
                        changes = []
                        if status:
                            changes.append(f"status: {status}")
                        if priority:
                            changes.append(f"priority: {priority}")
                        return f"✓ Updated '{updated_task.title}' - {', '.join(changes)}"
                    else:
                        return "Failed to update task"
            except Exception as e:
                return "Error updating task."

        # Create Agent with strict instructions (SDK will use env vars for client)
        agent = Agent(
            name="TaskManager",
            instructions="""You are a task manager assistant. You can ONLY perform these specific actions:

AVAILABLE TOOLS (use EXACTLY these names):
1. list_my_tasks_args - To see all tasks
   - When listing tasks, you MUST call list_my_tasks_args with filter=None
   - Never use words like "fetch" or invent other tool names
   - Example: list_my_tasks_args(filter=None)

2. add - To create a new task
   - Required: name (task title)
   - Optional: priority (low, medium, high)
   - Example: add(name="Buy groceries", priority="high")

3. remove - To delete a task
   - Required: name (task to remove)
   - Example: remove(name="Buy groceries")

4. update - To change task status or priority
   - Required: name (task to update)
   - Optional: status ("completed" or "pending")
   - Optional: priority ("low", "medium", "high")
   - Example: update(name="Buy groceries", status="completed")

FORMATTING RULES:
When displaying tasks, use this exact format:
1. [ ] Task Name (priority: medium)
2. [✓] Completed Task (priority: high)

- Use [ ] for incomplete tasks
- Use [✓] for completed tasks
- Always show priority level

STRICT LIMITATIONS:
- If a user asks for something you cannot do, politely deny and explain your limitations
- Do NOT attempt to guess or invent tools
- Do NOT use tool names other than the 4 listed above
- You can ONLY: list tasks, add tasks, remove tasks, and update tasks
- You CANNOT: search the web, send emails, access files, or perform any other actions

BEHAVIOR:
- When user asks to see/list/show tasks, call list_my_tasks_args(filter=None) and display the full results
- Always show tool results to the user, don't just summarize
- Be friendly and conversational
- If you don't understand a request, ask for clarification""",
            model="openai/gpt-4o-mini",
            tools=[list_my_tasks_args, add, remove, update]
        )

        # Run the agent with specific error handling and custom model provider
        try:
            run_config = RunConfig(
                model_provider=model_provider,
                tracing_disabled=True  # Disable tracing to avoid OpenAI API key errors
            )
            result = await Runner.run(agent, user_message, run_config=run_config)

            # Debug logging
            print("=" * 50)
            print("DEBUG: Agent Result")
            print("=" * 50)
            print(f"Result Type: {type(result)}")
            print(f"Result: {result}")
            if hasattr(result, 'final_output'):
                print(f"Final Output: {result.final_output}")
            print("=" * 50)

            # Extract response
            if result and hasattr(result, 'final_output') and result.final_output:
                output = result.final_output.strip()

                # Check for error indicators
                error_keywords = [
                    'Agent error', 'Error code', 'tool_use_failed',
                    'invalid_request', 'failed_generation', '400', '500'
                ]

                if any(keyword in output for keyword in error_keywords):
                    return "I encountered a problem with that specific request. Please try rephrasing, or ask me to 'list tasks', 'add a task', 'update a task', or 'remove a task'."

                return output if output else "Done! Ask me to 'list tasks' to see your list."
            else:
                return "Done! Ask me to 'list tasks' to see your list."

        except Exception as e:
            error_msg = str(e)
            print(f"Agent execution error: {error_msg}")

            # Friendly error message instead of technical details
            if "tool_use_failed" in error_msg or "400" in error_msg:
                return "I encountered a problem with that specific request. Please try asking me to 'list my tasks', 'add task [name]', 'update [task] priority to [level]', or 'remove [task]'."
            else:
                return "I had trouble processing that request. Try: 'list tasks', 'add task [name]', 'mark [task] done', or 'delete [task]'."

    except Exception as e:
        error_msg = str(e)
        print(f"Agent setup error: {error_msg}")
        return "I'm having trouble starting up. Please try again in a moment."


