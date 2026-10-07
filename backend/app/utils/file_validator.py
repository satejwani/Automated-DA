import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from backend.app.core.config import settings

def validate_uploaded_file(file: UploadFile) -> str:
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats are: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext

def generate_unique_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    unique_prefix = uuid.uuid4().hex[:10]
    safe_basename = Path(original_filename).stem.replace(" ", "_")
    return f"{unique_prefix}_{safe_basename}{ext}"
