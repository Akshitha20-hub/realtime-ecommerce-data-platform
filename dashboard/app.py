"""
Real-Time E-Commerce Data Engineering & Analytics Platform
==========================================================
Streamlit Dashboard – Phase 5

Shows business metrics, revenue trends, product performance, customer
behaviour, and payment analytics.  When PostgreSQL is running the
dashboard fetches live data; otherwise it falls back to realistic demo
data so the app always looks great during presentations.

Run:
    streamlit run dashboard/app.py
"""

import sys
import pathlib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Allow importing from the project root when running via `streamlit run`.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.analytics import (
    run_query,
    demo_revenue_summary,
    demo_monthly_revenue,
    demo_category_performance,
    demo_top_products,
    demo_order_status_funnel,
    demo_payment_analysis,
    demo_event_funnel,
    demo_repeat_customers,
    demo_revenue_by_state,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/online-store.png", width=72)
st.sidebar.title("🛒 E-Commerce Analytics")
st.sidebar.markdown("**Real-Time Data Platform**")
st.sidebar.divider()

use_live_db = st.sidebar.toggle("🔌 Use Live PostgreSQL", value=False)
st.sidebar.divider()
st.sidebar.markdown(
    """
**Phases Completed:**
- ✅ Phase 1 — Data Generation
- ✅ Phase 2 — PostgreSQL Warehouse
- ✅ Phase 3 — ETL Pipeline
- ✅ Phase 4 — Analytics SQL
- ✅ Phase 5 — Dashboard

**Stack:** Python · PostgreSQL · SQLAlchemy · Streamlit · Plotly
"""
)
st.sidebar.divider()
st.sidebar.caption("Built for portfolio & internship interviews 🚀")


# ---------------------------------------------------------------------------
# Data-loading helper (live DB or demo)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=120)
def _safe_kpi(is_live: bool = False) -> dict:
    """Fetch live KPI data, fall back to demo values on any error."""
    if is_live:
        try:
            df = run_query("revenue_summary.sql")
            return {
                "total_revenue":   float(df["total_revenue"].iloc[0]),
                "total_orders":    int(df["total_orders"].iloc[0]),
                "avg_order_value": float(df["avg_order_value"].iloc[0]),
            }
        except Exception:
            return demo_revenue_summary()
    return demo_revenue_summary()


@st.cache_data(ttl=120)
def load(sql_file: str, _demo_fn, is_live: bool = False):
    """Return live DB data when is_live is on, else call *_demo_fn*."""
    if is_live:
        try:
            return run_query(sql_file)
        except Exception as exc:
            st.warning(f"⚠️ Live query notice: {exc}. Displaying cached view.")
    return _demo_fn() if callable(_demo_fn) else _demo_fn


# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------
st.title("🛒 Real-Time E-Commerce Analytics Platform")
st.markdown(
    "An end-to-end data engineering portfolio project — data generation, "
    "ETL, PostgreSQL warehouse, and business intelligence."
)
st.divider()

# ===========================================================================
# SECTION 1 — KPI CARDS
# ===========================================================================
kpis = _safe_kpi(use_live_db)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue",    f"${kpis['total_revenue']:,.0f}")
col2.metric("📦 Total Orders",     f"{kpis['total_orders']:,}")
col3.metric("💳 Avg Order Value",  f"${kpis['avg_order_value']:,.2f}")
col4.metric("🛍️ Products",         "200")

st.divider()

# ===========================================================================
# SECTION 2 — REVENUE TRENDS
# ===========================================================================
st.subheader("📈 Monthly Revenue Trend")
monthly_df = load("monthly_revenue.sql", demo_monthly_revenue, use_live_db)
if "month" not in monthly_df.columns:
    if "order_year" in monthly_df.columns and "order_month" in monthly_df.columns:
        monthly_df["month"] = monthly_df["order_year"].astype(str) + "-" + monthly_df["order_month"].astype(str).str.zfill(2)

fig_rev = px.area(
    monthly_df,
    x="month",
    y="monthly_revenue",
    title="Monthly Revenue (Completed + Shipped Orders)",
    labels={"monthly_revenue": "Revenue ($)", "month": "Month"},
    color_discrete_sequence=["#636EFA"],
    markers=True,
)
fig_rev.update_layout(hovermode="x unified")
st.plotly_chart(fig_rev, use_container_width=True)

# ===========================================================================
# SECTION 3 — CATEGORY & PRODUCT PERFORMANCE
# ===========================================================================
st.subheader("🏷️ Product & Category Performance")
cat_col, prod_col = st.columns(2)

with cat_col:
    cat_df = load("category_performance.sql", demo_category_performance, use_live_db)
    fig_cat = px.bar(
        cat_df,
        x="category",
        y="total_revenue",
        color="category",
        title="Revenue by Category",
        labels={"total_revenue": "Revenue ($)"},
    )
    fig_cat.update_layout(showlegend=False)
    st.plotly_chart(fig_cat, use_container_width=True)

with prod_col:
    prod_df = load("top_products.sql", demo_top_products, use_live_db)
    fig_prod = px.bar(
        prod_df.head(10),
        x="total_revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Revenue",
        labels={"total_revenue": "Revenue ($)", "product_name": ""},
        color="total_revenue",
        color_continuous_scale="Blues",
    )
    fig_prod.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_prod, use_container_width=True)

