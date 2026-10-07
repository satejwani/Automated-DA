import pandas as pd
from pathlib import Path
from typing import Tuple
import logging
from backend.app.utils.pdf_extractor import extract_dataframe_from_pdf

logger = logging.getLogger(__name__)

class ExtractionService:
    @staticmethod
    def load_dataset_to_dataframe(file_path: Path, file_type: str) -> pd.DataFrame:
        """
        Loads dataset into a standardized Pandas DataFrame regardless of input file type.
        """
        ext = file_type.lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            elif ext == ".pdf":
                df = extract_dataframe_from_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            # Clean column names (strip whitespace, avoid duplicate column names)
            df.columns = [str(col).strip() if col is not None else f"Unnamed_{i}" for i, col in enumerate(df.columns)]
            return df
        except Exception as e:
            logger.error(f"Error loading dataset {file_path}: {e}")
            raise ValueError(f"Could not parse dataset file: {str(e)}")

    @staticmethod
    def infer_column_types(df: pd.DataFrame) -> dict:
        """
        Infers business data types: Numeric, Categorical, Date/Time, Boolean, or Text.
        """
        column_info = {}
        for col in df.columns:
            series = df[col]
            dtype_str = str(series.dtype)
            
            # Check for date time
            is_date = False
            if pd.api.types.is_datetime64_any_dtype(series):
                is_date = True
            elif series.dtype == 'object':
                # Try parsing sample non-null values to datetime
                sample = series.dropna().head(50)
                if not sample.empty:
                    try:
                        parsed = pd.to_datetime(sample, format='mixed', errors='coerce')
                        if parsed.notnull().mean() > 0.8:
                            is_date = True
                    except Exception:
                        pass
            
            if is_date:
                inferred = "Date/Time"
            elif pd.api.types.is_numeric_dtype(series):
                if series.nunique() <= 2 and series.dropna().isin([0, 1]).all():
                    inferred = "Boolean"
                else:
                    inferred = "Numerical"
            elif pd.api.types.is_bool_dtype(series):
                inferred = "Boolean"
            else:
                unique_ratio = series.nunique() / max(len(series), 1)
                if unique_ratio < 0.3 or series.nunique() < 50:
                    inferred = "Categorical"
                else:
                    inferred = "Text"

            column_info[col] = {
                "data_type": dtype_str,
                "inferred_type": inferred,
                "null_count": int(series.isnull().sum()),
                "unique_count": int(series.nunique()),
                "is_nullable": bool(series.isnull().any())
            }
        return column_info
