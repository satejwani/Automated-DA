import streamlit as st
import requests
from pathlib import Path

def render_chart_gallery(api_base_url: str):
    st.markdown("### 🖼️ Generated Visualizations & Chart Gallery")
    st.caption("Browse, preview, and filter generated histograms, box plots, bar charts, pie charts, trend lines, and heatmaps.")

    # Select Dataset
    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code != 200:
            st.error("Failed to load dataset list.")
            return

        datasets = res.json().get("datasets", [])
        if not datasets:
            st.info("No datasets available.")
            return

        dataset_options = {f"#{d['id']} - {d['original_filename']}": d['id'] for d in datasets}
        selected_label = st.selectbox("Select Dataset Charts to View:", list(dataset_options.keys()), key="chart_ds_select")
        selected_id = dataset_options[selected_label]

        # Fetch Charts
        c_res = requests.get(f"{api_base_url}/charts/{selected_id}")
        if c_res.status_code != 200 or not c_res.json():
            st.warning(f"No generated charts found for Dataset #{selected_id}. Run analysis first!")
            return

        charts = c_res.json()
        
        # Chart Type Filter
        chart_types = ["All Types"] + list(set([c["chart_type"] for c in charts]))
        selected_type = st.selectbox("Filter by Chart Type:", chart_types)

        filtered_charts = charts if selected_type == "All Types" else [c for c in charts if c["chart_type"] == selected_type]

        st.markdown(f"Displaying **{len(filtered_charts)}** chart(s):")
        
        # Grid layout (2 columns)
        cols = st.columns(2)
        for idx, chart in enumerate(filtered_charts):
            col = cols[idx % 2]
            with col:
                st.markdown(f"##### 📊 {chart['chart_title']} ({chart['chart_type']})")
                img_url = f"{api_base_url}/charts/{chart['id']}/file"
                st.image(img_url, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading chart gallery: {e}")
