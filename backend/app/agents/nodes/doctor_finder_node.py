from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from langchain_core.messages import AIMessage
from app.core.config import settings
import httpx
import json

def doctor_finder_node(state: TraumaGraphState):
    """Find nearby doctors/hospitals using Google Maps"""
    
    user_location = "Chennai, Tamil Nadu"  # Default for now (we'll improve later)
    severity = state.get("severity_score", 4)
    
    try:
        # Google Places API call
        api_key = settings.GOOGLE_MAPS_API_KEY
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        params = {
            "query": "hospital OR clinic OR emergency near " + user_location,
            "key": api_key
        }
        
        with httpx.Client() as client:
            response = client.get(url, params=params)
            data = response.json()
        
        if data.get("results"):
            top_places = data["results"][:3]
            doctors = []
            for place in top_places:
                doctors.append({
                    "name": place["name"],
                    "address": place.get("formatted_address", ""),
                    "rating": place.get("rating"),
                    "location": place["geometry"]["location"]
                })
        else:
            doctors = []
            
    except Exception as e:
        print(f"Doctor Finder Error: {e}")
        doctors = []

    message = "Here are some nearby medical facilities I found:"
    if doctors:
        for i, d in enumerate(doctors, 1):
            message += f"\n\n{i}. **{d['name']}**\n   {d['address']}"
    else:
        message += "\n\nI couldn't find specific doctors right now. Please search for 'hospital near me' on Google Maps."

    return {
        **state,
        "doctor_recommendation": doctors,
        "messages": state["messages"] + [AIMessage(content=message)]
    }


    