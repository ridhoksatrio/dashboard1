import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# -----------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------
# DATA LOADING
# -----------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except:
        try:
            df = pd.read_csv('final_customer_segments.csv', index_col=0)
        except:
            st.error("Data tidak ditemukan, menggunakan data sample.")
            np.random.seed(42)
            n = 800
            df = pd.DataFrame({
                'Recency': np.random.randint(1, 365, n),
                'Frequency': np.random.randint(1, 50, n),
                'Monetary': np.random.uniform(100, 50000, n),
                'AvgOrderValue': np.random.uniform(50, 600, n),
                'RFM_Score': np.random.randint(100, 600, n),
                'Cluster_KMeans': np.random.choice([0,1,2,3,4,5], n)
            })
            df.index = [f'CUST_{i:04d}' for i in range(n)]
    return df

rfm = load_data()

# -----------------------------------------------------
# HEADER
# -----------------------------------------------------
st.markdown("""
<div style='text-align:center; padding:30px; background:linear-gradient(135deg,#667eea,#764ba2); border-radius:20px; color:white;'>
    <h1 style='font-size:48px; font-weight:900;'>Customer Intelligence Hub</h1>
    <p style='font-size:20px; opacity:0.9;'>Advanced RFM Segmentation Dashboard</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# TOP METRICS
# -----------------------------------------------------
st.subheader("📊 Customer Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{len(rfm):,}")
col2.metric("Avg Recency", f"{rfm['Recency'].mean():.1f} days")
col3.metric("Avg Frequency", f"{rfm['Frequency'].mean():.1f}")
col4.metric("Avg Monetary", f"${rfm['Monetary'].mean():.2f}")

# -----------------------------------------------------
# DISTRIBUTION CHARTS
# -----------------------------------------------------
st.subheader("📈 Customer Value Distributions")
colA, colB = st.columns(2)
colC, colD = st.columns(2)

# Recency distribution
with colA:
    fig_r = px.histogram(rfm, x='Recency', nbins=40, title='Recency Distribution')
    st.plotly_chart(fig_r, use_container_width=True)

# Frequency distribution
with colB:
    fig_f = px.histogram(rfm, x='Frequency', nbins=40, title='Frequency Distribution')
    st.plotly_chart(fig_f, use_container_width=True)

# Monetary distribution
with colC:
    fig_m = px.histogram(rfm, x='Monetary', nbins=40, title='Monetary Distribution')
    st.plotly_chart(fig_m, use_container_width=True)

# RFM Score distribution
with colD:
    fig_s = px.histogram(rfm, x='RFM_Score', nbins=40, title='RFM Score Distribution')
    st.plotly_chart(fig_s, use_container_width=True)

# -----------------------------------------------------
# CLUSTER DISTRIBUTION
# -----------------------------------------------------
st.subheader("🎯 Cluster Distribution")
fig_cluster = px.pie(
    rfm,
    names='Cluster_KMeans',
    title='Cluster Proportion',
    hole=0.4,
)
st.plotly_chart(fig_cluster, use_container_width=True)

# -----------------------------------------------------
# CLUSTER DETAIL TABLE
# -----------------------------------------------------
st.subheader("📋 Cluster Summary Table")
cluster_table = rfm.groupby('Cluster_KMeans').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean',
    'AvgOrderValue': 'mean',
    'RFM_Score': 'mean',
    'Cluster_KMeans': 'count'
}).rename(columns={'Cluster_KMeans': 'Count'}).round(2)
st.dataframe(cluster_table, use_container_width=True)

# -----------------------------------------------------
# RAW DATA TABLE
# -----------------------------------------------------
st.subheader("🧾 Full Customer Data")
st.dataframe(rfm, use_container_width=True)

"}]}
