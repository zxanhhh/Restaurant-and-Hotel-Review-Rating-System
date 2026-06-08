import streamlit as st
from dashboard.api_client import fetch_summary
from dashboard.charts import overall_donut_chart


def render():
    st.title("📊 Review Rating System")
    st.caption("Phân tích sentiment review nhà hàng & khách sạn bằng Claude AI")

    summary = fetch_summary()
    if summary is None:
        st.error("Không thể kết nối tới API. Hãy chắc chắn FastAPI server đang chạy.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Businesses",       summary["total_businesses"])
    col2.metric("Total Reviews",    summary["total_reviews"])
    col3.metric("Reviews Analyzed", summary["total_analyzed"])

    st.divider()

    left, right = st.columns([1, 2])
    with left:
        st.subheader("Overall Sentiment")
        st.plotly_chart(overall_donut_chart(summary), use_container_width=True)

    with right:
        st.subheader("Quick Stats")
        pos = summary["overall_positive"]
        neu = summary["overall_neutral"]
        neg = summary["overall_negative"]
        st.progress(pos / 100, text=f"✅ Positive  {pos:.1f}%")
        st.progress(neu / 100, text=f"⚠️ Neutral   {neu:.1f}%")
        st.progress(neg / 100, text=f"❌ Negative  {neg:.1f}%")

        total_rev = summary["total_reviews"]
        analyzed  = summary["total_analyzed"]
        coverage  = (analyzed / total_rev * 100) if total_rev > 0 else 0
        st.info(f"Pipeline coverage: **{coverage:.1f}%** reviews đã được phân tích")
