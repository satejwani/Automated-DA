import pdfplumber
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_dataframe_from_pdf(file_path: Path) -> pd.DataFrame:
    """
    Extracts tabular data from a PDF file using pdfplumber into a unified Pandas DataFrame.
    """
    all_rows = []
    headers = None

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    for row_idx, row in enumerate(table):
                        # Clean cell values (strip text, handle None)
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        if not any(cleaned_row):
                            continue # skip empty rows
                        
                        if headers is None:
                            headers = cleaned_row
                        elif cleaned_row == headers:
                            continue # skip header repeats across pages
                        else:
                            all_rows.append(cleaned_row)

        if not headers:
            raise ValueError("No table structures found in PDF file.")

        # Ensure all rows have equal column count matching headers
        num_cols = len(headers)
        adjusted_rows = []
        for r in all_rows:
            if len(r) == num_cols:
                adjusted_rows.append(r)
            elif len(r) < num_cols:
                adjusted_rows.append(r + [""] * (num_cols - len(r)))
            else:
                adjusted_rows.append(r[:num_cols])

        df = pd.DataFrame(adjusted_rows, columns=headers)
        return df

    except Exception as e:
        logger.error(f"Failed to extract table from PDF {file_path}: {e}")
        raise ValueError(f"Failed to extract tabular data from PDF: {str(e)}")
