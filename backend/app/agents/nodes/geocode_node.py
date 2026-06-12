import logging

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.constants import ASK_LOCATION, SHOW_DOCTORS
from app.agents.state import TraumaGraphState
from app.utils.geocoding import geocode_address

logger = logging.getLogger("uvicorn")

GEOCODE_RETRY_MESSAGE = (
    "I couldn't find that location. Could you please try again with a more specific address? "
    "For example: **Royapuram, Chennai Tamilnadu** or **Adyar, Chennai**."
)


def _last_human_content(messages) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return messages[-1].content if messages else ""


def geocode_node(state: TraumaGraphState):
    """Geocode the user's location message and update state for doctor search."""
    messages = state.get("messages", [])
    address = _last_human_content(messages)

    geo_result = geocode_address(address)

    if geo_result:
        logger.info(f"[GEOCODE] Geocoded '{address}' -> {geo_result}")
        return {
            **state,
            "user_location_string": geo_result.get("formatted_address", address),
            "latitude": geo_result["latitude"],
            "longitude": geo_result["longitude"],
            "next_action": SHOW_DOCTORS,
        }

    return {
        **state,
        "next_action": ASK_LOCATION,
        "messages": messages + [AIMessage(content=GEOCODE_RETRY_MESSAGE)],
    }
