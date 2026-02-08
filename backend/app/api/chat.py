"""
Chat API endpoints for AI agent interactions using Gemini 2.0 Flash.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..agents.task_agent import run_agent
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
        # Check if Gemini API key is configured
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="AI Agent not configured: GEMINI_API_KEY not set in environment"
            )

        # Run the agent with user message and user ID
        response = await run_agent(
            user_message=chat_message.message,
            user_id=current_user.id
        )

        return ChatResponse(response=response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/chat/health")
async def chat_health():
    """
    Check if the chat service is healthy and configured.
    """
    has_api_key = bool(settings.gemini_api_key)

    return {
        "status": "healthy" if has_api_key else "misconfigured",
        "gemini_configured": has_api_key,
        "model": "gemini-2.0-flash-exp"
    }
