from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

class GeneratedChartSchema(BaseModel):
    id: int
    dataset_id: int
    analysis_id: int
    chart_type: str
    chart_title: str
    storage_path: str
    chart_metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
