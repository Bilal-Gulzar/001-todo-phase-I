"""
Chat API endpoints for AI agent interactions using OpenAI GPT-4o-mini.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..agents.task_agent_simple import run_agent
from ..api.deps import get_current_user
from ..models.user import User
from ..config import settings

router = APIRouter()


class ChatMessage(BaseModel):
    """Request model for chat messages."""
    message: str
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to the AI agent and get a response.
    The agent can interact with tasks using natural language.
    """
    try:
        # Check if OpenAI API key is configured
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="AI Agent not configured: OPENAI_API_KEY not set in environment"
            )

        # Run the agent with user message and user ID
        response = await run_agent(
            user_message=chat_message.message,
            user_id=current_user.id
        )

        # CRITICAL: NEVER return technical errors to users
        # Check for ANY error indicators in the response
        error_indicators = [
            "Agent error", "Error code", "tool_use_failed", "invalid_request",
            "validation failed", "400", "500", "Exception", "Traceback",
            "failed_generation", "tool call validation", "'error':", "\"error\":"
        ]

        # Convert response to lowercase for case-insensitive checking
        response_lower = response.lower()

        # If ANY error indicator is found, return friendly message
        if any(indicator.lower() in response_lower for indicator in error_indicators):
            print(f"ERROR FILTERED: {response[:200]}")  # Log for debugging
            return ChatResponse(response="""I can help you manage your tasks! Try:

• "list tasks" or "show tasks"
• "add task [name]" - Create a new task
• "mark [name] done" - Complete a task
• "delete [name]" - Remove a task

What would you like to do?""")

        return ChatResponse(response=response)

    except HTTPException:
        raise
    except Exception as e:
        # Convert ANY exception to user-friendly message
        print(f"EXCEPTION CAUGHT: {str(e)}")  # Log for debugging
        return ChatResponse(response="""I can help you manage your tasks! Try:

• "list tasks" or "show tasks"
• "add task [name]" - Create a new task
• "mark [name] done" - Complete a task
• "delete [name]" - Remove a task

What would you like to do?""")


@router.get("/chat/health")
async def chat_health():
    """
    Check if the chat service is healthy and configured.
    """
    has_api_key = bool(settings.openai_api_key)

    return {
        "status": "healthy" if has_api_key else "misconfigured",
        "openai_configured": has_api_key,
        "model": "openai/gpt-4o-mini"
    }
