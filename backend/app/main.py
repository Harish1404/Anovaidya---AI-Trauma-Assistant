from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import chat_router, history_router
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
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(history_router.router)


@app.get("/api/reports/{session_id}/download")
async def download_report(session_id: str):
    """Serve a generated Word document report for download."""
    import re
    from pathlib import Path
    from fastapi import HTTPException

    safe_session = re.sub(r"[^a-zA-Z0-9_-]", "_", session_id)
    filepath = Path(__file__).resolve().parent.parent / "uploads" / "reports" / f"trauma_report_{safe_session}.docx"

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=str(filepath),
        filename=f"TraumaAI_Report_{safe_session}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

