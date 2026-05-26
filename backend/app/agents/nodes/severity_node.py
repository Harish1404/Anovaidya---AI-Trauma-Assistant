from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import SEVERITY_SYSTEM_PROMPT
from langchain_core.messages import AIMessage
import json
import re

def severity_node(state: TraumaGraphState):
    """Assess severity and identify the needed medical specialization."""
    
    messages = state["messages"]
    conversation_history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])
    
    prompt = [
        {"role": "system", "content": SEVERITY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Conversation History:\n{conversation_history}\n\nAnalyze the above conversation and return JSON only."}
    ]
    
    try:
        # Use strong model for accurate clinical reasoning
        response_text = llm_client.call(
            messages=prompt,
            model="strong",
            temperature=0.2
        )
        
        # Clean and parse JSON
        cleaned = re.sub(r'```json|```', '', response_text).strip()
        result = json.loads(cleaned)
        
        severity_score = int(result.get("severity_score", 2))
        needs_doctor = result.get("needs_doctor", False)
        specialization_needed = result.get("specialization_needed", "General Physician")
        
    except Exception as e:
        print(f"[SEVERITY] LLM Parse Error: {e}")
        severity_score = 2
        needs_doctor = False
        specialization_needed = "General Physician"
        result = {
            "severity_score": 2,
            "reason": "Fallback due to parsing error",
            "needs_doctor": False,
            "specialization_needed": "General Physician"
        }

    print(f"[SEVERITY] Score: {severity_score}/5 | Needs Doctor: {needs_doctor} | Specialization: {specialization_needed}")

    return {
        **state,
        "severity_score": severity_score,
        "severity_reason": result.get("reason", ""),
        "needs_doctor": needs_doctor,
        "specialization_needed": specialization_needed,
        "messages": messages + [AIMessage(content=f"[Severity Assessment: {severity_score}/5 | Specialization: {specialization_needed}]")]
    }
