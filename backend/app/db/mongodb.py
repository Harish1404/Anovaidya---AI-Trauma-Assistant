from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

# Setup Logger (Critical for Cloud Debugging)
logger = logging.getLogger("uvicorn")

db_name = settings.DB_NAME

class Database:
    client: AsyncIOMotorClient = None

db_instance = Database()

def get_database_client():
    return db_instance.client

def doctor_collection():
    return db_instance.client[db_name]["doctors"]

async def connect_to_mongo():
    try:
        logger.info("[DATABASE] Connecting to MongoDB...")
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # THE PING TEST (Crucial for Cloud)
        await db_instance.client.admin.command('ping')
        logger.info("[DATABASE] MongoDB Connected Successfully!")
            
    except Exception as e:
        logger.error(f"[DATABASE] MongoDB Connection Failed: {e}")
        raise e


async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("[DATABASE] MongoDB connection closed.")


