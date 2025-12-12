import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Customer Segmentation Dashboard", layout="wide")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_customer_segments (1).csv")
    except:
        st.error("CSV tidak ditemukan. Pastikan file bernama final_customer_segments.csv.")
        st.stop()

    required = [
        'Customer ID','Recency','Frequency','Monetary','AvgOrderValue',
        'TransaksiPerHari','TransactionRate','R_Score','F_Score','M_Score',
        'RFM_Score','RFM_Segment','Customer_Category',
        'Cluster_KMeans','Cluster_DBSCAN','Cluster_Agglomerative'
    ]

    for col in required:
        if col not in df.columns:
            df[col] = np.nan

    df['Cluster_KMeans'] = df['Cluster_KMeans'].fillna(-1).astype(int)
    df['Cluster_Label'] = df['Cluster_KMeans'].apply(lambda x: f"Cluster {x}")

    return df


df = load_data()

# =============================
# CHART GENERATOR
# =============================

def generate_all_charts(df):

    # Chart 1 - Recency
    f1 = px.histogram(df, x='Recency', nbins=30, title='Recency Distribution')

    # Chart 2 - Frequency
    f2 = px.histogram(df, x='Frequency', nbins=30, title='Frequency Distribution')

    # Chart 3 - Monetary
    f3 = px.histogram(df, x='Monetary', nbins=30, title='Monetary Distribution')

    # Chart 4 - Average Order Value
    f4 = px.histogram(df, x='AvgOrderValue', nbins=30, title='Average Order Value Distribution')

    # Chart 5 - Cluster Counts
    f5 = px.histogram(df, x='Cluster_Label', title='Cluster Distribution')

    # Chart 6 - RFM Score Distribution
    f6 = px.histogram(df, x='RFM_Score', nbins=20, title='RFM Score Distribution')

    # Chart 7 - Table Summary
    try:
        tb = df.groupby('Cluster_Label').agg({
            'Recency':'mean','Frequency':'mean','Monetary':'mean',
            'AvgOrderValue':'mean','RFM_Score':'mean', 'Cluster_Label':'count'
        }).round(1).reset_index()

        tb.columns = [
            'Segment','Recency','Frequency','Monetary','AvgOrderValue','RFM_Score','Count'
        ]

        f7 = go.Figure(data=[go.Table(
            header=dict(values=['<b>'+c+'</b>' for c in tb.columns], fill_color='#4c6ef5', align='center', font=dict(color='white', size=12)),
            cells=dict(values=[tb[c] for c in tb.columns], fill_color='white', align='center')
        )])
        f7.update_layout(title={'text':'📊 RFM Segment Summary','x':0.5}, height=420)

    except Exception as e:
        f7 = go.Figure()
        f7.add_annotation(text=f"Error: {e}", x=0.5, y=0.5)

    return f1, f2, f3, f4, f5, f6, f7


# =============================
# LAYOUT
# =============================

st.title("📊 Customer Segmentation Dashboard")
st.write("Visualisasi RFM, Clustering, dan Segmentasi Pelanggan.")

f1, f2, f3, f4, f5, f6, f7 = generate_all_charts(df)

st.subheader("Distribution Charts")
st.plotly_chart(f1, use_container_width=True)
st.plotly_chart(f2, use_container_width=True)
st.plotly_chart(f3, use_container_width=True)
st.plotly_chart(f4, use_container_width=True)
st.plotly_chart(f5, use_container_width=True)
st.plotly_chart(f6, use_container_width=True)

st.subheader("RFM Segment Summary Table")
st.plotly_chart(f7, use_container_width=True)
