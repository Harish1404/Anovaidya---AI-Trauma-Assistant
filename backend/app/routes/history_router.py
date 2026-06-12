from typing import List, Optional, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from app.db.mongodb import get_database_client
from app.core.config import settings

logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/api/history", tags=["History"])


class SessionSummary(BaseModel):
    session_id: str
    updated_at: datetime
    severity_score: Optional[int] = None
    chief_complaint: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    user_id: str
    messages: List[Dict[str, str]]
    severity_score: Optional[int] = None


@router.get("/sessions/{user_id}", response_model=List[SessionSummary])
async def get_user_sessions(user_id: str):
    """List all past chat sessions for a specific user, sorted by updated_at descending."""
    try:
        db = get_database_client()[settings.DB_NAME]
        cursor = db["chat_history"].find({"user_id": user_id}).sort("updated_at", -1)
        sessions_doc = await cursor.to_list(length=100)

        sessions = []
        for doc in sessions_doc:
            messages = doc.get("messages", [])
            
            # Find the first user message to extract a snippet as the chief complaint
            chief_complaint = "No details provided"
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    chief_complaint = content[:60] + "..." if len(content) > 60 else content
                    break

            sessions.append(SessionSummary(
                session_id=doc["session_id"],
                updated_at=doc["updated_at"],
                severity_score=doc.get("severity_score"),
                chief_complaint=chief_complaint
            ))
            
        return sessions
    except Exception as e:
        logger.error(f"[HISTORY] Error listing user sessions: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve session list.")


@router.get("/chat/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Retrieve full chat history for a specific session."""
    try:
        db = get_database_client()[settings.DB_NAME]
        doc = await db["chat_history"].find_one({"session_id": session_id})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Session history not found.")
            
        return SessionHistoryResponse(
            session_id=doc["session_id"],
            user_id=doc["user_id"],
            messages=doc.get("messages", []),
            severity_score=doc.get("severity_score")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HISTORY] Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve chat history.")


@router.delete("/chat/{session_id}")
async def delete_session(session_id: str):
    """Delete a session's history and its LangGraph checkpoints."""
    try:
        db = get_database_client()[settings.DB_NAME]
        
        # 1. Delete user-facing chat logs
        history_result = await db["chat_history"].delete_one({"session_id": session_id})
        
        # 2. Delete LangGraph checkpoints and write history
        checkpoints_result = await db["checkpoints"].delete_many({"thread_id": session_id})
        writes_result = await db["checkpoint_writes"].delete_many({"thread_id": session_id})
        
        logger.info(
            f"[HISTORY] Deleted session {session_id}. "
            f"Logs: {history_result.deleted_count}, "
            f"Checkpoints: {checkpoints_result.deleted_count}, "
            f"Writes: {writes_result.deleted_count}"
        )
        
        if history_result.deleted_count == 0 and checkpoints_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found.")
            
        return {"status": "success", "message": "Session deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HISTORY] Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not delete session data.")
