from fastapi import APIRouter
from app.api.v1.endpoints import submissions

api_router = APIRouter()

# Include the submissions router under the /submissions prefix
api_router.include_router(
    submissions.router,
    prefix="/submissions",
    tags=["Submissions"]
)