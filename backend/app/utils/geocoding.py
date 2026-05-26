from app.core.config import settings
import googlemaps
from fastapi import HTTPException

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

def geocode_address(address: str):
    """Convert address to lat/long"""
    try:
        result = gmaps.geocode(address)
        if result:
            location = result[0]['geometry']['location']
            return {
                "latitude": location['lat'],
                "longitude": location['lng'],
                "formatted_address": result[0].get('formatted_address')
            }
        return None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None