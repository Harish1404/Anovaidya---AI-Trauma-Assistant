import json
import logging
import re
from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import SUPERVISOR_PROMPT
from langchain_core.messages import AIMessage

logger = logging.getLogger("uvicorn")

def supervisor_node(state: TraumaGraphState):
    """Intelligent supervisor that routes the conversation based on severity and user intent."""
    
    messages = state["messages"]
    severity = state.get("severity_score", 2)
    needs_doctor = state.get("needs_doctor", False)
    has_location = state.get("latitude") is not None
    specialization = state.get("specialization_needed", "General Physician")
    
    conversation_summary = "\n".join([f"{m.type}: {m.content}" for m in messages[-8:]])
    
    # Provide current state context to the LLM
    state_context = f"""
Severity Score: {severity}/5
Needs Doctor (clinical judgment): {"Yes" if needs_doctor else "No"}
Recommended Specialization: {specialization}
User Location Known: {"Yes" if has_location else "No"}
"""

    prompt = [
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user", "content": f"{state_context}\nRecent Conversation:\n{conversation_summary}"}
    ]
    
    try:
        response_text = llm_client.call(
            messages=prompt,
            model="strong",
            temperature=0.3
        )
        
        cleaned = re.sub(r'```json|```', '', response_text).strip()
        decision = json.loads(cleaned)
        
        next_action = decision.get("next") or decision.get("next_action") or "continue_conversation"
        user_message = decision.get("user_message") or decision.get("message") or "I'm here to help. Can you tell me more?"
        
    except Exception as e:
        logger.error(f"[SUPERVISOR] Parse Error: {e}")
        
        # Smart fallback based on severity and clinical judgment
        if (severity >= 4 or (needs_doctor and severity >= 3)) and not has_location:
            next_action = "escalate_to_doctor"
            user_message = (
                "Based on what you've described, I strongly recommend seeking medical attention as soon as possible. "
                "Could you tell me your current location so I can find specialized doctors nearby? "
                "For example: Royapuram, Chennai Tamilnadu"
            )
        elif severity >= 3 and not has_location:
            next_action = "ask_location"
            user_message = (
                "I think it would be wise to consult a specialist for this. "
                "Could you share your current location so I can find nearby doctors for you? "
                "For example: Adyar, Chennai Tamilnadu"
            )
        else:
            next_action = "continue_conversation"
            user_message = "Thank you for sharing. Can you tell me more about your symptoms?"
    
    # Override: if location is already known and action is ask_location, switch to show_doctors
    if next_action in ("ask_location", "escalate_to_doctor") and has_location:
        next_action = "show_doctors"
    
    logger.info(f"[SUPERVISOR] Decision: {next_action} | Severity: {severity}")
    
    return {
        **state,
        "next_action": next_action,
        "messages": messages + [AIMessage(content=user_message)]
    }