# ===========================================================================
# SECTION 4 — ORDER FUNNEL & STATUS
# ===========================================================================
st.subheader("🔄 Order Status Funnel")
funnel_df = load("order_status_funnel.sql", demo_order_status_funnel, use_live_db)

f1, f2 = st.columns(2)

with f1:
    fig_funnel = px.funnel(
        funnel_df,
        x="order_count",
        y="order_status",
        title="Order Status Distribution (Funnel)",
        color="order_status",
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with f2:
    fig_pie = px.pie(
        funnel_df,
        names="order_status",
        values="order_count",
        title="Order Status Share (%)",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ===========================================================================
# SECTION 5 — CUSTOMER BEHAVIOUR
# ===========================================================================
st.subheader("👥 Customer Behaviour")
rep_col, evt_col = st.columns(2)

with rep_col:
    rep_df = load("repeat_customers.sql", demo_repeat_customers, use_live_db)
    fig_rep = px.pie(
        rep_df,
        names="repeat_flag",
        values="customer_count",
        title="Repeat vs One-Time Customers",
        color_discrete_sequence=["#00CC96", "#EF553B"],
        hole=0.4,
    )
    st.plotly_chart(fig_rep, use_container_width=True)

with evt_col:
    evt_df = load("event_funnel.sql", demo_event_funnel, use_live_db)
    fig_evt = px.bar(
        evt_df,
        x="event_type",
        y="event_count",
        color="event_type",
        title="Customer Event Funnel",
        labels={"event_count": "Events", "event_type": "Event"},
    )
    fig_evt.update_layout(showlegend=False)
    st.plotly_chart(fig_evt, use_container_width=True)

# ===========================================================================
# SECTION 6 — PAYMENT ANALYSIS
# ===========================================================================
st.subheader("💳 Payment Analysis")
pay_df = load("payment_analysis.sql", demo_payment_analysis, use_live_db)

pay_pivot = pay_df.pivot_table(
    index="payment_method",
    columns="payment_status",
    values="payment_count",
    aggfunc="sum",
    fill_value=0,
).reset_index()

fig_pay = px.bar(
    pay_df,
    x="payment_method",
    y="payment_count",
    color="payment_status",
    barmode="group",
    title="Payment Method vs Status",
    labels={"payment_count": "Transactions", "payment_method": "Method"},
)
st.plotly_chart(fig_pay, use_container_width=True)

# ===========================================================================
# SECTION 7 — GEOGRAPHIC REVENUE
# ===========================================================================
st.subheader("🗺️ Revenue by State")
geo_df = load("revenue_by_state.sql", demo_revenue_by_state, use_live_db)

fig_geo = px.bar(
    geo_df,
    x="state",
    y="total_revenue",
    color="total_revenue",
    color_continuous_scale="Viridis",
    title="Top States by Revenue",
    labels={"total_revenue": "Revenue ($)", "state": "State"},
)
fig_geo.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_geo, use_container_width=True)

# ===========================================================================
# SECTION 8 — RAW DATA EXPLORER
# ===========================================================================
st.subheader("🔍 Raw Data Explorer")
table_choice = st.selectbox(
    "Pick a dataset to preview:",
    ["Monthly Revenue", "Category Performance", "Top Products", "Order Funnel", "Payment Analysis"],
)
table_map = {
    "Monthly Revenue":       monthly_df,
    "Category Performance":  cat_df,
    "Top Products":          prod_df,
    "Order Funnel":          funnel_df,
    "Payment Analysis":      pay_df,
}
st.dataframe(table_map[table_choice], use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "🚀 Real-Time E-Commerce Data Engineering & Analytics Platform | "
    "Built with Python · PostgreSQL · SQLAlchemy · Streamlit · Plotly"
)
