import os
try:
    import streamlit as st
    API_BASE = st.secrets.get("API_BASE_URL", os.getenv("API_BASE_URL", "http://localhost:8000/api/v1"))
except Exception:
    API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

PAGE_SIZE = 20
