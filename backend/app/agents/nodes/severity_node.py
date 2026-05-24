from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from langchain_core.messages import SystemMessage, AIMessage
from app.utils.prompts import SEVERITY_SYSTEM_PROMPT

def severity_node(state: TraumaGraphState):
    """Hybrid Severity Assessment Node"""
    
    messages = state["messages"]
    conversation_history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])  # Last 10 messages
    
    # Build prompt
    full_prompt = [
        SystemMessage(content=SEVERITY_SYSTEM_PROMPT),
        SystemMessage(content=f"Conversation History:\n{conversation_history}"),
        SystemMessage(content="Analyze the above conversation and return JSON only.")
    ]
    
    try:
        # Use strong model for better reasoning
        response_text = llm_client.call(
            messages=[{"role": "user", "content": msg.content} for msg in full_prompt],
            model="strong",          # Using Llama 3.3 70B
            temperature=0.3
        )
        
        # Parse JSON response
        import json
        result = json.loads(response_text.strip())
        
        severity_score = int(result.get("severity_score", 2))
        needs_doctor = result.get("needs_doctor", False)
        
    except Exception as e:
        print(f"Severity LLM Error: {e}")
        # Fallback: Simple rule-based logic
        severity_score = 2
        needs_doctor = False
        result = {"severity_score": 2, "reason": "Fallback due to parsing error", "needs_doctor": False}

    print(f"⚠️ Severity Detected: {severity_score}/5 | Needs Doctor: {needs_doctor}")

    # Return updated state
    return {
        **state,
        "severity_score": severity_score,
        "severity_reason": result.get("reason", ""),
        "needs_doctor": needs_doctor,
        "messages": messages + [AIMessage(content=f"[Severity Assessment: {severity_score}/5]")]
    }

