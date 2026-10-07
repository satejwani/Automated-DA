import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether, PageBreak
)
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    def generate_pdf_report(
        dataset_info: Dict[str, Any],
        quality_info: Dict[str, Any],
        analysis_info: Dict[str, Any],
        chart_paths: List[str]
    ) -> Dict[str, Any]:
        """
        Generates an automated, publication-quality PDF report using ReportLab.
        """
        dataset_id = dataset_info["id"]
        filename = f"report_dataset_{dataset_id}_{int(datetime.utcnow().timestamp())}.pdf"
        output_path = settings.REPORT_DIR / filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=14,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#1E293B')
        )
        table_header_style = ParagraphStyle(
            'TableHeaderCell',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.white
        )

        elements = []

        # 1. Document Header & Title
        elements.append(Paragraph("AUTOMATED DATA ANALYSIS REPORT", title_style))
        gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        elements.append(Paragraph(f"Dataset: <b>{dataset_info['original_filename']}</b> | Generated on: {gen_time}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

        # 2. Executive Summary
        elements.append(Paragraph("1. Executive Summary", h2_style))
        q_score = quality_info.get("overall_quality_score", 0.0)
        q_status = "Excellent" if q_score >= 85 else "Good" if q_score >= 70 else "Fair" if q_score >= 50 else "Poor"
        exec_text = (
            f"This automated report synthesizes structural, statistical, and data quality evaluations for dataset "
            f"<b>{dataset_info['original_filename']}</b>. The dataset contains <b>{dataset_info['row_count']:,}</b> rows and "
            f"<b>{dataset_info['column_count']}</b> columns. An overall Data Quality Score of <b>{q_score}% ({q_status})</b> "
            f"was assigned based on data completeness, uniqueness, and format validity."
        )
        elements.append(Paragraph(exec_text, body_style))
        elements.append(Spacer(1, 8))

        # 3. Dataset Overview Table
        elements.append(Paragraph("2. Dataset Overview", h2_style))
        overview_data = [
            [Paragraph("Property", table_header_style), Paragraph("Value", table_header_style)],
            [Paragraph("File Name", table_cell_style), Paragraph(str(dataset_info['original_filename']), table_cell_style)],
            [Paragraph("File Type", table_cell_style), Paragraph(str(dataset_info['file_type']).upper(), table_cell_style)],
            [Paragraph("File Size", table_cell_style), Paragraph(f"{dataset_info['file_size_bytes'] / 1024:.2f} KB", table_cell_style)],
            [Paragraph("Total Rows", table_cell_style), Paragraph(f"{dataset_info['row_count']:,}", table_cell_style)],
            [Paragraph("Total Columns", table_cell_style), Paragraph(str(dataset_info['column_count']), table_cell_style)],
            [Paragraph("Upload Timestamp", table_cell_style), Paragraph(str(dataset_info.get('upload_timestamp', gen_time)), table_cell_style)]
        ]
        overview_table = Table(overview_data, colWidths=[200, 340])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 10))

        # 4. Data Quality Report Table
        elements.append(Paragraph("3. Data Quality Report", h2_style))
        dq_data = [
            [Paragraph("Metric", table_header_style), Paragraph("Score / Value", table_header_style), Paragraph("Assessment", table_header_style)],
            [Paragraph("Overall Quality Score", table_cell_style), Paragraph(f"<b>{q_score}%</b>", table_cell_style), Paragraph(q_status, table_cell_style)],
            [Paragraph("Missing Value Cells", table_cell_style), Paragraph(f"{quality_info.get('total_missing_cells', 0):,} ({quality_info.get('missing_percentage', 0)}%)", table_cell_style), Paragraph("Completeness Metric", table_cell_style)],
            [Paragraph("Duplicate Rows", table_cell_style), Paragraph(f"{quality_info.get('duplicate_rows', 0):,} ({quality_info.get('duplicate_percentage', 0)}%)", table_cell_style), Paragraph("Uniqueness Metric", table_cell_style)],
            [Paragraph("Invalid / Infinity Cells", table_cell_style), Paragraph(f"{quality_info.get('invalid_cells', 0):,}", table_cell_style), Paragraph("Validity Metric", table_cell_style)],
            [Paragraph("Detected Date Columns", table_cell_style), Paragraph(", ".join(quality_info.get('date_columns', [])) or "None", table_cell_style), Paragraph("Temporal Features", table_cell_style)]
        ]
        dq_table = Table(dq_data, colWidths=[180, 180, 180])
        dq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(dq_table)
        elements.append(Spacer(1, 10))

        # 5. Statistical Analysis (Numerical Table)
        num_stats = analysis_info.get("numerical_analysis", {})
        if num_stats:
            elements.append(Paragraph("4. Statistical Analysis - Numerical Features", h2_style))
            num_rows = [
                [Paragraph("Column", table_header_style), Paragraph("Mean", table_header_style), Paragraph("Std Dev", table_header_style),
                 Paragraph("Median", table_header_style), Paragraph("Min", table_header_style), Paragraph("Max", table_header_style)]
            ]
            for col_name, stats in list(num_stats.items())[:8]: # Top 8 columns
                num_rows.append([
                    Paragraph(col_name, table_cell_style),
                    Paragraph(str(stats.get("mean", "-")), table_cell_style),
                    Paragraph(str(stats.get("std", "-")), table_cell_style),
                    Paragraph(str(stats.get("median", "-")), table_cell_style),
                    Paragraph(str(stats.get("min", "-")), table_cell_style),
                    Paragraph(str(stats.get("max", "-")), table_cell_style)
                ])
            num_table = Table(num_rows, colWidths=[140, 80, 80, 80, 80, 80])
            num_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(num_table)
            elements.append(Spacer(1, 10))

        # 6. Visualizations Section (Embed generated charts)
        if chart_paths:
            elements.append(Paragraph("5. Visualizations & Charts", h2_style))
            for i in range(0, len(chart_paths), 2):
                img_pair = []
                for p in chart_paths[i:i+2]:
                    if os.path.exists(p):
                        img_pair.append(Image(p, width=250, height=150))
                if len(img_pair) == 2:
                    t = Table([[img_pair[0], img_pair[1]]], colWidths=[270, 270])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
                    elements.append(t)
                    elements.append(Spacer(1, 6))
                elif len(img_pair) == 1:
                    t = Table([[img_pair[0]]], colWidths=[540])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
                    elements.append(t)
                    elements.append(Spacer(1, 6))

        # 7. Conclusions Section
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("6. Conclusions & Recommendations", h2_style))
        conclusion_text = (
            f"Based on the analysis of <b>{dataset_info['original_filename']}</b>, the dataset exhibits a quality score of "
            f"<b>{q_score}%</b>. "
        )
        if quality_info.get("missing_percentage", 0) > 5:
            conclusion_text += f"Noticeable missing values ({quality_info.get('missing_percentage')}% of total cells) require imputation or removal prior to downstream modeling. "
        else:
            conclusion_text += "Data completeness is high with negligible missing entries. "
        
        if quality_info.get("duplicate_rows", 0) > 0:
            conclusion_text += f"There are {quality_info.get('duplicate_rows')} duplicate records that should be deduplicated. "

        conclusion_text += "All statistical distributions and visualization graphics have been processed and cached for export."
        elements.append(Paragraph(conclusion_text, body_style))

        # Footer / Timestamp
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceAfter=8))
        elements.append(Paragraph(f"End of Automated Report | Generated by Automated Data Analysis Platform v1.0.0", subtitle_style))

        # Build PDF
        doc.build(elements)

        file_size = os.path.getsize(output_path)
        return {
            "dataset_id": dataset_id,
            "report_title": f"Executive Data Analysis Report - {dataset_info['original_filename']}",
            "storage_path": str(output_path),
            "filename": filename,
            "file_size_bytes": file_size,
            "created_at": datetime.utcnow()
        }
