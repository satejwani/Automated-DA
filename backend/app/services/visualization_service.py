import matplotlib
matplotlib.use('Agg') # Non-interactive backend for headless file generation
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import uuid
import logging
from typing import List, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure clean aesthetic Matplotlib theme
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.titlesize': 14
})

PRIMARY_COLOR = '#3B82F6' # Vibrant Blue
ACCENT_COLOR = '#10B981'  # Emerald Green
PALETTE = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6']

class VisualizationService:
    @staticmethod
    def generate_all_charts(df: pd.DataFrame, dataset_id: int, analysis_id: int) -> List[Dict[str, Any]]:
        """
        Generates static PNG visualization charts for numerical, categorical, date, and correlation structures.
        Returns chart metadata dicts for database insertion.
        """
        generated_charts = []

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # 1. Numerical Columns: Histograms & Box Plots
        for col in num_cols[:4]: # Limit to top 4 numeric columns for chart generation
            series = df[col].dropna()
            if series.empty:
                continue

            # Histogram
            fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
            sns.histplot(series, kde=True, color=PRIMARY_COLOR, ax=ax, edgecolor='white', linewidth=1.2)
            ax.set_title(f"Distribution of {col}", fontweight='bold', pad=12)
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
            fig.tight_layout()
            chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Histogram", f"Histogram of {col}")
            if chart_meta:
                generated_charts.append(chart_meta)

            # Box Plot
            fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
            sns.boxplot(x=series, color=ACCENT_COLOR, ax=ax, fliersize=3)
            ax.set_title(f"Box Plot of {col}", fontweight='bold', pad=12)
            ax.set_xlabel(col)
            fig.tight_layout()
            chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Box Plot", f"Box Plot of {col}")
            if chart_meta:
                generated_charts.append(chart_meta)

        # 2. Categorical Columns: Bar Chart & Pie Chart
        for col in cat_cols[:4]: # Limit to top 4 categorical columns
            series = df[col].dropna().astype(str)
            if series.empty:
                continue
            
            counts = series.value_counts().head(8)
            if counts.empty:
                continue

            # Bar Chart
            fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
            sns.barplot(x=counts.values, y=counts.index, palette=PALETTE, ax=ax)
            ax.set_title(f"Top Categories in {col}", fontweight='bold', pad=12)
            ax.set_xlabel("Count")
            ax.set_ylabel(col)
            fig.tight_layout()
            chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Bar Chart", f"Bar Chart of {col}")
            if chart_meta:
                generated_charts.append(chart_meta)

            # Pie Chart
            if len(counts) <= 6:
                fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=PALETTE[:len(counts)], startangle=140,
                       wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
                ax.set_title(f"Composition of {col}", fontweight='bold', pad=12)
                fig.tight_layout()
                chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Pie Chart", f"Pie Chart of {col}")
                if chart_meta:
                    generated_charts.append(chart_meta)

        # 3. Date Columns: Trend Chart
        date_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)
            elif df[col].dtype == 'object':
                sample = df[col].dropna().head(30)
                if not sample.empty:
                    try:
                        parsed = pd.to_datetime(sample, format='mixed', errors='coerce')
                        if parsed.notnull().mean() > 0.8:
                            date_cols.append(col)
                    except Exception:
                        pass

        for d_col in date_cols[:2]:
            try:
                temp_df = df.copy()
                temp_df[d_col] = pd.to_datetime(temp_df[d_col], errors='coerce')
                temp_df = temp_df.dropna(subset=[d_col])
                if not temp_df.empty:
                    trend_data = temp_df.set_index(d_col).resample('D').size()
                    if len(trend_data) > 1:
                        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
                        ax.plot(trend_data.index, trend_data.values, color=PRIMARY_COLOR, linewidth=2, marker='o', markersize=4)
                        ax.set_title(f"Time Series Trend ({d_col})", fontweight='bold', pad=12)
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Record Count")
                        fig.autofmt_xdate()
                        fig.tight_layout()
                        chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Trend Chart", f"Trend Chart of {d_col}")
                        if chart_meta:
                            generated_charts.append(chart_meta)
            except Exception as e:
                logger.warning(f"Could not generate trend chart for {d_col}: {e}")

        # 4. Correlation Heatmap
        if len(num_cols) > 1:
            try:
                fig, ax = plt.subplots(figsize=(7.5, 6), dpi=150)
                corr = df[num_cols].corr()
                sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax, cbar_kws={'label': 'Correlation Coefficient'})
                ax.set_title("Correlation Heatmap", fontweight='bold', pad=12)
                fig.tight_layout()
                chart_meta = VisualizationService._save_fig(fig, dataset_id, analysis_id, "Heatmap", "Correlation Heatmap")
                if chart_meta:
                    generated_charts.append(chart_meta)
            except Exception as e:
                logger.warning(f"Could not generate correlation heatmap: {e}")

        return generated_charts

    @staticmethod
    def _save_fig(fig, dataset_id: int, analysis_id: int, chart_type: str, title: str) -> Dict[str, Any]:
        try:
            filename = f"chart_{dataset_id}_{uuid.uuid4().hex[:8]}.png"
            file_path = settings.CHART_DIR / filename
            fig.savefig(file_path, bbox_inches='tight')
            plt.close(fig)

            return {
                "dataset_id": dataset_id,
                "analysis_id": analysis_id,
                "chart_type": chart_type,
                "chart_title": title,
                "storage_path": str(file_path),
                "filename": filename,
                "chart_metadata_json": {
                    "width": 1050,
                    "height": 675,
                    "dpi": 150
                }
            }
        except Exception as e:
            logger.error(f"Error saving chart figure: {e}")
            plt.close(fig)
            return None
