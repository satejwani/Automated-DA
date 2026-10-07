from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from backend.app.core.database import get_db, get_next_sequence_value
from backend.app.schemas.analysis import AnalysisResultSchema
from backend.app.services.extraction_service import ExtractionService
from backend.app.services.cleaning_service import CleaningService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.visualization_service import VisualizationService

router = APIRouter()

@router.post("/analyze/{id}", response_model=AnalysisResultSchema, status_code=status.HTTP_201_CREATED)
def run_dataset_analysis(id: int):
    """
    Executes automated data cleaning, statistical analysis, and chart generation for dataset ID.
    Stores results in MongoDB.
    """
    db = get_db()
    dataset = db["datasets"].find_one({"id": id})
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {id} not found."
        )

    try:
        # 1. Load DataFrame
        file_path = Path(dataset["storage_path"])
        df = ExtractionService.load_dataset_to_dataframe(file_path, dataset["file_type"])

        # 2. Data Cleaning & Quality Analysis
        quality_summary = CleaningService.analyze_data_quality(df)

        # 3. Statistical Analysis
        analysis_data = AnalysisService.perform_automated_analysis(df, file_size_bytes=dataset["file_size_bytes"])

        analysis_id = get_next_sequence_value("analysis_id")

        # 4. Save Analysis Result Document
        analysis_doc = {
            "id": analysis_id,
            "dataset_id": dataset["id"],
            "analysis_timestamp": datetime.utcnow(),
            "quality_score": quality_summary["overall_quality_score"],
            "data_quality_json": quality_summary,
            "numerical_stats_json": analysis_data["numerical_analysis"],
            "categorical_stats_json": analysis_data["categorical_analysis"],
            "correlation_matrix_json": analysis_data["correlation_analysis"]
        }
        db["analysis_results"].insert_one(analysis_doc)

        # 5. Generate Visualizations & Save to MongoDB
        chart_meta_list = VisualizationService.generate_all_charts(df, dataset["id"], analysis_id)
        for meta in chart_meta_list:
            chart_id = get_next_sequence_value("chart_id")
            chart_doc = {
                "id": chart_id,
                "dataset_id": dataset["id"],
                "analysis_id": analysis_id,
                "chart_type": meta["chart_type"],
                "chart_title": meta["chart_title"],
                "storage_path": meta["storage_path"],
                "chart_metadata_json": meta["chart_metadata_json"],
                "created_at": datetime.utcnow()
            }
            db["generated_charts"].insert_one(chart_doc)

        return db["analysis_results"].find_one({"id": analysis_id}, {"_id": 0})

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Automated analysis failed: {str(e)}"
        )

@router.get("/analysis/{id}", response_model=AnalysisResultSchema)
def get_analysis_by_id(id: int):
    """
    Retrieves detailed analysis results by analysis ID or dataset ID fallback.
    """
    db = get_db()
    analysis = db["analysis_results"].find_one({"id": id}, {"_id": 0})
    if not analysis:
        # Check if ID passed was dataset_id
        cursor = db["analysis_results"].find({"dataset_id": id}, {"_id": 0}).sort("analysis_timestamp", -1).limit(1)
        res = list(cursor)
        if res:
            analysis = res[0]
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis result for ID {id} not found."
        )
    return analysis
