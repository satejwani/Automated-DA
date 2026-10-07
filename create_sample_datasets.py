import pandas as pd
import numpy as np
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

sample_dir = Path("d:/Automate DA/samples")
sample_dir.mkdir(parents=True, exist_ok=True)

# 1. Create CSV Dataset
np.random.seed(42)
n_rows = 150
dates = pd.date_range(start="2025-01-01", periods=n_rows, freq="D")
categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Toys"]
regions = ["North", "South", "East", "West", "Central"]

csv_df = pd.DataFrame({
    "Transaction_ID": [f"TXN-{1000 + i}" for i in range(n_rows)],
    "Date": dates.astype(str),
    "Category": np.random.choice(categories, size=n_rows),
    "Region": np.random.choice(regions, size=n_rows),
    "Sales_Amount": np.round(np.random.normal(loc=250.0, scale=80.0, size=n_rows), 2),
    "Quantity": np.random.randint(1, 10, size=n_rows),
    "Discount_Pct": np.round(np.random.uniform(0.0, 0.3, size=n_rows), 2),
    "Customer_Rating": np.random.choice([1, 2, 3, 4, 5, np.nan], size=n_rows, p=[0.05, 0.1, 0.2, 0.4, 0.2, 0.05])
})

# Inject duplicate row and missing values
csv_df.loc[15] = csv_df.loc[14]
csv_df.loc[30, "Sales_Amount"] = np.nan
csv_df.loc[45, "Category"] = np.nan

csv_path = sample_dir / "sample_sales_data.csv"
csv_df.to_csv(csv_path, index=False)
print(f"Created CSV sample: {csv_path}")

# 2. Create Excel Dataset (.xlsx)
excel_df = pd.DataFrame({
    "Employee_ID": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "Department": ["Engineering", "HR", "Sales", "Engineering", "Marketing", "Sales", "Engineering", "Finance", "HR", "Finance"],
    "Salary": [85000, 62000, 75000, 92000, 68000, 78000, 88000, 95000, 64000, 91000],
    "Performance_Score": [4.5, 3.8, 4.2, 4.9, 3.6, 4.1, 4.7, 4.8, 3.9, 4.6],
    "Years_Experience": [5, 3, 6, 8, 4, 5, 7, 9, 4, 8]
})
excel_path = sample_dir / "sample_financial_data.xlsx"
excel_df.to_excel(excel_path, index=False)
print(f"Created Excel sample: {excel_path}")

# 3. Create PDF Dataset with tabular data
pdf_path = sample_dir / "sample_metrics_data.pdf"
doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
styles = getSampleStyleSheet()
elements = [
    Paragraph("Monthly Regional Summary Metrics", styles['Heading1']),
    Spacer(1, 12)
]

table_data = [
    ["Month", "Region", "Active_Users", "Revenue", "Conversion_Rate"],
    ["Jan", "North", "1250", "45000.50", "0.034"],
    ["Jan", "South", "980", "32000.00", "0.028"],
    ["Feb", "North", "1420", "51000.75", "0.038"],
    ["Feb", "South", "1100", "38500.20", "0.031"],
    ["Mar", "North", "1550", "58000.00", "0.041"],
    ["Mar", "South", "1210", "41000.60", "0.033"]
]

pdf_table = Table(table_data, colWidths=[80, 80, 100, 100, 100])
pdf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(pdf_table)
doc.build(elements)
print(f"Created PDF sample: {pdf_path}")
