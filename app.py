import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px;
        padding: 32px 40px;
        margin-bottom: 36px;
        text-align: center;
        color: white;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.35);
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 10px;
        text-shadow: 4px 4px 8px rgba(0,0,0,.35);
        letter-spacing: -1.5px;
    }
    
    .header-subtitle {
        font-size: 1.35rem;
        opacity: 0.95;
        font-weight: 500;
    }
    
    /* Metrics Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.45);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
    }
    
    .metric-icon {
        font-size: 2.8rem;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 10px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,.25);
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .metric-sub {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Filter Section */
    .filter-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 32px;
        box-shadow: 0 10px 30px rgba(0,0,0,.12);
    }
    
    /* Strategy Cards */
    .strategy-card {
        border-radius: 20px;
        padding: 30px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 15px 40px rgba(0,0,0,.22);
        transition: all 0.4s ease;
    }
    
    .strategy-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 50px rgba(0,0,0,.32);
    }
    
    .strategy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .strategy-name {
        font-size: 1.8rem;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,.2);
    }
    
    .priority-badge {
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        background: rgba(255,255,255,.25);
        backdrop-filter: blur(10px);
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 35px rgba(0,0,0,.08);
        margin-bottom: 25px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        border-color: #667eea;
        box-shadow: 0 15px 45px rgba(0,0,0,.15);
    }
    
    /* Champion Breakdown */
    .champion-breakdown {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 20px;
        padding: 30px;
        color: white;
        margin: 26px 0;
        box-shadow: 0 15px 40px rgba(255,215,0,.4);
    }
    
    /* Insights Section */
    .insights-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 20px;
        padding: 30px;
        color: white;
        margin: 26px 0;
        box-shadow: 0 15px 40px rgba(79,172,254,.4);
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
            st.error("File data tidak ditemukan. Pastikan 'final_customer_segments.csv' ada di direktori yang sama.")
            return None
    return rfm

rfm = load_data()
if rfm is None:
    st.stop()

# Cluster Strategies
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# Champion Sub-segments Explanation
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

def get_strat(cid, data):
    cd = data[data['Cluster_KMeans'] == cid]
    r = cd['Recency'].mean()
    f = cd['Frequency'].mean()
    m = cd['Monetary'].mean()
    
    if r < 50 and f > 10 and m > 1000:
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

# Preprocess data
profs = {}
for c in rfm['Cluster_KMeans'].unique():
    p = get_strat(c, rfm)
    profs[c] = p
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']

colors = {f"{p['name'][:2]} {p['name'][2:]} (C{c})": p['color'] for c, p in profs.items()}

