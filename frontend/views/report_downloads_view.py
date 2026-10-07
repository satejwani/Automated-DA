import streamlit as st
import requests

def render_report_downloads(api_base_url: str):
    st.markdown("### 📄 PDF Report Downloads Center")
    st.caption("Generate and download publication-ready ReportLab PDF reports containing executive summaries, quality metrics, tables, and charts.")

    # Select Dataset to generate report
    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code != 200:
            st.error("Failed to load dataset list.")
            return

        datasets = res.json().get("datasets", [])
        if not datasets:
            st.info("No datasets uploaded yet.")
            return

        st.markdown("#### ⚡ Generate New PDF Report")
        dataset_options = {f"#{d['id']} - {d['original_filename']}": d['id'] for d in datasets}
        selected_label = st.selectbox("Select Dataset for PDF Report Generation:", list(dataset_options.keys()), key="report_ds_select")
        selected_id = dataset_options[selected_label]

        if st.button("📄 Build PDF Report", type="primary"):
            with st.spinner("Compiling ReportLab PDF document with tables and charts..."):
                r_res = requests.post(f"{api_base_url}/report/{selected_id}")
                if r_res.status_code in [200, 201]:
                    st.success(f"Report generated successfully! Title: {r_res.json()['report_title']}")
                    st.rerun()
                else:
                    st.error(f"Report generation error: {r_res.json().get('detail')}")

        st.markdown("---")

        # Report Downloads Center
        st.markdown("#### ⬇️ Download Available PDF Reports")
        # Direct PDF download link for selected dataset if available
        dl_res = requests.get(f"{api_base_url}/report/{selected_id}/download")
        if dl_res.status_code == 200:
            st.download_button(
                label=f"📥 Download PDF Report for Dataset #{selected_id}",
                data=dl_res.content,
                file_name=f"Executive_Report_Dataset_{selected_id}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.info(f"No PDF report built yet for Dataset #{selected_id}. Click 'Build PDF Report' above!")

    except Exception as e:
        st.error(f"Error accessing report service: {e}")
