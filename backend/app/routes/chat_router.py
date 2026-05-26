from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from langchain_core.messages import HumanMessage
from app.agents.graph import trauma_graph
from app.utils.geocoding import geocode_address
from app.repo.doctor_repo import doctor_repo
from app.agents.nodes.report_node import report_node
from app.agents.nodes.email_node import email_node
import re
import logging

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
    next_action: str = "continue"


def extract_email(text: str) -> Optional[str]:
    """Extract an email address from user text."""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None


def extract_doctor_name(text: str, doctors: list) -> Optional[str]:
    """Try to match a doctor name from the user's message against the recommended list."""
    text_lower = text.lower()
    for doc in doctors:
        name = doc.get("full_name", "")
        # Match on last name or full name
        if name.lower() in text_lower:
            return name
        # Try matching just the last name (e.g., "Sharma", "Rajan")
        last_name = name.split()[-1] if name.split() else ""
        if last_name.lower() in text_lower and len(last_name) > 2:
            return name
    return None


@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.session_id}}
        
        # Get existing state from the graph checkpointer
        existing_state = None
        try:
            snapshot = trauma_graph.get_state(config)
            if snapshot and snapshot.values:
                existing_state = snapshot.values
        except Exception:
            existing_state = None
        
        current_next_action = existing_state.get("next_action") if existing_state else None
        
        # ──────────────────────────────────────────────────────
        # PHASE: User is providing their LOCATION
        # ──────────────────────────────────────────────────────
        if current_next_action in ("ask_location", "escalate_to_doctor"):
            geo_result = geocode_address(request.message)
            
            if geo_result:
                logger.info(f"[ROUTER] Geocoded '{request.message}' -> {geo_result}")
                
                # Update state with location and run doctor_finder
                trauma_graph.update_state(config, {
                    "messages": [HumanMessage(content=request.message)],
                    "user_location_string": geo_result.get("formatted_address", request.message),
                    "latitude": geo_result["latitude"],
                    "longitude": geo_result["longitude"],
                    "next_action": "show_doctors"
                })
                
                # Run the graph — it will enter at conversation but we want doctor_finder
                # So we invoke doctor_finder directly via the graph
                from app.agents.nodes.doctor_finder_node import doctor_finder_node
                
                current_state = trauma_graph.get_state(config).values
                finder_result = await doctor_finder_node(current_state)
                
                # Update graph state with the doctor finder results
                trauma_graph.update_state(config, finder_result)
                
                final_state = trauma_graph.get_state(config).values
                messages = final_state.get("messages", [])
                main_response = _extract_last_ai_message(messages)
                
                return ChatResponse(
                    response=main_response,
                    severity_score=final_state.get("severity_score"),
                    doctors_recommended=final_state.get("doctor_recommendation", []),
                    report_ready=False,
                    next_action=final_state.get("next_action", "select_doctor")
                )
            else:
                # Geocoding failed — ask again
                return ChatResponse(
                    response=(
                        "I couldn't find that location. Could you please try again with a more specific address? "
                        "For example: **Royapuram, Chennai Tamilnadu** or **Adyar, Chennai**."
                    ),
                    severity_score=existing_state.get("severity_score") if existing_state else None,
                    next_action="ask_location"
                )
        
        # ──────────────────────────────────────────────────────
        # PHASE: User is SELECTING a doctor
        # ──────────────────────────────────────────────────────
        if current_next_action == "select_doctor":
            doctors = existing_state.get("doctor_recommendation", []) if existing_state else []
            selected_name = extract_doctor_name(request.message, doctors)
            
            if selected_name:
                logger.info(f"[ROUTER] User selected doctor: {selected_name}")
                
                # Update state and run report generation
                trauma_graph.update_state(config, {
                    "messages": [HumanMessage(content=request.message)],
                    "selected_doctor_name": selected_name
                })
                
                current_state = trauma_graph.get_state(config).values
                report_result = report_node(current_state)
                
                trauma_graph.update_state(config, report_result)
                
                final_state = trauma_graph.get_state(config).values
                messages = final_state.get("messages", [])
                main_response = _extract_last_ai_message(messages)
                
                return ChatResponse(
                    response=main_response,
                    severity_score=final_state.get("severity_score"),
                    doctors_recommended=final_state.get("doctor_recommendation", []),
                    report_ready=True,
                    next_action="ask_email"
                )
            else:
                # Couldn't identify the doctor — ask again
                return ChatResponse(
                    response=(
                        "I couldn't identify which doctor you'd like to select. "
                        "Could you please mention the doctor's name from the list above?"
                    ),
                    severity_score=existing_state.get("severity_score") if existing_state else None,
                    doctors_recommended=doctors,
                    next_action="select_doctor"
                )
        
        # ──────────────────────────────────────────────────────
        # PHASE: User is providing their EMAIL
        # ──────────────────────────────────────────────────────
        if current_next_action == "ask_email":
            email = extract_email(request.message)
            
            if email:
                logger.info(f"[ROUTER] User provided email: {email}")
                
                trauma_graph.update_state(config, {
                    "messages": [HumanMessage(content=request.message)],
                    "user_email": email
                })
                
                current_state = trauma_graph.get_state(config).values
                email_result = await email_node(current_state)
                
                trauma_graph.update_state(config, email_result)
                
                final_state = trauma_graph.get_state(config).values
                messages = final_state.get("messages", [])
                main_response = _extract_last_ai_message(messages)
                
                return ChatResponse(
                    response=main_response,
                    severity_score=final_state.get("severity_score"),
                    report_ready=True,
                    next_action="complete"
                )
            else:
                # Check if user said "no" or wants to skip
                skip_keywords = ["no", "skip", "later", "not now", "nope", "don't"]
                if any(kw in request.message.lower() for kw in skip_keywords):
                    return ChatResponse(
                        response=(
                            "No problem! You can still visit the selected doctor directly. "
                            "Please take the first-aid advice we discussed and seek medical attention soon. Take care!"
                        ),
                        severity_score=existing_state.get("severity_score") if existing_state else None,
                        report_ready=True,
                        next_action="complete"
                    )
                
                return ChatResponse(
                    response="Could you please share a valid email address? For example: **yourname@gmail.com**",
                    severity_score=existing_state.get("severity_score") if existing_state else None,
                    report_ready=True,
                    next_action="ask_email"
                )
        
        # ──────────────────────────────────────────────────────
        # DEFAULT: Normal conversation flow through the graph
        # ──────────────────────────────────────────────────────
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "session_id": request.session_id,
            "report_sent": False
        }
        
        result = trauma_graph.invoke(input_state, config)
        
        messages = result.get("messages", [])
        main_response = _extract_last_ai_message(messages)
        
        return ChatResponse(
            response=main_response,
            severity_score=result.get("severity_score"),
            doctors_recommended=result.get("doctor_recommendation") or [],
            report_ready=bool(result.get("final_summary")),
            next_action=result.get("next_action", "continue")
        )
        
    except Exception as e:
        logger.error(f"[ROUTER] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _extract_last_ai_message(messages) -> str:
    """Extract the last meaningful AI message (skip internal severity tags)."""
    for msg in reversed(messages):
        content = msg.content
        if content and not content.startswith("["):
            return content
    return "I'm here to help. Could you tell me what happened?"