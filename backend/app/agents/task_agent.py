"""
Task Agent using Groq (Llama 3.3) via OpenAI-compatible bridge.
Follows the Panaversity OpenAI Agents SDK pattern.
"""
from agents import Agent, Runner, AsyncOpenAI, set_default_openai_client, set_tracing_disabled, set_default_openai_api, function_tool
from sqlmodel import Session
from typing import Optional
from ..database import engine
from ..services.task_service import create_task, get_all_tasks, update_task
from ..models.task import TaskCreate, TaskUpdate
from ..config import settings


async def run_agent(user_message: str, user_id: str) -> str:
    """
    Run the agent with a user message and return the response.

    Args:
        user_message: The user's input message
        user_id: The ID of the current user

    Returns:
        The agent's response
    """
    try:
        # Get Groq API key from settings
        groq_api_key = settings.groq_api_key

        if not groq_api_key:
            return "⚠️ AI Agent not configured: GROQ_API_KEY not set"

        # Disable tracing
        set_tracing_disabled(disabled=True)

        # Configure global API
        set_default_openai_api("chat_completions")

        # Define tools as closures that capture user_id
        @function_tool
        def create_todo_task(title: str, description: str = "", priority: str = "medium") -> str:
            """
            Adds a new task to the user's todo list.

            Args:
                title: The title of the task (required)
                description: Optional description of the task
                priority: Priority level (low, medium, high)

            Returns:
                Success message with task details
            """
            try:
                with Session(engine) as session:
                    task_data = TaskCreate(
                        title=title,
                        description=description,
                        priority=priority
                    )
                    task = create_task(session, task_data, user_id)
                    return f"Created task: '{task.title}' (ID: {task.id}, Priority: {task.priority})"
            except Exception as e:
                return f"Error creating task: {str(e)}"

        @function_tool
        def list_my_tasks(filter: Optional[str] = None) -> str:
            """
            List all tasks for the user.

            Args:
                filter: Optional. Not used. Leave empty.

            Returns:
                Formatted list of all tasks
            """
            try:
                with Session(engine) as session:
                    tasks = get_all_tasks(session, user_id)

                    if not tasks:
                        return "You have no tasks."

                    # Format tasks for display with plain text bullet points
                    result = f"You have {len(tasks)} tasks:\n\n"
                    for i, task in enumerate(tasks, 1):
                        result += f"• {task.title}\n"
                        result += f"  Status: {task.status}\n"
                        result += f"  Priority: {task.priority}\n"
                        if task.description:
                            result += f"  Description: {task.description}\n"
                        result += f"  ID: {task.id}\n\n"

                    return result
            except Exception as e:
                return f"Error fetching tasks: {str(e)}"

        @function_tool
        def update_existing_task(task_id: str, status: Optional[str] = None, priority: Optional[str] = None) -> str:
            """
            Updates an existing task's status, priority, or both.

            Args:
                task_id: The UUID of the task (required).
                status: New status ('pending', 'in-progress', 'completed').
                priority: New priority ('low', 'medium', 'high').

            Returns:
                Success message with updated task details
            """
            try:
                with Session(engine) as session:
                    # Pass both to TaskUpdate model
                    update_data = TaskUpdate(status=status, priority=priority)
                    task = update_task(session, task_id, update_data, user_id)

                    if not task:
                        return f"Task {task_id} not found."

                    return f"Updated task '{task.title}': Status={task.status}, Priority={task.priority}"
            except Exception as e:
                return f"Error: {str(e)}"

        @function_tool
        def delete_todo_task(task_id: str) -> str:
            """
            Deletes a task permanently from the user's todo list. Use this when the user wants to remove a task completely.

            Args:
                task_id: The UUID of the task to delete (required, must be a valid task ID from the user's task list)

            Returns:
                A success message string confirming the deletion, or an error message if the task was not found

            Example:
                delete_todo_task("305a2d95-2adc-4f81-adce-2571104f6a80")
            """
            try:
                with Session(engine) as session:
                    # First, get the task to verify it exists and belongs to the user
                    from sqlmodel import select
                    from ..models.task import Task

                    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
                    task = session.exec(statement).first()

                    if not task:
                        return f"Task not found with ID: {task_id}. Please check the task ID and try again."

                    task_title = task.title

                    # Delete the task
                    session.delete(task)
                    session.commit()

                    return f"Successfully deleted task '{task_title}'"
            except Exception as e:
                return f"Error deleting task: {str(e)}"

        # 1. Initialize the AsyncOpenAI client for Groq
        client = AsyncOpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        # 2. Set global client
        set_default_openai_client(client)

        # 3. Initialize the Agent with model string
        agent = Agent(
            name="Todo Assistant",
            instructions="""You are a helpful task management assistant.

You can help users:
- Create new tasks
- List all tasks
- Update task status (mark as pending, in-progress, or completed)
- Update task priority (low, medium, high)
- Delete tasks

When a user asks to update or delete a task:
1. First call list_my_tasks to see all tasks and their IDs
2. Find the matching task by title
3. Use the task's UUID to call update_existing_task or delete_todo_task

When creating tasks from natural language (e.g., "meeting with Bilal at 5pm"):
- Extract the main subject as the title
- Put time/date details in the description
- Set priority based on urgency (default: medium)

Always confirm what you did after completing an action.
""",
            model="llama-3.3-70b-versatile",
            tools=[create_todo_task, list_my_tasks, update_existing_task, delete_todo_task]
        )

        # 4. Run the agent with the user message
        try:
            result = await Runner.run(agent, user_message)

            # Ensure we always return a string response
            if result and hasattr(result, 'final_output') and result.final_output:
                # Check if final_output is not just whitespace
                if result.final_output.strip():
                    return result.final_output
                else:
                    return "I have processed your request."
            else:
                # Fallback if no final_output
                return "I have processed your request."
        except Exception as runner_error:
            return f"Agent error: {str(runner_error)}"

    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
