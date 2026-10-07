from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ColumnSchema(BaseModel):
    id: int
    column_name: str
    data_type: str
    inferred_type: str
    is_nullable: bool
    null_count: int
    unique_count: int

    class Config:
        from_attributes = True

class DatasetSchema(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    row_count: int
    column_count: int
    upload_timestamp: datetime
    columns: Optional[List[ColumnSchema]] = []

    class Config:
        from_attributes = True

class DatasetListResponse(BaseModel):
    total: int
    datasets: List[DatasetSchema]
