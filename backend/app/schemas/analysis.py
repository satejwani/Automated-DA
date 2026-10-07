from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List

class AnalysisResultSchema(BaseModel):
    id: int
    dataset_id: int
    analysis_timestamp: datetime
    quality_score: float
    data_quality_json: Dict[str, Any]
    numerical_stats_json: Dict[str, Any]
    categorical_stats_json: Dict[str, Any]
    correlation_matrix_json: Dict[str, Any]

    class Config:
        from_attributes = True
