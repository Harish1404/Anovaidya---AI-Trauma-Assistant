from app.agents.state import TraumaGraphState
from app.repo.doctor_repo import doctor_repo
from langchain_core.messages import AIMessage

async def doctor_finder_node(state: TraumaGraphState):
    """Find specialized doctors near the user's geocoded location."""
    
    user_lat = state.get("latitude", 13.0827)  # Default: Chennai center
    user_lon = state.get("longitude", 80.2707)
    specialization = state.get("specialization_needed")
    severity = state.get("severity_score", 3)
    location_str = state.get("user_location_string", "your area")
    
    message_parts = []
    registered_doctors = []
    
    try:
        # Query doctors with specialization and 4km radius, min 5, max 10
        registered_doctors = await doctor_repo.get_nearby_specialized_doctors(
            user_lat=user_lat,
            user_lon=user_lon,
            specialization=specialization,
            radius_km=4.0,
            min_doctors=5,
            max_doctors=10
        )
        
        if registered_doctors:
            spec_label = f" specializing in **{specialization}**" if specialization else ""
            message_parts.append(
                f"I found {len(registered_doctors)} doctors{spec_label} near **{location_str}**. "
                f"Here are the best options for you:\n"
            )
            
            for i, doc in enumerate(registered_doctors, 1):
                availability = "Available Now" if doc.get("is_available") else "Currently Unavailable"
                distance = doc.get("distance_km", "N/A")
                
                message_parts.append(
                    f"**{i}. {doc['full_name']}** — {doc['hospital_name']}\n"
                    f"   Specialization: {doc['specialization']} | Experience: {doc.get('experience_years', 'N/A')} years\n"
                    f"   Location: {doc['clinic_address']} ({distance} km away)\n"
                    f"   Status: {availability}\n"
                )
            
            message_parts.append(
                "\nPlease tell me which doctor you'd like to choose "
                "(e.g., *\"I want to select Dr. Priya Sharma\"*)."
            )
        else:
            message_parts.append(
                "I wasn't able to find registered doctors in your area right now. "
                "Please visit the nearest hospital or call emergency services."
            )
            
    except Exception as e:
        print(f"[DOCTOR_FINDER] Error: {e}")
        message_parts.append(
            "I encountered an issue while searching for doctors. "
            "Please try again or visit the nearest hospital."
        )

    final_message = "\n".join(message_parts)
    
    return {
        **state,
        "doctor_recommendation": registered_doctors,
        "next_action": "select_doctor",
        "messages": state.get("messages", []) + [AIMessage(content=final_message)]
    }