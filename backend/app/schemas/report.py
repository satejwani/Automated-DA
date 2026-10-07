from pydantic import BaseModel
from datetime import datetime

class ReportSchema(BaseModel):
    id: int
    dataset_id: int
    analysis_id: int
    report_title: str
    storage_path: str
    file_size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True
