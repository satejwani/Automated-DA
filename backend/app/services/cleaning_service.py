import pandas as pd
import numpy as np
from typing import Dict, Any

class CleaningService:
    @staticmethod
    def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Performs data quality analysis including missing values, duplicate rows,
        invalid value checks, date detection, and computes an overall Data Quality Score (0-100).
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols if total_cols > 0 else 1

        # 1. Missing Value Analysis
        missing_by_col = df.isnull().sum().to_dict()
        total_missing = int(df.isnull().sum().sum())
        missing_percentage = round((total_missing / total_cells) * 100, 2)

        # 2. Duplicate Row Analysis
        duplicate_rows = int(df.duplicated().sum())
        duplicate_percentage = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0

        # 3. Invalid Values (Inf, -Inf, Whitespace-only strings)
        invalid_cells = 0
        column_invalid_counts = {}
        for col in df.columns:
            series = df[col]
            inv_count = 0
            if pd.api.types.is_numeric_dtype(series):
                inv_count += int(np.isinf(series.dropna()).sum())
            elif series.dtype == 'object':
                # Check for empty or whitespace-only strings
                inv_count += int((series.astype(str).str.strip() == '').sum()) - int(series.isnull().sum())
                inv_count = max(0, inv_count)
            column_invalid_counts[col] = inv_count
            invalid_cells += inv_count

        # 4. Date Column Detection
        date_columns = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.append(col)
            elif df[col].dtype == 'object':
                sample = df[col].dropna().head(30)
                if not sample.empty:
                    try:
                        parsed = pd.to_datetime(sample, format='mixed', errors='coerce')
                        if parsed.notnull().mean() > 0.8:
                            date_columns.append(col)
                    except Exception:
                        pass

        # 5. Data Quality Score Calculation (weighted: 50% Completeness, 30% Uniqueness, 20% Validity)
        completeness = max(0.0, 100.0 - missing_percentage)
        uniqueness = max(0.0, 100.0 - duplicate_percentage)
        validity = max(0.0, 100.0 - ((invalid_cells / total_cells) * 100))

        quality_score = round((0.5 * completeness) + (0.3 * uniqueness) + (0.2 * validity), 1)

        quality_summary = {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "total_cells": total_cells,
            "total_missing_cells": total_missing,
            "missing_percentage": missing_percentage,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": duplicate_percentage,
            "invalid_cells": invalid_cells,
            "date_columns": date_columns,
            "completeness_score": round(completeness, 1),
            "uniqueness_score": round(uniqueness, 1),
            "validity_score": round(validity, 1),
            "overall_quality_score": quality_score,
            "column_missing_counts": missing_by_col,
            "column_invalid_counts": column_invalid_counts
        }

        return quality_summary
