import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Modern dengan Glassmorphism & Animasi
st.markdown("""
<style>
/* Reset & Base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Main Container dengan Glassmorphism */
.main-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 32px;
    padding: 40px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
    margin: 20px auto;
    max-width: 95%;
    border: 1px solid rgba(255, 255, 255, 0.2);
    animation: slideUp 0.8s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Header dengan Gradient Animasi */
.header-container {
    text-align: center;
    padding: 40px 30px;
    margin-bottom: 40px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
}

.header-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.4;
    animation: float 6s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

.title {
    font-size: 3.5rem;
    font-weight: 900;
    color: white;
    margin-bottom: 12px;
    text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    letter-spacing: -1px;
    position: relative;
    display: inline-block;
}

.title::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 25%;
    width: 50%;
    height: 4px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
    border-radius: 2px;
}

.subtitle {
    color: rgba(255, 255, 255, 0.95);
    font-size: 1.3rem;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Metrics Cards dengan Neumorphism */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 40px;
}

.metric-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 
        0 8px 32px rgba(31, 38, 135, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: 0.5s;
}

.metric-card:hover::before {
    left: 100%;
}

.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 
        0 20px 40px rgba(31, 38, 135, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.metric-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.metric-value {
    font-size: 2.8rem;
    font-weight: 800;
    color: #2d3748;
    margin: 10px 0;
    letter-spacing: -1px;
}

.metric-label {
    font-size: 0.95rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

.metric-trend {
    font-size: 0.85rem;
    color: #38a169;
    margin-top: 8px;
    font-weight: 500;
}

/* Filter Panel */
.filter-panel {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.filter-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 20px;
}

.filter-title i {
    font-size: 1.6rem;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    margin-bottom: 30px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.9);
    border: none;
    border-radius: 15px;
    padding: 15px 25px;
    font-weight: 600;
    font-size: 1rem;
    color: #667eea;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stTabs [data-baseweb="tab"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
    transition: 0.5s;
}

.stTabs [data-baseweb="tab"]:hover::before {
    left: 100%;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.1);
    transform: translateY(-2px);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3) !important;
}

/* Charts Container */
.charts-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
    margin-bottom: 30px;
}

.chart-card {
    background: white;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border: 1px solid rgba(102, 126, 234, 0.1);
    position: relative;
}

.chart-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px 0 0 20px;
}

.chart-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.chart-card-full {
    grid-column: 1 / -1;
}

/* Strategy Cards */
.strategy-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
    margin-bottom: 30px;
}

.strategy-card {
    border-radius: 20px;
    padding: 30px;
    color: white;
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.strategy-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.strategy-card:hover::before {
    opacity: 1;
}

.strategy-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
}

.strategy-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 8px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.strategy-subtitle {
    font-size: 1rem;
    opacity: 0.9;
    font-weight: 500;
}

.priority-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.tactics-container {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    backdrop-filter: blur(10px);
}

.tactic-item {
    padding: 12px 16px;
    margin: 8px 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    transition: all 0.3s ease;
    border-left: 4px solid rgba(255, 255, 255, 0.5);
    font-weight: 500;
}

.tactic-item:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateX(5px);
    border-left-width: 6px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin: 20px 0;
}

.kpi-item {
    background: rgba(255, 255, 255, 0.2);
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.kpi-item:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.05);
}

.budget-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    margin-top: 20px;
    backdrop-filter: blur(10px);
}

.budget-item {
    text-align: center;
    flex: 1;
}

.budget-label {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-bottom: 5px;
}

.budget-value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* Insights Section */
.insights-section {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 24px;
    padding: 40px;
    margin: 40px 0;
    color: white;
    box-shadow: 0 15px 40px rgba(79, 172, 254, 0.3);
    position: relative;
    overflow: hidden;
}

.insights-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.3;
}

.insights-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 30px;
    position: relative;
    display: inline-block;
}

.insights-title::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 0;
    width: 60px;
    height: 4px;
    background: white;
    border-radius: 2px;
}

.insights-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
}

.insight-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.insight-card:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-5px);
}

.insight-header {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.insight-list {
    list-style: none;
}

.insight-list li {
    padding: 12px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    font-weight: 500;
}

.insight-list li:last-child {
    border-bottom: none;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    margin-top: 50px;
    color: #718096;
    font-size: 0.95rem;
    font-weight: 500;
    border-top: 1px solid rgba(102, 126, 234, 0.2);
    position: relative;
}

.footer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 25%;
    width: 50%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .charts-container,
    .strategy-grid,
    .insights-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .main-container {
        padding: 20px;
    }
    
    .title {
        font-size: 2.5rem;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #764ba2, #667eea);
}
</style>
""", unsafe_allow_html=True)

