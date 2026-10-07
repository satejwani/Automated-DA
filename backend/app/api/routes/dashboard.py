from fastapi import APIRouter
from backend.app.core.database import get_db
from backend.app.schemas.dashboard import DashboardStatsResponse

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats():
    """
    Returns platform summary counters for Dashboard cards.
    """
    db = get_db()
    
    total_datasets = len(list(db["datasets"].find()))
    total_analyses = len(list(db["analysis_results"].find()))
    total_reports = len(list(db["reports"].find()))
    total_charts = len(list(db["generated_charts"].find()))

    return DashboardStatsResponse(
        total_datasets=total_datasets,
        total_analyses=total_analyses,
        total_reports=total_reports,
        total_charts=total_charts
    )
