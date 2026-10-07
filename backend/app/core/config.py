import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated Data Analysis Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # MongoDB Settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "automated_da")

    # File Storage Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    CHART_DIR: Path = BASE_DIR / "charts"
    REPORT_DIR: Path = BASE_DIR / "reports"

    # Validation
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls", ".pdf"}

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHART_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
