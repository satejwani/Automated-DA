from fastapi import APIRouter
from backend.app.api.routes import upload, datasets, analysis, report, charts, dashboard

api_router = APIRouter()

api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(datasets.router, tags=["Datasets"])
api_router.include_router(analysis.router, tags=["Analysis"])
api_router.include_router(report.router, tags=["Report"])
api_router.include_router(charts.router, tags=["Charts"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
