from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.schemas import MonitoringStats
import app.models as models

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/stats", response_model=MonitoringStats)
async def get_stats(db: Session = Depends(get_db)):
    """
    Statistiques d'utilisation et de coûts
    """
    total_papers = db.query(func.count(models.Paper.id)).scalar() or 0
    total_chunks = db.query(func.count(models.Chunk.id)).scalar() or 0
    total_queries = db.query(func.count(models.QueryLog.id)).scalar() or 0

    total_cost = db.query(func.sum(models.QueryLog.cost_usd)).scalar() or 0.0
    avg_response_time = db.query(func.avg(models.QueryLog.response_time_ms)).scalar() or 0.0

    # Requêtes aujourd'hui
    from datetime import datetime, timedelta
    today = datetime.now().date()
    queries_today = db.query(func.count(models.QueryLog.id)).filter(
        func.date(models.QueryLog.created_at) == today
    ).scalar() or 0

    return MonitoringStats(
        total_papers=total_papers,
        total_chunks=total_chunks,
        total_queries=total_queries,
        total_cost_usd=round(total_cost, 2),
        avg_response_time_ms=round(avg_response_time, 0),
        queries_today=queries_today
    )
