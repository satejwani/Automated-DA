import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from backend.app.core.database import get_db, get_next_sequence_value
from backend.app.core.config import settings
from backend.app.utils.file_validator import validate_uploaded_file, generate_unique_filename
from backend.app.services.extraction_service import ExtractionService
from backend.app.schemas.dataset import DatasetSchema

router = APIRouter()

@router.post("/upload", response_model=DatasetSchema, status_code=status.HTTP_201_CREATED)
def upload_dataset(file: UploadFile = File(...)):
    """
    Validates, stores, extracts metadata, and records dataset document in MongoDB.
    """
    ext = validate_uploaded_file(file)
    
    unique_name = generate_unique_filename(file.filename)
    dest_path = settings.UPLOAD_DIR / unique_name
    db = get_db()

    try:
        # Save file to uploads/
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = dest_path.stat().st_size

        # Parse DataFrame to count rows and inspect column schema
        df = ExtractionService.load_dataset_to_dataframe(dest_path, ext)
        col_info = ExtractionService.infer_column_types(df)

        dataset_id = get_next_sequence_value("dataset_id")
        
        # Prepare embedded columns schema
        columns_list = []
        col_id_counter = 1
        for col_name, meta in col_info.items():
            columns_list.append({
                "id": col_id_counter,
                "column_name": col_name,
                "data_type": meta["data_type"],
                "inferred_type": meta["inferred_type"],
                "is_nullable": meta["is_nullable"],
                "null_count": meta["null_count"],
                "unique_count": meta["unique_count"]
            })
            col_id_counter += 1

        dataset_doc = {
            "id": dataset_id,
            "filename": unique_name,
            "original_filename": file.filename,
            "file_type": ext,
            "file_size_bytes": file_size,
            "storage_path": str(dest_path),
            "row_count": len(df),
            "column_count": len(df.columns),
            "upload_timestamp": datetime.utcnow(),
            "columns": columns_list
        }

        db["datasets"].insert_one(dataset_doc)
        return dataset_doc

    except Exception as e:
        if dest_path.exists():
            dest_path.unlink() # cleanup file on failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset upload: {str(e)}"
        )
