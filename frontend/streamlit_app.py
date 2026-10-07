import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Automated Data Analysis & Reporting Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look & feel
st.markdown("""
<style>
    /* Main Background & Font Styling */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Custom Header Styling */
    .app-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: #F8FAFC;
        letter-spacing: -0.025em;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.25rem;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #2563EB !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #E2E8F0 !important;
        font-weight: 500;
    }

    /* Buttons Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Imports for views
from views.dashboard_view import render_dashboard
from views.dataset_list_view import render_dataset_list
from views.dataset_details_view import render_dataset_details
from views.analysis_view import render_analysis_results
from views.chart_gallery_view import render_chart_gallery
from views.report_downloads_view import render_report_downloads

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

# Application Header
st.markdown("""
<div class="app-header">
    <div class="app-title">📊 Automated Data Analysis & Reporting Platform</div>
    <div class="app-subtitle">MVP Engine for Data Extraction, Automated Cleaning, Analytics, Plotting & ReportLab PDF Generation</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/96/analytics.png", width=70)
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to Page:",
    [
        "📊 Dashboard",
        "📂 Dataset List",
        "🔍 Dataset Details",
        "📈 Analysis Results",
        "🖼️ Chart Gallery",
        "📄 Report Downloads"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Platform Capabilities:**
- File Types: CSV, XLSX, XLS, PDF
- Cleaning: Nulls, Duplicates, Types, Dates
- Stats: Numerical & Categorical
- Charts: Histograms, Boxplots, Bar, Pie, Heatmap
- PDF: Publication-Quality ReportLab Reports
""")

# Route to view
if page == "📊 Dashboard":
    render_dashboard(API_BASE_URL)
elif page == "📂 Dataset List":
    render_dataset_list(API_BASE_URL)
elif page == "🔍 Dataset Details":
    render_dataset_details(API_BASE_URL)
elif page == "📈 Analysis Results":
    render_analysis_results(API_BASE_URL)
elif page == "🖼️ Chart Gallery":
    render_chart_gallery(API_BASE_URL)
elif page == "📄 Report Downloads":
    render_report_downloads(API_BASE_URL)
