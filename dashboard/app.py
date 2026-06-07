import streamlit as st

st.set_page_config(
    page_title = "Review Rating System",
    page_icon  = "📊",
    layout     = "wide",
)

from dashboard.pages.overview        import render as render_overview
from dashboard.pages.business_detail import render as render_business_detail

PAGES = {
    "📊 Overview":        render_overview,
    "🏪 Business Detail": render_business_detail,
}

page = st.sidebar.radio("Navigation", list(PAGES.keys()))
st.sidebar.divider()
PAGES[page]()
