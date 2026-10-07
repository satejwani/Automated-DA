import pandas as pd
import numpy as np
from typing import Dict, Any, List

class AnalysisService:
    @staticmethod
    def perform_automated_analysis(df: pd.DataFrame, file_size_bytes: int = 0) -> Dict[str, Any]:
        """
        Executes comprehensive statistical analysis:
        Dataset overview, numerical descriptive stats, categorical frequency stats, and correlation analysis.
        """
        # 1. Dataset Overview
        overview = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "file_size_bytes": file_size_bytes,
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum())
        }

        # Select column types
        num_df = df.select_dtypes(include=[np.number])
        cat_df = df.select_dtypes(include=['object', 'category', 'bool'])

        # 2. Numerical Analysis
        numerical_analysis = {}
        for col in num_df.columns:
            series = num_df[col].dropna()
            if series.empty:
                continue
            
            # Mode handling
            mode_vals = series.mode().tolist()
            mode_val = mode_vals[0] if len(mode_vals) > 0 else None

            numerical_analysis[col] = {
                "count": int(series.count()),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "mode": round(float(mode_val), 4) if isinstance(mode_val, (int, float, np.number)) else str(mode_val),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "std": round(float(series.std()), 4) if len(series) > 1 else 0.0,
                "q25": round(float(series.quantile(0.25)), 4),
                "q75": round(float(series.quantile(0.75)), 4)
            }

        # 3. Categorical Analysis
        categorical_analysis = {}
        for col in cat_df.columns:
            series = cat_df[col].dropna().astype(str)
            if series.empty:
                continue
            
            val_counts = series.value_counts()
            top_cats = val_counts.head(10).to_dict()
            total_valid = len(series)

            freq_dist = {
                cat: {
                    "count": int(count),
                    "percentage": round((count / total_valid) * 100, 2)
                } for cat, count in val_counts.head(15).items()
            }

            categorical_analysis[col] = {
                "unique_values": int(series.nunique()),
                "top_category": str(val_counts.index[0]) if not val_counts.empty else "N/A",
                "top_category_count": int(val_counts.iloc[0]) if not val_counts.empty else 0,
                "frequency_distribution": freq_dist,
                "top_categories": top_cats
            }

        # 4. Correlation Analysis
        correlation_matrix = {}
        strong_positive = []
        strong_negative = []

        if len(num_df.columns) > 1:
            corr = num_df.corr(method='pearson')
            # Clean correlation dict for JSON serializability
            for col1 in corr.columns:
                correlation_matrix[col1] = {}
                for col2 in corr.columns:
                    val = corr.loc[col1, col2]
                    correlation_matrix[col1][col2] = round(float(val), 4) if not np.isnan(val) else 0.0

            # Find strong correlations (upper triangle)
            cols = list(num_df.columns)
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    c1, c2 = cols[i], cols[j]
                    val = corr.loc[c1, c2]
                    if not np.isnan(val):
                        r_val = round(float(val), 4)
                        if r_val >= 0.6:
                            strong_positive.append({"col1": c1, "col2": c2, "correlation": r_val})
                        elif r_val <= -0.6:
                            strong_negative.append({"col1": c1, "col2": c2, "correlation": r_val})

        return {
            "overview": overview,
            "numerical_analysis": numerical_analysis,
            "categorical_analysis": categorical_analysis,
            "correlation_analysis": {
                "matrix": correlation_matrix,
                "strong_positive": strong_positive,
                "strong_negative": strong_negative
            }
        }
