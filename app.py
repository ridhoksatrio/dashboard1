import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# LOAD DATA
# ==========================================
st.set_page_config(page_title="Customer RFM Dashboard", layout="wide")
st.title("Customer Segmentation Dashboard")

uploaded = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    st.warning("Please upload your dataset first.")
    st.stop()

# ==========================================
# RFM CALCULATION
# ==========================================

def calculate_rfm(df):
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    max_date = df['InvoiceDate'].max()

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (max_date - x.max()).days,
        'InvoiceNo': 'count',
        'TotalAmount': 'sum'
    }).reset_index()

    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    rfm['AvgOrderValue'] = rfm['Monetary'] / rfm['Frequency']

    # RFM Score
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4]).astype(int)

    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

    # Simple segmentation
    rfm['Cluster_Label'] = pd.cut(rfm['RFM_Score'], bins=[0,4,8,12], labels=['Low Value','Mid Value','High Value'])

    return rfm

rfm = calculate_rfm(df)

# ==========================================
# CHART GENERATION
# ==========================================

def generate_all_charts(df):

    # Chart 1 – Recency distribution
    f1 = px.histogram(df, x='Recency', nbins=30, title='Recency Distribution')

    # Chart 2 – Frequency distribution
    f2 = px.histogram(df, x='Frequency', nbins=30, title='Frequency Distribution')

    # Chart 3 – Monetary distribution
    f3 = px.histogram(df, x='Monetary', nbins=30, title='Monetary Distribution')

    # Chart 4 – Average Order Value
    f4 = px.histogram(df, x='AvgOrderValue', nbins=30, title='Avg Order Value Distribution')

    # Chart 5 – RFM Score
    f5 = px.histogram(df, x='RFM_Score', nbins=12, title='RFM Score Distribution')

    # Chart 6 – Scatter Recency vs Monetary
    f6 = px.scatter(df, x='Recency', y='Monetary', color='Cluster_Label', title='Recency vs Monetary')

    # Chart 7 – Summary Table
    try:
        tb = df.groupby('Cluster_Label').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'AvgOrderValue': 'mean',
            'RFM_Score': 'mean'
        }).round(1).reset_index()

        tb['Count'] = df.groupby('Cluster_Label').size().values

        # Format Table
        f7 = go.Figure(data=[go.Table(
            header=dict(values=['Segment','Count','Recency','Frequency','Monetary','AvgOrderValue','RFM_Score'],
                        fill_color='#4C6EF5', font=dict(color='white', size=12), align='center'),
            cells=dict(values=[tb[col] for col in tb.columns], fill_color='white', align='center')
        )])

        f7.update_layout(title='RFM Segment Summary', height=400)

    except Exception as e:
        f7 = go.Figure()
        f7.update_layout(title=f"Error Creating Table: {str(e)}")

    return f1, f2, f3, f4, f5, f6, f7


# ==========================================
# DISPLAY ALL CHARTS
# ==========================================

st.subheader("RFM Charts")

f1, f2, f3, f4, f5, f6, f7 = generate_all_charts(rfm)

st.plotly_chart(f1, use_container_width=True)
st.plotly_chart(f2, use_container_width=True)
st.plotly_chart(f3, use_container_width=True)
st.plotly_chart(f4, use_container_width=True)
st.plotly_chart(f5, use_container_width=True)
st.plotly_chart(f6, use_container_width=True)
st.plotly_chart(f7, use_container_width=True)
