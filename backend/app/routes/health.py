from fastapi import APIRouter

router = APIRouter()

@router.get("/api/health", tags=["Health"], summary="Health check")
async def health_check():
    return {
        "status": "healthy",
        "message": "ML Auto-Pipeline API is running"
    }