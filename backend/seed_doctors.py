import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, doctor_collection, close_mongo_connection
from app.utils.sample_doctor import SAMPLE_DOCTORS

async def seed():
    print("[INFO] Starting database seed for Anovaidya Doctors...")
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        
        col = doctor_collection()
        
        # Clear existing doctors
        print("[INFO] Clearing existing doctors collection...")
        delete_result = await col.delete_many({})
        print(f"[INFO] Deleted {delete_result.deleted_count} old doctor records.")
        
        # Format and add timestamps
        doctors_to_insert = []
        for doc in SAMPLE_DOCTORS:
            seeded_doc = doc.copy()
            seeded_doc["created_at"] = datetime.utcnow()
            seeded_doc["updated_at"] = datetime.utcnow()
            doctors_to_insert.append(seeded_doc)
            
        # Insert new doctors
        print(f"[INFO] Inserting {len(doctors_to_insert)} fresh doctor profiles...")
        result = await col.insert_many(doctors_to_insert)
        print(f"[SUCCESS] Seeding completed! Inserted {len(result.inserted_ids)} doctors successfully.")
        
    except Exception as e:
        print(f"[ERROR] Seeding failed with error: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed())
