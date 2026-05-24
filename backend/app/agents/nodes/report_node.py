from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import REPORT_PROMPT
from langchain_core.messages import AIMessage


def report_node(state: TraumaGraphState):
    """Generate structured report"""
    
    messages = state["messages"]
    conversation = "\n".join([f"{m.type}: {m.content}" for m in messages[-12:]])
    severity = state.get("severity_score", 4)
    
    prompt = [
        {"role": "system", "content": REPORT_PROMPT},
        {"role": "user", "content": f"""
Severity: {severity}/5

Full Conversation:
{conversation}
"""}
    ]
    
    try:
        report_text = llm_client.call(
            messages=prompt,
            model="strong",
            temperature=0.3
        )
    except:
        report_text = "Report generation failed."

    return {
        **state,
        "final_summary": report_text,
        "messages": messages + [AIMessage(content="✅ I have prepared a summary report that can be sent to a doctor.")]
    }