# Load & Prepare Data
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except:
        try:
            rfm = pd.read_csv('final_customer_segments.csv', index_col=0)
        except:
            st.error("Data file not found. Using sample data for demonstration.")
            np.random.seed(42)
            n_samples = 1000
            rfm = pd.DataFrame({
                'Recency': np.random.randint(1, 365, n_samples),
                'Frequency': np.random.randint(1, 50, n_samples),
                'Monetary': np.random.uniform(100, 50000, n_samples),
                'AvgOrderValue': np.random.uniform(50, 500, n_samples),
                'RFM_Score': np.random.randint(100, 600, n_samples),
                'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5], n_samples, p=[0.2, 0.1, 0.15, 0.1, 0.25, 0.2])
            })
            rfm.index = [f'CUST_{i:04d}' for i in range(n_samples)]
    
    required_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score', 'Cluster_KMeans']
    for col in required_cols:
        if col not in rfm.columns:
            rfm[col] = 0
    
    return rfm

rfm = load_data()

# Cluster Strategies dengan warna yang DIPERBAIKI (semua dengan #)
strats = {
    'champions': {
        'name':'🏆 Champions',
        'grad':'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
        'color':'#FFD700',
        'priority':'CRITICAL',
        'strategy':'VIP Platinum Program',
        'tactics':['💎 Exclusive Early Access to New Products','🎁 Premium Gifts & Personalized Offers','📞 24/7 Dedicated Account Manager','🌟 VIP-Only Events & Experiences','✨ Celebration Rewards on Milestones'],
        'kpis':['Retention Rate > 95%','Upsell Conversion > 40%','Referral Rate > 30%'],
        'budget':'30%',
        'roi':'500%'
    },
    'loyal': {
        'name':'💎 Loyal Customers',
        'grad':'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'color':'#667eea',
        'priority':'HIGH',
        'strategy':'Loyalty Boosting Program',
        'tactics':['🎯 Tiered Rewards System with Exclusive Benefits','📱 Mobile App-Only Perks & Features','🎉 Personalized Birthday & Anniversary Offers','💝 Enhanced Referral Bonus Program','🔔 Early Access to Flash Sales'],
        'kpis':['Retention Rate > 85%','Purchase Frequency +20%','Net Promoter Score > 8'],
        'budget':'25%',
        'roi':'380%'
    },
    'big': {
        'name':'💰 Big Spenders',
        'grad':'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'color':'#f093fb',  # DIPERBAIKI: ditambahkan #
        'priority':'CRITICAL',
        'strategy':'Value Maximization Program',
        'tactics':['💳 Flexible Payment Terms & Financing Options','🎁 Luxury Gifts with High-Value Purchases','🚚 Free Express Shipping & Returns','📦 Custom Product Bundles & Packages','🌟 Personal Shopping Concierge Service'],
        'kpis':['Average Order Value +15%','Retention Rate > 90%','Satisfaction Score > 4.8/5'],
        'budget':'20%',
        'roi':'420%'
    },
    'dormant': {
        'name':'😴 Dormant Customers',
        'grad':'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
        'color':'#ff6b6b',  # DIPERBAIKI: ditambahkan #
        'priority':'URGENT',
        'strategy':'Win-Back Campaign',
        'tactics':['🎁 25-30% Discount on Next Purchase','📧 Multi-Channel Re-engagement Campaign','🎯 Personalized Retargeting Ads','💬 Personal Phone Call from Sales Team','⏰ Limited-Time Urgency Offers'],
        'kpis':['Win-Back Rate > 25%','Campaign Response Rate > 15%','ROI on Campaign > 200%'],
        'budget':'15%',
        'roi':'250%'
    },
    'potential': {
        'name':'🌱 High Potential',
        'grad':'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        'color':'#11998e',  # DIPERBAIKI: ditambahkan #
        'priority':'MEDIUM',
        'strategy':'Accelerated Conversion Program',
        'tactics':['🎓 Educational Content & Product Guides','🎁 15% Discount on Second Purchase','💌 Automated Welcome Email Sequence','📚 Video Tutorials & How-To Guides','🎯 Intelligent Cross-Sell Recommendations'],
        'kpis':['Conversion Rate > 35%','Second Purchase Within 30 Days','Lifetime Value +25%'],
        'budget':'5%',
        'roi':'180%'
    },
    'standard': {
        'name':'📊 Standard Customers',
        'grad':'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
        'color':'#89f7fe',  # DIPERBAIKI: ditambahkan #
        'priority':'MEDIUM',
        'strategy':'Steady Engagement Program',
        'tactics':['📧 Regular Newsletter with Valuable Content','🎯 Seasonal Promotions & Offers','💌 AI-Powered Product Recommendations','🎁 Surprise & Delight Mini-Gifts','📱 Community Building Activities'],
        'kpis':['Engagement Rate > 40%','Stable Purchase Behavior','Satisfaction Score > 3.5/5'],
        'budget':'5%',
        'roi':'150%'
    }
}

