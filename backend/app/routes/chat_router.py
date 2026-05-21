from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.graph import trauma_graph
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "test-user"
    session_id: Optional[str] = "test-session"

class ChatResponse(BaseModel):
    response: str
    severity_score: Optional[int] = None

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare input
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "session_id": request.session_id,
            "report_sent": False
        }
        
        # Run graph
        config = {"configurable": {"thread_id": request.session_id}}
        result = trauma_graph.invoke(input_state, config)
        
        last_message = result["messages"][-1].content if result["messages"] else "No response"
        
        return ChatResponse(
            response=last_message,
            severity_score=result.get("severity_score")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        