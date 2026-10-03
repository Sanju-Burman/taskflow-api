from fastapi import APIRouter, status
from sqlalchemy import text
from app.api.deps import SessionDep
from app.core.config import settings

router = APIRouter(tags=["Health & System"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
async def health_check(db: SessionDep):
    """Check API and database health status."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