# Champion Sub-segments
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

def get_strat(cid, data):
    cd = data[data['Cluster_KMeans'] == cid]
    if len(cd) == 0:
        return {**strats['standard'], 'cluster_id': cid}
    
    r = cd['Recency'].mean() if 'Recency' in cd.columns else 100
    f = cd['Frequency'].mean() if 'Frequency' in cd.columns else 5
    m = cd['Monetary'].mean() if 'Monetary' in cd.columns else 500
    
    if pd.isna(r) or pd.isna(f) or pd.isna(m):
        s = 'standard'
    elif r < 50 and f > 10 and m > 1000: 
        s = 'champions'
    elif r < 50 and f > 5: 
        s = 'loyal'
    elif m > 1500: 
        s = 'big'
    elif r > 100: 
        s = 'dormant'
    elif r < 50 and f < 5: 
        s = 'potential'
    else: 
        s = 'standard'
    return {**strats[s], 'cluster_id': cid}

@st.cache_data
def init_data(rfm):
    profs = {}
    for c in rfm['Cluster_KMeans'].unique():
        p = get_strat(c, rfm)
        profs[c] = p
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name']} (C{c})"
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']
    
    colors = {}
    for c, p in profs.items():
        label = f"{p['name']} (C{c})"
        colors[label] = p['color']
    
    return profs, colors, rfm

profs, colors, rfm = init_data(rfm)

