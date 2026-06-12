from datetime import datetime
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.agents.graph import trauma_graph
from app.core.config import settings
from app.db.mongodb import get_database_client
from app.utils.chat_response import state_to_chat_response

logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: str = "test-user"
    session_id: str = "test-session"


class ChatResponse(BaseModel):
    response: str
    severity_score: Optional[int] = None
    doctors_recommended: List[Dict] = []
    report_ready: bool = False
    report_download_url: Optional[str] = None
    next_action: str = "continue"


@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.session_id}}
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "session_id": request.session_id,
        }
        result = await trauma_graph.ainvoke(input_state, config)

        # Save human-readable chat logs to MongoDB
        db_messages = []
        for msg in result.get("messages", []):
            if msg.content and msg.content.startswith("["):
                continue
            role = "user" if msg.type == "human" else "assistant"
            db_messages.append({
                "role": role,
                "content": msg.content,
            })

        db = get_database_client()[settings.DB_NAME]
        chat_history_col = db["chat_history"]

        await chat_history_col.update_one(
            {"session_id": request.session_id},
            {
                "$set": {
                    "user_id": request.user_id,
                    "messages": db_messages,
                    "severity_score": result.get("severity_score"),
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

        return state_to_chat_response(result, ChatResponse)
    except Exception as e:
        logger.error(f"[ROUTER] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

