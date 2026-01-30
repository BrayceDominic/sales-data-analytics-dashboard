import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
import os
import time

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Sales Analytics Pro",
    layout="wide",
    page_icon="📊"
)

# =====================================================
# CUSTOM CSS
# =====================================================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(to right, #0e1117, #0e1117); }
    .kpi-card { background: linear-gradient(135deg, #1f2937, #374151); color:#fff; padding:25px 20px; border-radius:20px; box-shadow:0px 10px 25px rgba(0,0,0,0.3); text-align:center; transition:all 0.4s ease; }
    .kpi-card:hover { transform: translateY(-8px) scale(1.03); box-shadow:0px 15px 30px rgba(0,0,0,0.4); }
    .kpi-card h4 { font-weight:600; font-size:18px; display:flex; justify-content:center; align-items:center; gap:8px; }
    .kpi-card h2 { font-weight:700; font-size:28px; }
    .stButton>button { border-radius: 10px; background: linear-gradient(to right,#2563eb,#1d4ed8); color:white; padding:12px 25px; font-weight:600; transition: all 0.3s ease; }
    .stButton>button:hover { transform: scale(1.05); }
    .main-title { font-size:36px; font-weight:700; color:#ffffff; }
    .sub-title { color:#9ca3af; font-size:16px; }
    </style>
    """, unsafe_allow_html=True)
load_css()

# =====================================================
# PASSWORD HASH FUNCTIONS
# =====================================================
def hash_password(password: str) -> bytes:
    return bcrypt.gensalt(), bcrypt.hashpw(password.encode(), bcrypt.gensalt())
def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

# =====================================================
# SESSION STATE INIT
# =====================================================
if "users" not in st.session_state:
    st.session_state.users = {"admin": {"name": "Brayce Dominic", "password": hash_password("admin123")[1]}}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "landing"  # start at landing

# =====================================================
# LOGOUT FUNCTION
# =====================================================
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.page = "landing"

# =====================================================
# LANDING PAGE
# =====================================================
if st.session_state.page == "landing":
    st.markdown("<h1 style='text-align:center;color:white'>Welcome to Sales Analytics SaaS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#9ca3af'>Click below to access the dashboard (login required)</p>", unsafe_allow_html=True)
    if st.button("Go to Dashboard"):
        st.session_state.page = "dashboard"
    st.stop()

# =====================================================
# DASHBOARD LOGIN/REGISTER
# =====================================================
st.sidebar.header("Account")
st.sidebar.button("Logout", on_click=logout)

action = st.sidebar.radio("Select Action", ["Login", "Register"])

if not st.session_state.authenticated:
    if action == "Register":
        reg_name = st.sidebar.text_input("Full Name")
        reg_username = st.sidebar.text_input("Username")
        reg_password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            if reg_username in st.session_state.users:
                st.sidebar.error("Username exists")
            elif not reg_name or not reg_username or not reg_password:
                st.sidebar.warning("Fill all fields")
            else:
                st.session_state.users[reg_username] = {
                    "name": reg_name,
                    "password": hash_password(reg_password)[1]
                }
                st.sidebar.success(f"User {reg_username} registered! Please login.")

    if action == "Login":
        username_input = st.sidebar.text_input("Username")
        password_input = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if username_input in st.session_state.users:
                stored_hash = st.session_state.users[username_input]["password"]
                if verify_password(password_input, stored_hash):
                    st.session_state.authenticated = True
                    st.session_state.username = username_input
                    st.success(f"Welcome {st.session_state.users[username_input]['name']}!")
                else:
                    st.error("Invalid password")
            else:
                st.error("User not found")
    if not st.session_state.authenticated:
        st.stop()

# =====================================================
# USER-SPECIFIC CSV UPLOAD AND DASHBOARD
# =====================================================
UPLOAD_DIR = "users_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
user_csv_path = os.path.join(UPLOAD_DIR, f"{st.session_state.username}.csv")

if os.path.exists(user_csv_path):
    df = pd.read_csv(user_csv_path)
else:
    st.subheader("Upload Your Sales CSV")
    uploaded_file = st.file_uploader("Upload CSV (must match dashboard format)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv(user_csv_path, index=False)
        st.success("CSV loaded and saved successfully!")
    else:
        st.info("Please upload a CSV file to continue")
        st.stop()

# =====================================================
# DASHBOARD CONTENT (KPI, CHARTS, etc.)
# =====================================================
st.markdown(f"<h1 class='main-title'>Sales Analytics Dashboard</h1>", unsafe_allow_html=True)
st.divider()

years = df['Year'].unique().tolist()
regions = df['Region'].unique().tolist()
selected_year = st.sidebar.selectbox("Select Year", years)
selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

filtered_df = df[df['Year'] == selected_year]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

total_revenue = filtered_df['Revenue'].sum()
total_orders = filtered_df['OrderID'].nunique()
units_sold = filtered_df['Quantity'].sum()
avg_order = total_revenue / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)

dollar_svg = '<svg width="24" height="24" fill="currentColor"><path d="M8 1a3 3 0 0 1 3 3v1h1a2 2 0 0 1 0 4h-1v1a3 3 0 0 1-3 3 3 3 0 0 1-3-3v-1H4a2 2 0 0 1 0-4h1V4a3 3 0 0 1 3-3z"/></svg>'
box_svg = '<svg width="24" height="24" fill="currentColor"><path d="M2.5 2.5h11v11h-11v-11z"/></svg>'
cart_svg = '<svg width="24" height="24" fill="currentColor"><path d="M0 1h2l3 9h8l3-7H5L2 1z"/></svg>'
chart_svg = '<svg width="24" height="24" fill="currentColor"><path d="M0 10h2v6H0v-6zm4-4h2v10H4V6zm4-3h2v13H8V3zm4-2h2v15h-2V1z"/></svg>'

def kpi_card_svg(title, value, svg_icon):
    return f'<div class="kpi-card"><h4>{svg_icon}<span style="margin-left:8px">{title}</span></h4><h2>{value}</h2></div>'

col1.markdown(kpi_card_svg("Revenue (TZS)", f"{total_revenue:,.0f}", dollar_svg), unsafe_allow_html=True)
col2.markdown(kpi_card_svg("Orders", total_orders, box_svg), unsafe_allow_html=True)
col3.markdown(kpi_card_svg("Units Sold", units_sold, cart_svg), unsafe_allow_html=True)
col4.markdown(kpi_card_svg("Avg Order", f"{avg_order:,.0f}", chart_svg), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
st.subheader("Monthly Sales Trend")
fig1 = px.line(filtered_df.groupby("Month")['Revenue'].sum().reset_index(), x="Month", y="Revenue", markers=True)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Top Products")
fig2 = px.bar(filtered_df.groupby("Product")['Revenue'].sum().sort_values(ascending=False).head(10).reset_index(), x="Revenue", y="Product", orientation="h")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Regional Performance")
fig3 = px.pie(filtered_df.groupby("Region")['Revenue'].sum().reset_index(), names="Region", values="Revenue", hole=0.4)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(20), use_container_width=True)

st.markdown("---")
st.markdown(f"<center>Developed by <strong>{st.session_state.users[st.session_state.username]['name']}</strong> | SaaS Analytics Platform</center>", unsafe_allow_html=True)
