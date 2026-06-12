import logging
from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import REPORT_PROMPT
from app.utils.docx_generator import generate_clinical_report_docx
from langchain_core.messages import AIMessage

logger = logging.getLogger("uvicorn")

def report_node(state: TraumaGraphState):
    """Generate a clinical-grade trauma report and export it as a Word document."""
    
    messages = state["messages"]
    conversation = "\n".join([f"{m.type}: {m.content}" for m in messages[-12:]])
    severity = state.get("severity_score", 3)
    specialization = state.get("specialization_needed", "General Physician")
    selected_doctor = state.get("selected_doctor_name", "the doctor")
    user_id = state.get("user_id", "unknown")
    session_id = state.get("session_id", "unknown")
    
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
        # Use Gemini 3.5 Flash for high-quality, detailed clinical report
        report_text = llm_client.call(
            messages=prompt,
            model="gemini",
            temperature=0.3
        )
    except Exception as e:
        logger.error(f"[REPORT] Generation Error: {e}")
        report_text = f"Report generation failed. Severity: {severity}/5. Please consult a {specialization}."

    # Generate Word document
    docx_path = generate_clinical_report_docx(
        report_content=report_text,
        user_id=user_id,
        session_id=session_id,
        doctor_name=selected_doctor,
        severity_score=severity,
        specialization=specialization,
    )

    if docx_path:
        logger.info(f"[REPORT] Word document generated: {docx_path}")

    # Build the download URL (relative — the router will serve it)
    download_url = f"/api/reports/{session_id}/download" if docx_path else None

    response_msg = (
        f"I have prepared a detailed clinical report for **{selected_doctor}**.\n\n"
    )
    if download_url:
        response_msg += "📄 You can **download the report** as a Word document from the link below.\n\n"
    response_msg += (
        "Would you like me to email this report to you and the doctor? "
        "If yes, please share your email address."
    )

    return {
        **state,
        "final_summary": report_text,
        "report_docx_path": docx_path,
        "report_download_url": download_url,
        "next_action": "ask_email",
        "messages": messages + [AIMessage(content=response_msg)]
    }
