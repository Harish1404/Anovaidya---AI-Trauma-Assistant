from langchain_core.messages import AIMessage, HumanMessage

from app.agents.constants import SELECT_DOCTOR
from app.agents.state import TraumaGraphState
from app.utils.parsers import extract_doctor_name

DOCTOR_RETRY_MESSAGE = (
    "I couldn't identify which doctor you'd like to select. "
    "Could you please mention the doctor's name from the list above?"
)


def _last_human_content(messages) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return messages[-1].content if messages else ""


def doctor_select_node(state: TraumaGraphState):
    """Parse doctor selection from the user's message."""
    messages = state.get("messages", [])
    doctors = state.get("doctor_recommendation", []) or []
    selected_name = extract_doctor_name(_last_human_content(messages), doctors)

    if selected_name:
        return {
            **state,
            "selected_doctor_name": selected_name,
        }

    return {
        **state,
        "next_action": SELECT_DOCTOR,
        "messages": messages + [AIMessage(content=DOCTOR_RETRY_MESSAGE)],
    }