# Header
st.markdown('<div class="header-container"><h1 class="header-title">🎯 Customer Intelligence Hub</h1><p class="header-subtitle">Customer Segmentation for Personalized Retail Marketing</p></div>', unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{len(rfm):,}</div>
        <div class="metric-label">Customers</div>
        <div class="metric-sub">Active Database</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🎯</div>
        <div class="metric-value">{rfm['Cluster_KMeans'].nunique()}</div>
        <div class="metric-label">Segments</div>
        <div class="metric-sub">AI-Classified</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-value">£{rfm['Monetary'].sum()/1e6:.2f}M</div>
        <div class="metric-label">Revenue</div>
        <div class="metric-sub">Avg £{rfm['Monetary'].mean():.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">£{rfm['AvgOrderValue'].mean():.0f}</div>
        <div class="metric-label">Avg Order</div>
        <div class="metric-sub">Peak £{rfm['AvgOrderValue'].max():.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# Filter Section
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #2c3e50; margin-bottom: 22px;">🎛️ Smart Filters</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

st.markdown('<div class="filter-container">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #2c3e50; margin-bottom: 22px;">🎛️ Smart Filters</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Buat opsi untuk filter cluster
    segment_choices = ['🌐 All Segments']
    segment_values = ['all']
    
    for cluster_id, profile in profs.items():
        if profile['name'] == '🏆 Champions' and cluster_id in champion_details:
            display_name = f"{profile['name']} - {champion_details[cluster_id]['tier']}"
        else:
            display_name = profile['name']
        
        segment_choices.append(display_name)
        segment_values.append(str(cluster_id))
    
    selected_segment_index = st.selectbox(
        "🎨 Segment Filter",
        options=range(len(segment_choices)),
        format_func=lambda x: segment_choices[x],
        index=0
    )
    
    selected_cluster = segment_values[selected_segment_index]

with col2:
    min_score, max_score = st.slider(
        "📊 RFM Score Range",
        min_value=int(rfm['RFM_Score'].min()),
        max_value=int(rfm['RFM_Score'].max()),
        value=(int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())),
        step=1
    )

with col3:
    priority_choices = ['🌐 All Priorities', '🔴 CRITICAL', '🔥 URGENT', '⚡ HIGH', '📊 MEDIUM']
    priority_values = ['all', 'CRITICAL', 'URGENT', 'HIGH', 'MEDIUM']
    
    selected_priority_index = st.selectbox(
        "🔥 Priority Level",
        options=range(len(priority_choices)),
        format_func=lambda x: priority_choices[x],
        index=0
    )
    
    selected_priority_value = priority_values[selected_priority_index]

st.markdown('</div>', unsafe_allow_html=True)

# Filter data based on selections
filtered_df = rfm[(rfm['RFM_Score'] >= min_score) & (rfm['RFM_Score'] <= max_score)]

if selected_cluster != 'all':
    filtered_df = filtered_df[filtered_df['Cluster_KMeans'] == selected_cluster]

if selected_priority_value != 'all':
    filtered_df = filtered_df[filtered_df['Priority'] == selected_priority_value]

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])

with tab1:
    # Row 1: Pie chart and Bar chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Customer Distribution Pie
        cluster_counts = filtered_df['Cluster_Label'].value_counts()
        fig1 = go.Figure(go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=.68,
            marker=dict(
                colors=[colors.get(label, '#95A5A6') for label in cluster_counts.index],
                line=dict(color='white', width=5)
            ),
            textfont=dict(size=14, family='Inter, Poppins', weight=700),
            textposition='outside',
            pull=[0.05] * len(cluster_counts)
        ))
        
        fig1.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x': 0.5, 'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=420,
            annotations=[dict(
                text=f'<b>{len(filtered_df):,}</b><br><span style="font-size:14px">Customers</span>',
                x=0.5, y=0.5, font={'size': 24, 'color': '#667eea', 'family': 'Inter, Poppins'}, showarrow=False
            )],
            margin=dict(t=80, b=40, l=40, r=40)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Chart 2: Revenue by Segment
        revenue_by_segment = filtered_df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
        fig2 = go.Figure(go.Bar(
            x=revenue_by_segment.values,
            y=revenue_by_segment.index,
            orientation='h',
            marker=dict(
                color=revenue_by_segment.values,
                colorscale='Sunset',
                line=dict(color='white', width=3)
            ),
            text=[f'£{v/1000:.1f}K' for v in revenue_by_segment.values],
            textposition='outside',
            textfont={'size': 13, 'weight': 700, 'family': 'Inter, Poppins'}
        ))
        
        fig2.update_layout(
            title={'text': "<b>💰 Revenue by Segment</b>", 'x': 0.5, 'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            xaxis={'title': '<b>Revenue (£)</b>', 'titlefont': {'size': 14, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            yaxis={'titlefont': {'size': 14, 'family': 'Inter, Poppins'}},
            height=420,
            plot_bgcolor='rgba(245,247,250,.6)',
            margin=dict(t=80, b=60, l=140, r=60)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Chart 3: 3D RFM Analysis
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig3 = go.Figure(go.Scatter3d(
        x=filtered_df['Recency'],
        y=filtered_df['Frequency'],
        z=filtered_df['Monetary'],
        mode='markers',
        marker=dict(
            size=7,
            color=filtered_df['Cluster_KMeans'],
            colorscale='Rainbow',
            showscale=True,
            line=dict(width=.8, color='white'),
            opacity=.88,
            colorbar=dict(title='Cluster', thickness=20, len=0.7)
        ),
        text=filtered_df['Cluster_Label'],
        hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'
    ))
    
    fig3.update_layout(
        title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': 0.5, 'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
        height=650,
        scene=dict(
            xaxis=dict(title='<b>Recency (days)</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
            yaxis=dict(title='<b>Frequency</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
            zaxis=dict(title='<b>Monetary (£)</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        paper_bgcolor='rgba(245,247,250,.4)',
        margin=dict(t=80, b=40, l=40, r=40)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 4: Histograms
    col4, col5, col6 = st.columns(3)
    
    with col4:
        # Chart 4: Recency Distribution
        fig4 = go.Figure(go.Histogram(
            x=filtered_df['Recency'],
            nbinsx=35,
            marker=dict(color='#ff6b6b', line=dict(color='white', width=2), opacity=.85)
        ))
        fig4.update_layout(
            title={'text': "<b>⏰ Recency Distribution</b>", 'x': 0.5, 'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            xaxis={'title': '<b>Recency</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            yaxis={'title': '<b>Count</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)',
            margin=dict(t=70, b=50, l=60, r=40)
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with col5:
        # Chart 5: Frequency Distribution
        fig5 = go.Figure(go.Histogram(
            x=filtered_df['Frequency'],
            nbinsx=35,
            marker=dict(color='#4ecdc4', line=dict(color='white', width=2), opacity=.85)
        ))
        fig5.update_layout(
            title={'text': "<b>🔄 Frequency Distribution</b>", 'x': 0.5, 'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            xaxis={'title': '<b>Frequency</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            yaxis={'title': '<b>Count</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)',
            margin=dict(t=70, b=50, l=60, r=40)
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    with col6:
        # Chart 6: Monetary Distribution
        fig6 = go.Figure(go.Histogram(
            x=filtered_df['Monetary'],
            nbinsx=35,
            marker=dict(color='#45b7d1', line=dict(color='white', width=2), opacity=.85)
        ))
        fig6.update_layout(
            title={'text': "<b>💵 Monetary Distribution</b>", 'x': 0.5, 'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            xaxis={'title': '<b>Monetary (£)</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            yaxis={'title': '<b>Count</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 'gridcolor': 'rgba(0,0,0,0.05)'},
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)',
            margin=dict(t=70, b=50, l=60, r=40)
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    # Chart 7: Segment Summary Table
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    table_data = filtered_df.groupby('Cluster_Label').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean',
        'AvgOrderValue': 'mean',
        'RFM_Score': 'mean'
    }).round(1).reset_index()
    
    table_data['Count'] = filtered_df.groupby('Cluster_Label').size().values
    
    fig7 = go.Figure(go.Table(
        header=dict(
            values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                   '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
            fill_color='#667eea',
            font=dict(color='white', size=13, family='Inter, Poppins'),
            align='center',
            height=42,
            line=dict(color='white', width=2)
        ),
        cells=dict(
            values=[
                table_data['Cluster_Label'],
                table_data['Count'],
                [f"{v:.0f}d" for v in table_data['Recency']],
                table_data['Frequency'].round(1),
                [f"£{v:,.0f}" for v in table_data['Monetary']],
                [f"£{v:.0f}" for v in table_data['AvgOrderValue']],
                table_data['RFM_Score']
            ],
            fill_color=[['white', '#f8f9fc'] * len(table_data)],
            align='center',
            font={'size': 12, 'family': 'Inter, Poppins'},
            height=38,
            line=dict(color='#e0e0e0', width=1)
        )
    ))
    
    fig7.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig7, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # Champion Breakdown Section
    champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() if profs[c]['name'] == '🏆 Champions']
    
    if len(champion_clusters) > 0:
        st.markdown('<div class="champion-breakdown">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; margin-bottom: 20px;">🏆 Champion Segments Breakdown</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.1rem; margin-bottom: 24px;">Understanding the Different Champion Tiers</p>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        col_idx = 0
        
        for cid in sorted(champion_clusters):
            if cid in champion_details:
                det = champion_details[cid]
                with cols[col_idx % 2]:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,.16); border-radius: 16px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: 900; margin-bottom: 8px;">Champion C{cid}</div>
                        <div style="font-size: 1.3rem; font-weight: 800; margin-bottom: 12px;">🏅 {det['tier']}</div>
                        <div style="font-size: 1.05rem; margin-bottom: 12px; line-height: 1.5;">{det['desc']}</div>
                        <div style="font-size: 0.95rem; background: rgba(255,255,255,.2); padding: 10px; border-radius: 8px; font-weight: 600;">
                            📊 Characteristics: {det['char']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                col_idx += 1
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Strategy Cards
    st.markdown('<h2 style="color: #2c3e50; margin-bottom: 24px;">🎯 Growth Strategies</h2>', unsafe_allow_html=True)
    
    if selected_cluster == 'all':
        clusters_to_show = profs.keys()
    else:
        clusters_to_show = [selected_cluster]
    
    for cid in clusters_to_show:
        p = profs[cid]
        st.markdown(f"""
        <div class="strategy-card" style="background: {p['grad']};">
            <div class="strategy-header">
                <div class="strategy-name">{p['name']}</div>
                <div class="priority-badge">{p['priority']}</div>
            </div>
            <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 20px;">📋 {p['strategy']} Strategy</div>
            
            <div style="background: rgba(255,255,255,.12); border-radius: 16px; padding: 20px; margin: 20px 0;">
                <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 14px;">🎯 Key Tactics</div>
                {''.join([f'<div style="padding: 14px 18px; margin: 10px 0; background: rgba(255,255,255,.18); border-radius: 12px; border-left: 4px solid rgba(255,255,255,.45); font-weight: 600;">{tactic}</div>' for tactic in p['tactics']])}
            </div>
            
            <div style="background: rgba(255,255,255,.12); border-radius: 16px; padding: 20px; margin: 20px 0;">
                <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 14px;">📊 Target KPIs</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    {''.join([f'<div style="background: rgba(255,255,255,.16); padding: 12px; border-radius: 10px; font-weight: 700; text-align: center;">{kpi}</div>' for kpi in p['kpis']])}
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-top: 20px; padding: 18px; background: rgba(255,255,255,.16); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 0.92rem; opacity: .92; margin-bottom: 6px; font-weight: 600;">Budget Allocation</div>
                    <div style="font-size: 1.8rem; font-weight: 900;">{p['budget']}</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 0.92rem; opacity: .92; margin-bottom: 6px; font-weight: 600;">ROI Target</div>
                    <div style="font-size: 1.8rem; font-weight: 900;">{p['roi']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="insights-section">', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-bottom: 20px;">🧠 AI-Powered Insights & Recommendations</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,.16); border-radius: 16px; padding: 24px; backdrop-filter: blur(10px); margin-bottom: 20px;">
            <div style="font-size: 1.35rem; font-weight: 800; margin-bottom: 16px;">📊 Top Performers</div>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">🏆 Highest Revenue: {}</li>
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">👥 Largest Group: {} ({:,} customers)</li>
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">💰 Best AOV: {} (£{:.0f})</li>
                <li style="padding: 10px 0; font-size: 1.02rem; font-weight: 500;">🔄 Most Frequent: {} ({:.1f} orders)</li>
            </ul>
        </div>
        """.format(
            filtered_df.groupby('Cluster_Label')['Monetary'].sum().idxmax(),
            filtered_df['Cluster_Label'].value_counts().idxmax(),
            filtered_df['Cluster_Label'].value_counts().max(),
            filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax(),
            filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean().max(),
            filtered_df.groupby('Cluster_Label')['Frequency'].mean().idxmax(),
            filtered_df.groupby('Cluster_Label')['Frequency'].mean().max()
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,.16); border-radius: 16px; padding: 24px; backdrop-filter: blur(10px); margin-bottom: 20px;">
            <div style="font-size: 1.35rem; font-weight: 800; margin-bottom: 16px;">💡 Smart Recommendations</div>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">🎯 Prioritize high-value segment retention programs</li>
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">📧 Launch win-back campaigns for dormant customers</li>
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">🚀 Accelerate potential customer nurturing flows</li>
                <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); font-size: 1.02rem; font-weight: 500;">💎 Create exclusive VIP experiences for champions</li>
                <li style="padding: 10px 0; font-size: 1.02rem; font-weight: 500;">📈 Implement cross-sell strategies for loyal segments</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 26px; border-top: 4px solid #667eea; color: #7f8c8d; font-size: 1.05rem; font-weight: 600;">
    Customer Intelligence Hub • Powered by Streamlit • All data is confidential
</div>
""", unsafe_allow_html=True)
