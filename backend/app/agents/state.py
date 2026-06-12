from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

from app.agents.constants import CONTINUE

class TraumaGraphState(TypedDict):
    """Main state for TraumaAI LangGraph"""
    messages: Annotated[List[BaseMessage], add_messages]
    
    user_id: str | None
    session_id: str | None
    
    # Severity assessment
    severity_score: Optional[int] = None
    severity_reason: Optional[str] = None
    needs_doctor: Optional[bool] = None
    specialization_needed: Optional[str] = None
    
    # Routing control
    next_action: Optional[str] = CONTINUE
    # Values: continue_conversation / ask_location / show_doctors / select_doctor / ask_email / complete
    
    # Location tracking
    user_location_string: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Doctor results
    doctor_recommendation: Optional[list] = None
    selected_doctor_name: Optional[str] = None
    
    # Report & email
    final_summary: Optional[str] = None
    report_docx_path: Optional[str] = None
    report_download_url: Optional[str] = None
    report_sent: bool = False
    user_email: Optional[str] = None
    email_sent_success: bool = False
    
    # Turn tracking
    turn_count: int = 0
    should_check_severity: bool = False