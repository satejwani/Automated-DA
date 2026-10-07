from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.core.database import get_db
from backend.app.schemas.dataset import DatasetSchema, DatasetListResponse

router = APIRouter()

@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets():
    """
    Retrieves all uploaded datasets from MongoDB.
    """
    db = get_db()
    cursor = db["datasets"].find({}, {"_id": 0}).sort("upload_timestamp", -1)
    datasets = list(cursor)
    return DatasetListResponse(total=len(datasets), datasets=datasets)

@router.get("/dataset/{id}", response_model=DatasetSchema)
def get_dataset_by_id(id: int):
    """
    Retrieves detailed metadata for a specific dataset ID including column schema.
    """
    db = get_db()
    dataset = db["datasets"].find_one({"id": id}, {"_id": 0})
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {id} not found."
        )
    return dataset
