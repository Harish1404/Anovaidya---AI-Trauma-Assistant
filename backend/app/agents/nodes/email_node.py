from app.agents.constants import COMPLETE
from app.agents.state import TraumaGraphState
from app.utils.brevo_email import send_report_via_brevo
from langchain_core.messages import AIMessage

async def email_node(state: TraumaGraphState):
    """Send the clinical report via Brevo to the user (and optionally the doctor)."""
    
    messages = state["messages"]
    user_email = state.get("user_email")
    selected_doctor_name = state.get("selected_doctor_name", "Unknown")
    report_content = state.get("final_summary", "Report not available.")
    severity = state.get("severity_score", 3)
    docx_path = state.get("report_docx_path")
    
    if not user_email:
        return {
            **state,
            "email_sent_success": False,
            "messages": messages + [AIMessage(content="I need your email address to send the report. Please share it.")]
        }
    
    # Since doctors now come from Google Maps (no email in DB),
    # we send the report to the user's email only.
    # The user can then forward it to the doctor directly.
    success = await send_report_via_brevo(
        doctor_email=user_email,  # Send to user (as primary recipient)
        doctor_name=selected_doctor_name,
        user_email=user_email,
        report_content=report_content,
        severity_score=severity,
        docx_path=docx_path,
    )
    
    if success:
        response_msg = (
            f"✅ Your clinical report has been successfully emailed to **{user_email}**.\n\n"
            f"The report is addressed to **{selected_doctor_name}**. "
            "Please print or forward the attached Word document when you visit the hospital.\n\n"
            "Take care and stay safe! 🙏"
        )
    else:
        response_msg = (
            "I tried sending the report but encountered an issue with the email service. "
            "You can still download the report using the link above and visit the doctor directly. "
            "Please take care!"
        )
    
    return {
        **state,
        "email_sent_success": success,
        "report_sent": success,
        "next_action": COMPLETE if success else state.get("next_action"),
        "messages": messages + [AIMessage(content=response_msg)]
    }
