import streamlit as st
import pandas as pd
import requests
from pathlib import Path

def render_dashboard(api_base_url: str):
    st.markdown("### 📊 Platform Executive Dashboard")
    st.caption("Overview of uploaded datasets, automated analysis runs, generated charts, and PDF reports.")

    # 1. Fetch Dashboard Stats
    try:
        res = requests.get(f"{api_base_url}/dashboard/stats", timeout=5)
        if res.status_code == 200:
            stats = res.json()
        else:
            stats = {"total_datasets": 0, "total_analyses": 0, "total_reports": 0, "total_charts": 0}
    except Exception:
        stats = {"total_datasets": 0, "total_analyses": 0, "total_reports": 0, "total_charts": 0}

    # Stat Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Uploaded Files", value=stats["total_datasets"], delta="Datasets")
    with c2:
        st.metric(label="Total Analyses Executed", value=stats["total_analyses"], delta="Runs")
    with c3:
        st.metric(label="Total Reports Generated", value=stats["total_reports"], delta="PDFs")
    with c4:
        st.metric(label="Total Charts Created", value=stats["total_charts"], delta="Graphics")

    st.markdown("---")

    # 2. File Upload Module Section
    st.markdown("#### 📁 Quick Upload Dataset")
    uploaded_file = st.file_uploader(
        "Choose a dataset (CSV, Excel .xlsx/.xls, or PDF table)",
        type=["csv", "xlsx", "xls", "pdf"],
        help="Maximum file size 50 MB"
    )

    if uploaded_file is not None:
        if st.button("🚀 Upload & Register Dataset", type="primary"):
            with st.spinner("Uploading and analyzing schema..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    resp = requests.post(f"{api_base_url}/upload", files=files)
                    if resp.status_code == 201:
                        data = resp.json()
                        st.success(f"Successfully uploaded **{data['original_filename']}**! Assigned Dataset ID: #{data['id']}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.markdown("---")

    # 3. Recent Datasets Quick Action Table
    st.markdown("#### 📂 Recent Datasets")
    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code == 200:
            datasets = res.json().get("datasets", [])
            if not datasets:
                st.info("No datasets uploaded yet. Upload your first dataset above!")
            else:
                df_summary = []
                for d in datasets[:10]:
                    df_summary.append({
                        "ID": d["id"],
                        "File Name": d["original_filename"],
                        "Type": d["file_type"].upper(),
                        "Rows": f"{d['row_count']:,}",
                        "Columns": d["column_count"],
                        "Size (KB)": round(d["file_size_bytes"] / 1024, 1),
                        "Uploaded At": d["upload_timestamp"][:19].replace("T", " ")
                    })
                st.dataframe(pd.DataFrame(df_summary), use_container_width=True)
        else:
            st.error("Failed to load dataset list.")
    except Exception as e:
        st.warning(f"Could not connect to backend API: {e}")
