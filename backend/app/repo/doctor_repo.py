from typing import List, Dict, Optional
from app.db.mongodb import doctor_collection
from math import radians, cos, sin, asin, sqrt

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of earth in kilometers
    return c * r


class DoctorRepository:
    
    async def get_all_doctors(self) -> List[Dict]:
        """Get all registered doctors from local MongoDB."""
        cursor = doctor_collection().find({})
        doctors = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doctors.append(doc)
        return doctors

    async def get_nearby_specialized_doctors(
        self,
        user_lat: float,
        user_lon: float,
        specialization: Optional[str] = None,
        radius_km: float = 4.0,
        min_doctors: int = 5,
        max_doctors: int = 10
    ) -> List[Dict]:
        """
        Get doctors from MongoDB filtered by specialization and proximity.
        
        Strategy:
        1. First, fetch all doctors matching the specialization within the radius.
        2. If fewer than min_doctors, expand by adding ANY available doctors sorted by distance.
        3. Cap results at max_doctors.
        """
        # Fetch all doctors from the database
        cursor = doctor_collection().find({})
        all_doctors = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            lat = doc.get("latitude")
            lon = doc.get("longitude")
            if lat is not None and lon is not None:
                doc["distance_km"] = round(haversine(user_lon, user_lat, lon, lat), 2)
            else:
                doc["distance_km"] = float('inf')
            all_doctors.append(doc)
        
        # Sort all doctors: available first, then by distance
        all_doctors.sort(key=lambda x: (not x.get("is_available", False), x.get("distance_km", float('inf'))))
        
        # Phase 1: Specialized doctors within radius
        specialized_nearby = []
        other_doctors = []
        
        for doc in all_doctors:
            is_match = (
                specialization is None 
                or doc.get("specialization", "").lower() == specialization.lower()
            )
            is_within_radius = doc.get("distance_km", float('inf')) <= radius_km
            
            if is_match and is_within_radius:
                specialized_nearby.append(doc)
            else:
                other_doctors.append(doc)
        
        # Phase 2: If fewer than min_doctors, fill with remaining doctors sorted by distance
        result = specialized_nearby.copy()
        
        if len(result) < min_doctors:
            # Add specialized doctors outside radius first
            specialized_outside = [
                d for d in other_doctors
                if specialization is None or d.get("specialization", "").lower() == specialization.lower()
            ]
            for doc in specialized_outside:
                if len(result) >= min_doctors:
                    break
                result.append(doc)
        
        if len(result) < min_doctors:
            # Fill with any remaining available doctors by proximity
            non_specialized = [d for d in other_doctors if d not in result]
            for doc in non_specialized:
                if len(result) >= min_doctors:
                    break
                result.append(doc)
        
        return result[:max_doctors]

    async def get_nearby_doctors(self, user_lat: float, user_lon: float, limit: int = 5) -> List[Dict]:
        """Legacy: Get doctors sorted by availability then distance."""
        return await self.get_nearby_specialized_doctors(
            user_lat=user_lat,
            user_lon=user_lon,
            specialization=None,
            radius_km=100.0,
            min_doctors=limit,
            max_doctors=limit
        )

    async def get_doctors_by_specialization(self, specialization: str) -> List[Dict]:
        """Filter doctors from MongoDB by specialization."""
        cursor = doctor_collection().find({"specialization": specialization})
        doctors = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doctors.append(doc)
        return doctors

    async def get_doctor_by_name(self, name: str) -> Optional[Dict]:
        """Find a doctor by full_name (case-insensitive partial match)."""
        cursor = doctor_collection().find({
            "full_name": {"$regex": name, "$options": "i"}
        })
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            return doc
        return None


# Global instance
doctor_repo = DoctorRepository()
