from typing import List
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from backend.app.core.database import get_db
from backend.app.schemas.chart import GeneratedChartSchema

router = APIRouter()

@router.get("/charts/{id}", response_model=List[GeneratedChartSchema])
def get_charts_for_dataset(id: int):
    """
    Retrieves chart metadata list for dataset ID or analysis ID.
    """
    db = get_db()
    charts = list(db["generated_charts"].find({"dataset_id": id}))
    if not charts:
        charts = list(db["generated_charts"].find({"analysis_id": id}))
    return charts

@router.get("/charts/{id}/file")
def get_chart_image_file(id: int):
    """
    Serves the binary PNG chart image file for a given chart ID.
    """
    db = get_db()
    chart = db["generated_charts"].find_one({"id": id})
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart with ID {id} not found."
        )

    file_path = Path(chart["storage_path"])
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart file not found on server disk."
        )

    return FileResponse(path=file_path, media_type="image/png")
