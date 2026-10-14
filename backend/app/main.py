from fastapi import FastAPI
from app.api.v1.router import api_router

from app.core.database import SessionLocal
from app.services.ai.matcher import build_faiss_index

app = FastAPI(
    title="SIH26043 Innovation Decision Platform",
    description="API for the AI-Assisted Societal Innovation Engine",
    version="1.0.0"
)

# Attach the V1 router to the main app
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "message": "API is running"}

@app.on_event("startup")
def startup_event():
    """Triggered automatically when Uvicorn starts the server."""
    db = SessionLocal()
    try:
        build_faiss_index(db)
    finally:
        db.close()