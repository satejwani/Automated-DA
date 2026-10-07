import streamlit as st
import pandas as pd
import requests

def render_dataset_details(api_base_url: str):
    st.markdown("### 🔍 Dataset Details & Schema Explorer")
    st.caption("Deep-dive inspection into column types, null rates, and unique counts.")

    # Dataset Selector
    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code != 200:
            st.error("Failed to load dataset list.")
            return

        datasets = res.json().get("datasets", [])
        if not datasets:
            st.info("No datasets available.")
            return

        dataset_options = {f"#{d['id']} - {d['original_filename']} ({d['file_type']})": d['id'] for d in datasets}
        
        default_index = 0
        if 'selected_dataset_id' in st.session_state:
            for idx, (label, d_id) in enumerate(dataset_options.items()):
                if d_id == st.session_state['selected_dataset_id']:
                    default_index = idx
                    break

        selected_label = st.selectbox("Select Dataset to Inspect:", list(dataset_options.keys()), index=default_index)
        selected_id = dataset_options[selected_label]

        # Fetch detail metadata
        d_res = requests.get(f"{api_base_url}/dataset/{selected_id}")
        if d_res.status_code == 200:
            d_data = d_res.json()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Filename", d_data['original_filename'])
            c2.metric("Total Rows", f"{d_data['row_count']:,}")
            c3.metric("Total Columns", d_data['column_count'])
            c4.metric("Storage Path", d_data['storage_path'][:25] + "...")

            st.markdown("#### 📋 Column Schema & Data Types")
            columns = d_data.get("columns", [])
            if columns:
                col_df = pd.DataFrame([
                    {
                        "Column Name": c["column_name"],
                        "Raw Data Type": c["data_type"],
                        "Inferred Business Type": c["inferred_type"],
                        "Is Nullable": "Yes" if c["is_nullable"] else "No",
                        "Null Count": c["null_count"],
                        "Unique Values": c["unique_count"]
                    } for c in columns
                ])
                st.dataframe(col_df, use_container_width=True)
            else:
                st.info("No column metadata stored.")

    except Exception as e:
        st.error(f"Error retrieving dataset details: {e}")
