import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from dashboard.api_client import fetch_businesses, fetch_insights, fetch_reviews
from dashboard.charts import sentiment_bar_chart
from dashboard.config import PAGE_SIZE


def render():
    st.title("🏪 Business Insights")

    from dashboard.config import API_BASE

    businesses = fetch_businesses()

    if not businesses:
        st.error(f"Không lấy được businesses từ API. URL: {API_BASE}/businesses")
        st.info("Thử mở link trên trình duyệt xem có trả về data không.")
        return

    options       = {b["name"]: b["id"] for b in businesses}
    selected_name = st.sidebar.selectbox("Chọn Business", list(options.keys()))
    selected_id   = options[selected_name]

    # Reset pagination khi đổi business
    if st.session_state.get("last_business_id") != selected_id:
        st.session_state.review_page      = 0
        st.session_state.last_business_id = selected_id

    # --- Insights ---
    st.subheader(f"📈 Sentiment Breakdown — {selected_name}")
    insights = fetch_insights(selected_id)

    if insights is None:
        st.info("Chưa có dữ liệu phân tích. Hãy chạy pipeline trước.")
    else:
        st.plotly_chart(
            sentiment_bar_chart(insights["categories"]),
            use_container_width=True,
        )

        st.subheader("💡 Top Strengths & Weaknesses")
        for cat in insights["categories"]:
            with st.expander(f"**{cat['category']}** — {cat['total_reviews']} reviews"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**✅ Strengths**")
                    for s in (cat.get("top_strengths") or []):
                        st.markdown(f"- {s}")
                    if not (cat.get("top_strengths") or []):
                        st.caption("Chưa có dữ liệu")
                with c2:
                    st.markdown("**❌ Weaknesses**")
                    for w in (cat.get("top_weaknesses") or []):
                        st.markdown(f"- {w}")
                    if not (cat.get("top_weaknesses") or []):
                        st.caption("Chưa có dữ liệu")

    st.divider()

    # --- Reviews với pagination ---
    st.subheader("📝 Reviews")

    if "review_page" not in st.session_state:
        st.session_state.review_page = 0

    reviews = fetch_reviews(
        selected_id,
        limit  = PAGE_SIZE,
        offset = st.session_state.review_page * PAGE_SIZE,
    )

    if not reviews:
        st.caption("Không có review nào.")
    else:
        for r in reviews:
            rating_str = f"⭐ {r['rating']:.1f}" if r["rating"] else "—"
            badges     = "  ".join(
                f"`{cat}: {sent}`" for cat, sent in r["sentiments"].items()
            )
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"**{r['reviewer_name'] or 'Anonymous'}** "
                        f"— {r['review_date'] or ''}"
                    )
                    st.write(r["content"])
                    if badges:
                        st.markdown(badges)
                with col2:
                    st.markdown(f"### {rating_str}")

    # Pagination controls
    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.session_state.review_page > 0:
            if st.button("← Prev"):
                st.session_state.review_page -= 1
                st.rerun()
    with p2:
        st.caption(f"Trang {st.session_state.review_page + 1}")
    with p3:
        if len(reviews) == PAGE_SIZE:
            if st.button("Next →"):
                st.session_state.review_page += 1
                st.rerun()

render()
