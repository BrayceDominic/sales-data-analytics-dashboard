import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Sales Analytics Pro",
    layout="wide",
    page_icon="📊"
)

# ==============================
# CUSTOM CSS
# ==============================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: #0e1117;
    }

    .kpi-card {
        background: linear-gradient(135deg, #1f2937, #374151);
        color:#fff;
        padding:25px;
        border-radius:20px;
        box-shadow:0px 10px 25px rgba(0,0,0,0.3);
        text-align:center;
        transition:0.3s;
    }

    .kpi-card:hover {
        transform: translateY(-6px);
    }

    .main-title {
        font-size:36px;
        font-weight:700;
        color:#fff;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==============================
# TITLE
# ==============================
st.markdown("<h1 class='main-title'>Sales Analytics Dashboard</h1>", unsafe_allow_html=True)
st.divider()

# ==============================
# FILE UPLOAD
# ==============================
st.sidebar.header("Upload Data")

uploaded_file = st.sidebar.file_uploader("Upload Sales CSV", type=["csv"])

if not uploaded_file:
    st.info("📂 Please upload a CSV file to continue")
    st.stop()

df = pd.read_csv(uploaded_file)

# ==============================
# FILTERS
# ==============================
years = sorted(df["Year"].unique())
regions = sorted(df["Region"].unique())

selected_year = st.sidebar.selectbox("Select Year", years)
selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

filtered_df = df[df["Year"] == selected_year]

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

# ==============================
# KPIs
# ==============================
total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["OrderID"].nunique()
units_sold = filtered_df["Quantity"].sum()

avg_order = total_revenue / total_orders if total_orders else 0


def kpi(title, value):
    return f"""
    <div class="kpi-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """


c1, c2, c3, c4 = st.columns(4)

c1.markdown(kpi("Revenue (TZS)", f"{total_revenue:,.0f}"), unsafe_allow_html=True)
c2.markdown(kpi("Orders", total_orders), unsafe_allow_html=True)
c3.markdown(kpi("Units Sold", units_sold), unsafe_allow_html=True)
c4.markdown(kpi("Avg Order", f"{avg_order:,.0f}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# CHARTS
# ==============================
st.subheader("📈 Monthly Sales Trend")

monthly = filtered_df.groupby("Month")["Revenue"].sum().reset_index()

fig1 = px.line(
    monthly,
    x="Month",
    y="Revenue",
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)


st.subheader("🏆 Top Products")

top_products = (
    filtered_df
    .groupby("Product")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(
    top_products,
    x="Revenue",
    y="Product",
    orientation="h"
)

st.plotly_chart(fig2, use_container_width=True)


st.subheader("🌍 Regional Performance")

regional = (
    filtered_df
    .groupby("Region")["Revenue"]
    .sum()
    .reset_index()
)

fig3 = px.pie(
    regional,
    names="Region",
    values="Revenue",
    hole=0.4
)

st.plotly_chart(fig3, use_container_width=True)


# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📄 Dataset Preview")

st.dataframe(filtered_df.head(20), use_container_width=True)

# ==============================
# FOOTER
# ==============================
st.markdown("---")

st.markdown(
    "<center>Developed by <strong>Brayce Dominic</strong> | Sales Analytics Platform</center>",
    unsafe_allow_html=True
)
