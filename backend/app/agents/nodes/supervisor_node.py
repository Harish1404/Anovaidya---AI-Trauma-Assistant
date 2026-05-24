from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from langchain_core.messages import AIMessage
import json
import re

SUPERVISOR_PROMPT = """
You are the Supervisor of TraumaAI.

Based on severity and conversation, decide next step.

Return **only valid JSON** in this exact format:

{
  "next": "continue_conversation" or "escalate_to_doctor",
  "user_message": "A calm, empathetic, and natural message to show the user"
}

Do not add any extra text, explanation, or markdown.
"""

def supervisor_node(state: TraumaGraphState):
    """Improved Supervisor with better JSON parsing"""
    
    severity = state.get("severity_score", 2)
    messages = state.get("messages", [])
    
    # Create conversation summary
    conversation_summary = "\n".join([f"{m.type}: {m.content[:300]}" for m in messages[-8:]])
    
    prompt_messages = [
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user", "content": f"Severity Score: {severity}/5\n\nRecent Conversation:\n{conversation_summary}"}
    ]
    
    try:
        response_text = llm_client.call(
            messages=prompt_messages,
            model="strong",
            temperature=0.3
        )
        
        # Clean and extract JSON
        cleaned = re.sub(r'```json|```', '', response_text).strip()
        
        # Try to parse JSON
        decision = json.loads(cleaned)
        
        next_action = decision.get("next", "continue_conversation")
        user_message = decision.get("user_message", "I'm here to help. Can you tell me more?")
        
    except Exception as e:
        print(f"⚠️ Supervisor JSON Parse Error: {e}")
        print(f"Raw LLM Output: {response_text[:300]}...")
        
        # Smart fallback based on severity
        if severity >= 4:
            next_action = "escalate_to_doctor"
            user_message = "This sounds serious. I recommend consulting a doctor soon. Would you like me to help find nearby doctors?"
        else:
            next_action = "continue_conversation"
            user_message = "Thank you for sharing. Can you tell me more about your symptoms or how it happened?"

    print(f"🤖 Supervisor → Next: {next_action} | Severity: {severity}")

    return {
        **state,
        "messages": messages + [AIMessage(content=user_message)],
        "next_action": next_action
    }