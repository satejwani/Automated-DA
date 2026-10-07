import streamlit as st
import pandas as pd
import requests

def render_analysis_results(api_base_url: str):
    st.markdown("### 📈 Automated Analysis Results")
    st.caption("Data Quality summary, numerical statistics, categorical breakdowns, and correlation matrix.")

    # Select Dataset
    try:
        res = requests.get(f"{api_base_url}/datasets", timeout=5)
        if res.status_code != 200:
            st.error("Failed to load dataset list.")
            return

        datasets = res.json().get("datasets", [])
        if not datasets:
            st.info("No datasets available. Please upload a dataset first.")
            return

        dataset_options = {f"#{d['id']} - {d['original_filename']}": d['id'] for d in datasets}
        
        default_index = 0
        if 'selected_dataset_id' in st.session_state:
            for idx, (label, d_id) in enumerate(dataset_options.items()):
                if d_id == st.session_state['selected_dataset_id']:
                    default_index = idx
                    break

        selected_label = st.selectbox("Select Dataset Analysis to View:", list(dataset_options.keys()), index=default_index, key="analysis_ds_select")
        selected_id = dataset_options[selected_label]

        # Fetch Analysis Result
        a_res = requests.get(f"{api_base_url}/analysis/{selected_id}")
        if a_res.status_code != 200:
            st.warning(f"No analysis result found for Dataset #{selected_id}. Click below to run analysis!")
            if st.button("🚀 Run Automated Analysis Now", type="primary"):
                with st.spinner("Processing automated analysis engine..."):
                    run_res = requests.post(f"{api_base_url}/analyze/{selected_id}")
                    if run_res.status_code in [200, 201]:
                        st.success("Analysis complete!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {run_res.json().get('detail')}")
            return

        analysis_data = a_res.json()
        dq = analysis_data.get("data_quality_json", {})
        num_stats = analysis_data.get("numerical_stats_json", {})
        cat_stats = analysis_data.get("categorical_stats_json", {})
        corr_stats = analysis_data.get("correlation_matrix_json", {})

        # 1. Data Quality Score Summary
        st.markdown("#### 🛡️ Data Quality Summary")
        q_score = analysis_data.get("quality_score", 0.0)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Quality Score", f"{q_score}%")
        c2.metric("Completeness Rate", f"{dq.get('completeness_score', 0)}%")
        c3.metric("Uniqueness Rate", f"{dq.get('uniqueness_score', 0)}%")
        c4.metric("Validity Rate", f"{dq.get('validity_score', 0)}%")

        st.info(
            f"**Missing Cells**: {dq.get('total_missing_cells', 0):,} ({dq.get('missing_percentage', 0)}%) | "
            f"**Duplicate Rows**: {dq.get('duplicate_rows', 0):,} ({dq.get('duplicate_percentage', 0)}%) | "
            f"**Detected Date Columns**: {', '.join(dq.get('date_columns', [])) or 'None'}"
        )

        st.markdown("---")

        # 2. Numerical Analysis
        st.markdown("#### 🔢 Numerical Statistics")
        if num_stats:
            num_rows = []
            for col_name, stats in num_stats.items():
                num_rows.append({
                    "Column": col_name,
                    "Mean": stats.get("mean"),
                    "Median": stats.get("median"),
                    "Mode": stats.get("mode"),
                    "Min": stats.get("min"),
                    "Max": stats.get("max"),
                    "Std Dev": stats.get("std"),
                    "25th %": stats.get("q25"),
                    "75th %": stats.get("q75")
                })
            st.dataframe(pd.DataFrame(num_rows), use_container_width=True)
        else:
            st.info("No numerical columns present in this dataset.")

        st.markdown("---")

        # 3. Categorical Analysis
        st.markdown("#### 🏷️ Categorical Distribution")
        if cat_stats:
            for col_name, stats in cat_stats.items():
                with st.expander(f"Categorical Feature: {col_name} ({stats['unique_values']} unique values)", expanded=False):
                    st.write(f"**Top Category**: `{stats['top_category']}` (Count: {stats['top_category_count']})")
                    freq_df = pd.DataFrame([
                        {"Category": cat, "Count": info["count"], "Percentage": f"{info['percentage']}%"}
                        for cat, info in stats.get("frequency_distribution", {}).items()
                    ])
                    st.dataframe(freq_df, use_container_width=True)
        else:
            st.info("No categorical columns present in this dataset.")

        st.markdown("---")

        # 4. Correlation Analysis
        st.markdown("#### 🔗 Correlation Analysis")
        matrix = corr_stats.get("matrix", {})
        if matrix:
            st.write("**Pearson Correlation Matrix**:")
            corr_df = pd.DataFrame(matrix)
            st.dataframe(corr_df.style.background_gradient(cmap="coolwarm", vmin=-1.0, vmax=1.0), use_container_width=True)

            pos = corr_stats.get("strong_positive", [])
            neg = corr_stats.get("strong_negative", [])

            if pos:
                st.success(f"**Strong Positive Correlations (r ≥ 0.6)**: " + ", ".join([f"{p['col1']} & {p['col2']} (r={p['correlation']})" for p in pos]))
            if neg:
                st.warning(f"**Strong Negative Correlations (r ≤ -0.6)**: " + ", ".join([f"{n['col1']} & {n['col2']} (r={n['correlation']})" for n in neg]))
        else:
            st.info("Insufficient numerical features to calculate correlation matrix.")

    except Exception as e:
        st.error(f"Error loading analysis results: {e}")
