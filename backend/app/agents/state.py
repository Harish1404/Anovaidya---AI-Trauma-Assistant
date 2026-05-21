from typing import TypedDict, Annotated, List
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class TraumaGraphState(TypedDict):
    """Main state for our TraumaAI LangGraph"""
    
    messages: Annotated[List[BaseMessage], add_messages]  # Chat history
    
    user_id: str | None
    session_id: str | None
    
    severity_score: int | None          # 1 to 5
    severity_reason: str | None
    
    needs_doctor: bool | None
    doctor_recommendation: dict | None
    
    report_sent: bool
    final_summary: str | None

    