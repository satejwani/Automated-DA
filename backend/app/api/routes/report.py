from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from backend.app.core.database import get_db, get_next_sequence_value
from backend.app.schemas.report import ReportSchema
from backend.app.services.report_service import ReportService

router = APIRouter()

@router.post("/report/{id}", response_model=ReportSchema, status_code=status.HTTP_201_CREATED)
def generate_report_for_dataset(id: int):
    """
    Generates a downloadable ReportLab PDF report for dataset ID and records in MongoDB.
    """
    db = get_db()
    dataset = db["datasets"].find_one({"id": id})
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {id} not found."
        )

    # Check for existing analysis result
    cursor = db["analysis_results"].find({"dataset_id": dataset["id"]}).sort("analysis_timestamp", -1).limit(1)
    results = list(cursor)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset {id} must be analyzed before generating a report. Run POST /api/analyze/{id} first."
        )

    analysis = results[0]

    # Fetch charts
    charts_cursor = db["generated_charts"].find({"analysis_id": analysis["id"]})
    chart_paths = [c["storage_path"] for c in charts_cursor]

    dataset_info = {
        "id": dataset["id"],
        "filename": dataset["filename"],
        "original_filename": dataset["original_filename"],
        "file_type": dataset["file_type"],
        "file_size_bytes": dataset["file_size_bytes"],
        "row_count": dataset["row_count"],
        "column_count": dataset["column_count"],
        "upload_timestamp": str(dataset["upload_timestamp"])
    }

    try:
        pdf_meta = ReportService.generate_pdf_report(
            dataset_info=dataset_info,
            quality_info=analysis.get("data_quality_json", {}),
            analysis_info={
                "numerical_analysis": analysis.get("numerical_stats_json", {}),
                "categorical_analysis": analysis.get("categorical_stats_json", {}),
                "correlation_analysis": analysis.get("correlation_matrix_json", {})
            },
            chart_paths=chart_paths
        )

        report_id = get_next_sequence_value("report_id")
        report_doc = {
            "id": report_id,
            "dataset_id": dataset["id"],
            "analysis_id": analysis["id"],
            "report_title": pdf_meta["report_title"],
            "storage_path": pdf_meta["storage_path"],
            "file_size_bytes": pdf_meta["file_size_bytes"],
            "created_at": datetime.utcnow()
        }
        db["reports"].insert_one(report_doc)
        return db["reports"].find_one({"id": report_id}, {"_id": 0})

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}"
        )

@router.get("/report/{id}/download")
def download_report_pdf(id: int):
    """
    Downloads the PDF report file for report ID or dataset ID.
    """
    db = get_db()
    report = db["reports"].find_one({"id": id})
    if not report:
        cursor = db["reports"].find({"dataset_id": id}).sort("created_at", -1).limit(1)
        res = list(cursor)
        if res:
            report = res[0]

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file with ID {id} not found."
        )

    file_path = Path(report["storage_path"])
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file on disk was not found."
        )

    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=Path(report["storage_path"]).name
    )
