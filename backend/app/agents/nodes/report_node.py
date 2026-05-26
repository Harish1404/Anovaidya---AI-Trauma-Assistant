from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import REPORT_PROMPT
from langchain_core.messages import AIMessage

def report_node(state: TraumaGraphState):
    """Generate a clinical-grade trauma report for the selected doctor."""
    
    messages = state["messages"]
    conversation = "\n".join([f"{m.type}: {m.content}" for m in messages[-12:]])
    severity = state.get("severity_score", 3)
    specialization = state.get("specialization_needed", "General Physician")
    selected_doctor = state.get("selected_doctor_name", "the doctor")
    
    prompt = [
        {"role": "system", "content": REPORT_PROMPT},
        {"role": "user", "content": f"""
Severity: {severity}/5
Recommended Specialization: {specialization}
Selected Doctor: {selected_doctor}

Full Conversation:
{conversation}
"""}
    ]
    
    try:
        # Use strong model for high-quality clinical report
        report_text = llm_client.call(
            messages=prompt,
            model="strong",
            temperature=0.3
        )
    except Exception as e:
        print(f"[REPORT] Generation Error: {e}")
        report_text = f"Report generation failed. Severity: {severity}/5. Please consult a {specialization}."

    return {
        **state,
        "final_summary": report_text,
        "next_action": "ask_email",
        "messages": messages + [AIMessage(content=(
            f"I have prepared a detailed clinical report for **{selected_doctor}**.\n\n"
            "Would you like me to email this report to you and the doctor? "
            "If yes, please share your email address."
        ))]
    }
