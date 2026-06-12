import logging
from app.agents.state import TraumaGraphState
from app.utils.google_maps import find_nearby_medical_facilities
from langchain_core.messages import AIMessage

logger = logging.getLogger("uvicorn")


async def doctor_finder_node(state: TraumaGraphState):
    """Find nearby hospitals, clinics, and specialists using Google Maps Places API."""

    user_lat = state.get("latitude")
    user_lon = state.get("longitude")
    specialization = state.get("specialization_needed")
    location_str = state.get("user_location_string", "your area")

    # Fail explicitly if location is not available
    if user_lat is None or user_lon is None:
        return {
            **state,
            "next_action": "ask_location",
            "messages": state.get("messages", []) + [AIMessage(content=(
                "I need your location to find nearby doctors. "
                "Could you please share your current location? "
                "For example: **Adyar, Chennai Tamilnadu**"
            ))]
        }

    message_parts = []
    facilities = []

    try:
        facilities = await find_nearby_medical_facilities(
            lat=user_lat,
            lng=user_lon,
            specialization=specialization,
            min_results=3,
            max_results=10,
        )

        if facilities:
            spec_label = f" specializing in **{specialization}**" if specialization else ""
            message_parts.append(
                f"I found {len(facilities)} hospitals & clinics{spec_label} near **{location_str}**. "
                f"Here are the best options for you:\n"
            )

            for i, fac in enumerate(facilities, 1):
                availability = "Open Now" if fac.get("is_available") else "Hours N/A"
                distance = fac.get("distance_km", "N/A")
                rating = fac.get("rating")
                rating_str = f" | ⭐ {rating}/5" if rating else ""

                message_parts.append(
                    f"**{i}. {fac['full_name']}**\n"
                    f"   Specialization: {fac['specialization']}{rating_str}\n"
                    f"   Location: {fac['clinic_address']} ({distance} km away)\n"
                    f"   Status: {availability}\n"
                )

            message_parts.append(
                "\nPlease tell me which hospital or clinic you'd like to choose "
                "(e.g., *\"I want to select Apollo Hospitals\"*)."
            )
        else:
            message_parts.append(
                "I wasn't able to find hospitals or clinics near your location right now. "
                "Please visit the nearest hospital or call emergency services."
            )

    except Exception as e:
        logger.error(f"[DOCTOR_FINDER] Error: {e}")
        message_parts.append(
            "I encountered an issue while searching for nearby facilities. "
            "Please try again or visit the nearest hospital."
        )

    final_message = "\n".join(message_parts)

    return {
        **state,
        "doctor_recommendation": facilities,
        "next_action": "select_doctor",
        "messages": state.get("messages", []) + [AIMessage(content=final_message)]
    }