# Fungsi untuk membuat chart yang lebih baik dan AMAN
def create_charts(df):
    charts = []
    
    # Chart 1: Customer Distribution (Donut)
    if 'Cluster_Label' in df.columns:
        cc = df['Cluster_Label'].value_counts()
        
        if not cc.empty:
            fig1 = go.Figure(go.Pie(
                labels=cc.index, 
                values=cc.values, 
                hole=0.6,
                marker=dict(
                    colors=[colors.get(l, '#95A5A6') for l in cc.index],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textposition='outside',
                pull=[0.1 if 'Champions' in str(l) else 0 for l in cc.index]
            ))
            
            fig1.update_layout(
                title=dict(
                    text="🎯 Customer Distribution by Segment",
                    font=dict(size=18, color='#2d3748'),
                    x=0.5
                ),
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            charts.append(fig1)
        else:
            charts.append(go.Figure())
    else:
        charts.append(go.Figure())
    
    # Chart 2: Revenue by Segment (Horizontal Bar)
    if 'Monetary' in df.columns and 'Cluster_Label' in df.columns:
        try:
            rv = df.groupby('Cluster_Label')['Monetary'].sum()
            if not rv.empty:
                rv = rv.sort_values(ascending=True)
                
                # Pastikan semua warna valid
                color_list = []
                for l in rv.index:
                    color_val = colors.get(l, '#667eea')
                    # Pastikan format warna benar
                    if not color_val.startswith('#'):
                        color_val = '#' + color_val
                    color_list.append(color_val)
                
                fig2 = go.Figure(go.Bar(
                    x=rv.values, 
                    y=rv.index, 
                    orientation='h',
                    marker=dict(
                        color=color_list,
                        line=dict(color='white', width=1)
                    ),
                    text=[f'£{v/1000:.1f}K' for v in rv.values],
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>'
                ))
                
                fig2.update_layout(
                    title=dict(
                        text="💰 Revenue Contribution by Segment",
                        font=dict(size=18, color='#2d3748'),
                        x=0.5
                    ),
                    xaxis_title="Total Revenue (£)",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=50, b=20, l=150, r=20)
                )
                charts.append(fig2)
            else:
                charts.append(go.Figure())
        except:
            charts.append(go.Figure())
    else:
        charts.append(go.Figure())
    
    # Chart 3: RFM Score Distribution by Cluster
    if 'RFM_Score' in df.columns and 'Cluster_Label' in df.columns:
        try:
            fig3 = go.Figure()
            clusters = df['Cluster_Label'].unique()[:6]  # Batasi maksimal 6 cluster
            
            for cluster in clusters:
                cluster_data = df[df['Cluster_Label'] == cluster]['RFM_Score']
                if not cluster_data.empty:
                    color_val = colors.get(cluster, '#667eea')
                    if not color_val.startswith('#'):
                        color_val = '#' + color_val
                    
                    fig3.add_trace(go.Box(
                        y=cluster_data,
                        name=cluster[:20],  # Batasi panjang nama
                        marker_color=color_val,
                        boxpoints='outliers',
                        jitter=0.3,
                        pointpos=-1.8
                    ))
            
            if len(fig3.data) > 0:
                fig3.update_layout(
                    title=dict(
                        text="📊 RFM Score Distribution by Segment",
                        font=dict(size=18, color='#2d3748'),
                        x=0.5
                    ),
                    yaxis_title="RFM Score",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=True
                )
                charts.append(fig3)
            else:
                charts.append(go.Figure())
        except:
            charts.append(go.Figure())
    else:
        charts.append(go.Figure())
    
    # Chart 4: Recency vs Monetary Scatter
    if all(col in df.columns for col in ['Recency', 'Monetary', 'Cluster_Label']):
        try:
            fig4 = go.Figure()
            clusters = df['Cluster_Label'].unique()[:8]  # Batasi jumlah cluster
            
            for cluster in clusters:
                cluster_data = df[df['Cluster_Label'] == cluster]
                if len(cluster_data) > 0:
                    color_val = colors.get(cluster, '#667eea')
                    if not color_val.startswith('#'):
                        color_val = '#' + color_val
                    
                    fig4.add_trace(go.Scatter(
                        x=cluster_data['Recency'],
                        y=cluster_data['Monetary'],
                        mode='markers',
                        name=cluster[:15],  # Batasi panjang nama
                        marker=dict(
                            size=8,
                            color=color_val,
                            opacity=0.7,
                            line=dict(width=1, color='white')
                        ),
                        hovertemplate='<b>%{text}</b><br>Recency: %{x} days<br>Spent: £%{y:,.0f}<extra></extra>',
                        text=cluster_data.index
                    ))
            
            if len(fig4.data) > 0:
                fig4.update_layout(
                    title=dict(
                        text="📈 Recency vs Monetary Value",
                        font=dict(size=18, color='#2d3748'),
                        x=0.5
                    ),
                    xaxis_title="Recency (Days Since Last Purchase)",
                    yaxis_title="Total Monetary Value (£)",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5
                    )
                )
                charts.append(fig4)
            else:
                charts.append(go.Figure())
        except:
            charts.append(go.Figure())
    else:
        charts.append(go.Figure())
    
    # Chart 5: Segment Metrics Heatmap
    if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary', 'Cluster_Label']):
        try:
            segment_metrics = df.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean'
            }).round(1)
            
            if not segment_metrics.empty:
                # Normalize for heatmap
                normalized = (segment_metrics - segment_metrics.min()) / (segment_metrics.max() - segment_metrics.min())
                
                fig5 = go.Figure(go.Heatmap(
                    z=normalized.values,
                    x=['Recency', 'Frequency', 'Monetary'],
                    y=normalized.index,
                    colorscale='Viridis',
                    hoverongaps=False,
                    hovertemplate='<b>%{y}</b><br>%{x}: %{customdata}<extra></extra>',
                    customdata=segment_metrics.values
                ))
                
                fig5.update_layout(
                    title=dict(
                        text="🔥 Segment Performance Heatmap",
                        font=dict(size=18, color='#2d3748'),
                        x=0.5
                    ),
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                charts.append(fig5)
            else:
                charts.append(go.Figure())
        except:
            charts.append(go.Figure())
    else:
        charts.append(go.Figure())
    
    # Jika ada chart yang kosong, tambahkan chart kosong
    while len(charts) < 5:
        charts.append(go.Figure())
    
    return charts[0], charts[1], charts[2], charts[3], charts[4]

# Layout utama
def main():
    # Container utama
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="title">🎯 Customer Intelligence Hub</h1>
        <p class="subtitle">AI-Powered Customer Segmentation & Personalized Marketing Strategies</p>
        <div style="margin-top: 20px; font-size: 1rem; opacity: 0.9;">
            📊 Real-time Analytics • 🎯 Personalized Strategies • 💡 Actionable Insights
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{len(rfm):,}</div>
            <div class="metric-label">Total Customers</div>
            <div class="metric-trend">↗️ 12% growth</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        segments = rfm['Cluster_KMeans'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">{segments}</div>
            <div class="metric-label">AI Segments</div>
            <div class="metric-trend">🤖 ML optimized</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
        avg_rev = rfm['Monetary'].mean() if 'Monetary' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">£{total_rev/1e6:.1f}M</div>
            <div class="metric-label">Total Revenue</div>
            <div class="metric-trend">📈 £{avg_rev:.0f} avg/customer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        champion_count = len(rfm[rfm['Cluster_Label'].str.contains('Champions', na=False)]) if 'Cluster_Label' in rfm.columns else 0
        champion_pct = (champion_count / len(rfm) * 100) if len(rfm) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">{champion_count:,}</div>
            <div class="metric-label">Champions</div>
            <div class="metric-trend">⭐ {champion_pct:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filters
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">🎛️ Advanced Filters</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        segment_options = [('🌐 All Segments', 'all')]
        for c, p in profs.items():
            if p['name'] == '🏆 Champions' and c in champion_details:
                label = f"{p['name']} - {champion_details[c]['tier']}"
            else:
                label = p['name']
            segment_options.append((label, c))
        
        segment_filter = st.selectbox(
            "🎨 Customer Segment",
            options=[opt[1] for opt in segment_options],
            format_func=lambda x: next((opt[0] for opt in segment_options if opt[1] == x), x),
            index=0
        )
    
    with col2:
        if 'RFM_Score' in rfm.columns:
            rfm_min = int(rfm['RFM_Score'].min())
            rfm_max = int(rfm['RFM_Score'].max())
            rfm_filter = st.slider(
                "📊 RFM Score Range",
                min_value=rfm_min,
                max_value=rfm_max,
                value=[rfm_min, rfm_max]
            )
        else:
            rfm_filter = [0, 100]
    
    with col3:
        priority_options = [
            ('🌐 All Priorities', 'all'),
            ('🔴 CRITICAL', 'CRITICAL'),
            ('🔥 URGENT', 'URGENT'),
            ('⚡ HIGH', 'HIGH'),
            ('📊 MEDIUM', 'MEDIUM')
        ]
        priority_filter = st.selectbox(
            "🎯 Priority Level",
            options=[opt[1] for opt in priority_options],
            format_func=lambda x: next((opt[0] for opt in priority_options if opt[1] == x), x),
            index=0
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = rfm.copy()
    
    if 'RFM_Score' in rfm.columns:
        filtered_df = filtered_df[
            (filtered_df['RFM_Score'] >= rfm_filter[0]) & 
            (filtered_df['RFM_Score'] <= rfm_filter[1])
        ]
    
    if segment_filter != 'all':
        filtered_df = filtered_df[filtered_df['Cluster_KMeans'] == segment_filter]
    
    if priority_filter != 'all' and 'Priority' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts
            fig1, fig2, fig3, fig4, fig5 = create_charts(filtered_df)
            
            # Row 1: Two charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 2: RFM Distribution
            st.markdown('<div class="chart-card chart-card-full">', unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 3: Scatter and Heatmap
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No data available for the selected filters.")
    
    with tab2:
        # Strategy Cards
        strategy_html = ""
        for cid, p in profs.items():
            if segment_filter == 'all' or segment_filter == cid:
                # Build tactics HTML
                tactics_html = "".join([f'<div class="tactic-item">{tactic}</div>' for tactic in p['tactics']])
                
                # Build KPIs HTML
                kpis_html = "".join([f'<div class="kpi-item">{kpi}</div>' for kpi in p['kpis']])
                
                strategy_html += f"""
                <div class="strategy-card" style="background: {p['grad']}">
                    <div class="strategy-header">
                        <div>
                            <div class="strategy-title">{p['name']}</div>
                            <div class="strategy-subtitle">{p['strategy']}</div>
                        </div>
                        <div class="priority-badge">{p['priority']}</div>
                    </div>
                    
                    <div class="tactics-container">
                        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 15px;">🎯 Key Tactics</div>
                        {tactics_html}
                    </div>
                    
                    <div class="tactics-container">
                        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 15px;">📊 Target KPIs</div>
                        <div class="kpi-grid">
                            {kpis_html}
                        </div>
                    </div>
                    
                    <div class="budget-display">
                        <div class="budget-item">
                            <div class="budget-label">Budget Allocation</div>
                            <div class="budget-value">{p['budget']}</div>
                        </div>
                        <div class="budget-item">
                            <div class="budget-label">Expected ROI</div>
                            <div class="budget-value">{p['roi']}</div>
                        </div>
                        <div class="budget-item">
                            <div class="budget-label">Customers</div>
                            <div class="budget-value">{len(filtered_df[filtered_df['Cluster_KMeans'] == cid]):,}</div>
                        </div>
                    </div>
                </div>
                """
        
        if strategy_html:
            st.markdown(f'<div class="strategy-grid">{strategy_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Select a specific segment to view detailed strategy.")
    
    with tab3:
        if len(filtered_df) > 0:
            # Calculate insights
            insights = []
            
            # Revenue-based insights
            if 'Monetary' in filtered_df.columns:
                revenue_by_segment = filtered_df.groupby('Cluster_Label')['Monetary'].sum()
                if not revenue_by_segment.empty:
                    top_revenue_segment = revenue_by_segment.idxmax()
                    top_revenue_value = revenue_by_segment.max()
                    insights.append(f"💰 **{top_revenue_segment}** generates the highest revenue (£{top_revenue_value/1000:.1f}K)")
            
            # Customer count insights
            if 'Cluster_Label' in filtered_df.columns:
                segment_counts = filtered_df['Cluster_Label'].value_counts()
                if not segment_counts.empty:
                    largest_segment = segment_counts.idxmax()
                    insights.append(f"👥 **{largest_segment}** is the largest segment ({segment_counts.max():,} customers)")
            
            # AOV insights
            if 'AvgOrderValue' in filtered_df.columns and 'Cluster_Label' in filtered_df.columns:
                aov_by_segment = filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean()
                if not aov_by_segment.empty:
                    highest_aov_segment = aov_by_segment.idxmax()
                    highest_aov_value = aov_by_segment.max()
                    insights.append(f"💳 **{highest_aov_segment}** has the highest average order value (£{highest_aov_value:.0f})")
            
            # Recency insights
            if 'Recency' in filtered_df.columns and 'Cluster_Label' in filtered_df.columns:
                recency_by_segment = filtered_df.groupby('Cluster_Label')['Recency'].mean()
                if not recency_by_segment.empty:
                    most_recent_segment = recency_by_segment.idxmin()
                    most_recent_value = recency_by_segment.min()
                    insights.append(f"🕐 **{most_recent_segment}** customers are most active ({most_recent_value:.0f} days since last purchase)")
            
            # Champion insights
            if 'Cluster_Label' in filtered_df.columns and 'Monetary' in filtered_df.columns:
                champion_segments = [s for s in filtered_df['Cluster_Label'].unique() if isinstance(s, str) and 'Champions' in s]
                if champion_segments:
                    champion_count = len(filtered_df[filtered_df['Cluster_Label'].str.contains('Champions', na=False)])
                    champion_revenue = filtered_df[filtered_df['Cluster_Label'].str.contains('Champions', na=False)]['Monetary'].sum()
                    total_revenue = filtered_df['Monetary'].sum() if filtered_df['Monetary'].sum() > 0 else 1
                    champion_percent = (champion_revenue / total_revenue * 100)
                    insights.append(f"🏆 **Champions** ({champion_count} customers) drive {champion_percent:.1f}% of total revenue")
            
            # Recommendations
            recommendations = [
                "🎯 **Prioritize retention programs** for high-value segments to maximize ROI",
                "📧 **Launch personalized campaigns** based on segment characteristics",
                "🚀 **Implement win-back strategies** for dormant customers to recover lost revenue",
                "💎 **Create VIP experiences** for champion segments to enhance loyalty",
                "📊 **Monitor segment performance** monthly and adjust strategies accordingly",
                "🤝 **Develop referral programs** leveraging loyal customers as brand advocates",
                "📱 **Optimize mobile experience** for tech-savvy segments",
                "🎁 **Personalize rewards** based on individual customer preferences"
            ]
            
            # Build insights HTML
            insights_html = f"""
            <div class="insights-section">
                <h2 class="insights-title">🧠 AI-Powered Insights & Recommendations</h2>
                
                <div class="insights-grid">
                    <div class="insight-card">
                        <div class="insight-header">📈 Key Findings</div>
                        <ul class="insight-list">
                            {''.join([f'<li>{insight}</li>' for insight in insights[:4]]) if insights else '<li>No insights available for selected filters</li>'}
                        </ul>
                    </div>
                    
                    <div class="insight-card">
                        <div class="insight-header">💡 Strategic Recommendations</div>
                        <ul class="insight-list">
                            {''.join([f'<li>{recommendation}</li>' for recommendation in recommendations[:4]])}
                        </ul>
                    </div>
                </div>
            </div>
            """
            
            st.markdown(insights_html, unsafe_allow_html=True)
        else:
            st.info("No insights available for the selected filters.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 10px;">
            🎯 Customer Intelligence Hub v3.0 • Powered by Advanced AI Segmentation
        </div>
        <div style="font-size: 0.85rem; opacity: 0.8;">
            Data Updated: {date} • Real-time Analytics Dashboard
        </div>
    </div>
    """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
