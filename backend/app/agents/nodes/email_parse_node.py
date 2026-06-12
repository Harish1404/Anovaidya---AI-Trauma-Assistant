from langchain_core.messages import AIMessage, HumanMessage

from app.agents.constants import ASK_EMAIL, COMPLETE
from app.agents.state import TraumaGraphState
from app.utils.parsers import extract_email, is_email_skip_message

EMAIL_RETRY_MESSAGE = (
    "Could you please share a valid email address? For example: **yourname@gmail.com**"
)

SKIP_MESSAGE = (
    "No problem! You can still visit the selected doctor directly. "
    "Please take the first-aid advice we discussed and seek medical attention soon. Take care!"
)


def _last_human_content(messages) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return messages[-1].content if messages else ""


def email_parse_node(state: TraumaGraphState):
    """Parse email from user message or handle skip."""
    messages = state.get("messages", [])
    text = _last_human_content(messages)

    email = extract_email(text)
    if email:
        return {
            **state,
            "user_email": email,
        }

    if is_email_skip_message(text):
        return {
            **state,
            "next_action": COMPLETE,
            "messages": messages + [AIMessage(content=SKIP_MESSAGE)],
        }

    return {
        **state,
        "next_action": ASK_EMAIL,
        "messages": messages + [AIMessage(content=EMAIL_RETRY_MESSAGE)],
    }
