from app.agents.state import TraumaGraphState
from app.utils.brevo_email import send_report_via_brevo
from app.repo.doctor_repo import doctor_repo
from langchain_core.messages import AIMessage

async def email_node(state: TraumaGraphState):
    """Send the clinical report via Brevo to the doctor and user."""
    
    messages = state["messages"]
    user_email = state.get("user_email")
    selected_doctor_name = state.get("selected_doctor_name")
    report_content = state.get("final_summary", "Report not available.")
    severity = state.get("severity_score", 3)
    
    if not user_email or not selected_doctor_name:
        return {
            **state,
            "email_sent_success": False,
            "messages": messages + [AIMessage(content="I need both your email and a selected doctor to send the report.")]
        }
    
    # Look up doctor email from DB
    doctor = await doctor_repo.get_doctor_by_name(selected_doctor_name)
    
    if not doctor:
        return {
            **state,
            "email_sent_success": False,
            "messages": messages + [AIMessage(content=f"I couldn't find {selected_doctor_name} in our records. Please select a doctor from the list.")]
        }
    
    doctor_email = doctor.get("email", "")
    doctor_name = doctor.get("full_name", selected_doctor_name)
    
    # Send via Brevo
    success = await send_report_via_brevo(
        doctor_email=doctor_email,
        doctor_name=doctor_name,
        user_email=user_email,
        report_content=report_content,
        severity_score=severity
    )
    
    if success:
        response_msg = (
            f"Your clinical report has been successfully sent to **{doctor_name}** "
            f"({doctor.get('hospital_name', '')}) and a copy has been sent to **{user_email}**.\n\n"
            "Please visit the doctor at your earliest convenience. Take care and stay safe!"
        )
    else:
        response_msg = (
            "I tried sending the report but encountered an issue with the email service. "
            "You can still visit the doctor directly and describe your symptoms. "
            "Please take care!"
        )
    
    return {
        **state,
        "email_sent_success": success,
        "report_sent": success,
        "messages": messages + [AIMessage(content=response_msg)]
    }
