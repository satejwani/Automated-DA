from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_datasets: int
    total_analyses: int
    total_reports: int
    total_charts: int
