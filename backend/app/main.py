from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import chat_router
from contextlib import asynccontextmanager
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import logging

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    await connect_to_mongo()
    yield
    logger.info("App shutdown")
    await close_mongo_connection()


app = FastAPI(
    title="TraumaAI - Medical Trauma Assistant",
    description="Multi-Agent AI Trauma System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "TraumaAI Backend is Running",
        "status": "healthy",
        "env": settings.ENV
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(chat_router.router)

