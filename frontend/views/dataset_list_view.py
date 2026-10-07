import streamlit as st
import pandas as pd
import requests

def render_dataset_list(api_base_url: str):
    st.markdown("### 📂 Uploaded Datasets")
    st.caption("Browse, inspect schema, and trigger automated analysis runs.")

    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code != 200:
            st.error("Failed to retrieve dataset list.")
            return

        datasets = res.json().get("datasets", [])
        if not datasets:
            st.info("No datasets uploaded yet. Go to the Dashboard page to upload a file.")
            return

        for dataset in datasets:
            with st.expander(f"📄 #{dataset['id']} - {dataset['original_filename']} ({dataset['file_type'].upper()})", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Row Count", f"{dataset['row_count']:,}")
                col2.metric("Column Count", dataset['column_count'])
                col3.metric("File Size", f"{round(dataset['file_size_bytes'] / 1024, 1)} KB")
                col4.metric("Upload Date", dataset['upload_timestamp'][:10])

                b1, b2, b3 = st.columns([1, 1, 2])
                with b1:
                    if st.button(f"⚡ Run Analysis", key=f"btn_analyze_{dataset['id']}", type="primary"):
                        with st.spinner(f"Analyzing dataset #{dataset['id']}..."):
                            try:
                                a_res = requests.post(f"{api_base_url}/analyze/{dataset['id']}")
                                if a_res.status_code in [200, 201]:
                                    st.success(f"Analysis complete for Dataset #{dataset['id']}! Data Quality Score: {a_res.json()['quality_score']}%")
                                    st.session_state['selected_dataset_id'] = dataset['id']
                                    st.rerun()
                                else:
                                    st.error(f"Analysis failed: {a_res.json().get('detail')}")
                            except Exception as e:
                                st.error(f"Error calling analysis API: {e}")

                with b2:
                    if st.button(f"📑 Generate PDF", key=f"btn_report_{dataset['id']}"):
                        with st.spinner("Building ReportLab PDF..."):
                            try:
                                r_res = requests.post(f"{api_base_url}/report/{dataset['id']}")
                                if r_res.status_code in [200, 201]:
                                    st.success(f"Generated PDF Report #{r_res.json()['id']}!")
                                    st.session_state['selected_report_id'] = r_res.json()['id']
                                    st.rerun()
                                else:
                                    st.error(f"Report generation error: {r_res.json().get('detail')}")
                            except Exception as e:
                                st.error(f"Error calling report API: {e}")

                with b3:
                    if st.button(f"🔍 Inspect Schema & Details", key=f"btn_details_{dataset['id']}"):
                        st.session_state['selected_dataset_id'] = dataset['id']
                        st.info(f"Selected Dataset #{dataset['id']}. Switch to 'Dataset Details' or 'Analysis Results' tab!")

    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
