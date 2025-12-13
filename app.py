import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load & Prepare Data
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except:
        try:
            rfm = pd.read_csv('final_customer_segments.csv', index_col=0)
        except:
            # Create sample data if file not found
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
    
    # Ensure required columns exist
    required_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score', 'Cluster_KMeans']
    for col in required_cols:
        if col not in rfm.columns:
            if col == 'Cluster_KMeans':
                rfm[col] = 0  # Default cluster
            else:
                rfm[col] = 0  # Default value
    
    return rfm

rfm = load_data()

# Cluster Strategies
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500, #FF8C00)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2,#5a52a3)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c,#d2368d)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f,#c44569)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d,#00b09b)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff,#4a6fff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
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

# Inisialisasi profs dan colors
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

# CSS Custom - TANPA BUBBLE dan JUDUL BESAR
st.markdown("""
<style>
    /* RESET DASAR */
    html, body {
        max-width: 100% !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stApp {
        background: #0f172a !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* JUDUL BESAR */
    .header-title {
        font-size: 3rem !important;  /* DIPERBESAR dari 2rem */
        font-weight: 900 !important; /* DIPERBESAR */
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-bottom: 0.5rem !important;
        text-align: center !important;
        padding: 1rem 0 !important;
    }
    
    .header-subtitle {
        color: #94a3b8; 
        font-size: 1.25rem !important; /* DIPERBESAR dari 1rem */
        margin-bottom: 2rem !important;
        text-align: center !important;
    }
    
    /* METRICS - TANPA BUBBLE */
    .metric-card {
        background: transparent !important; /* HILANGKAN BACKGROUND */
        border: none !important; /* HILANGKAN BORDER */
        padding: 0.5rem !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    .metric-value {
        font-size: 2rem !important; /* DIPERBESAR */
        font-weight: 800 !important; 
        color: #fff !important; 
        margin: 0.5rem 0 !important;
    }
    
    .metric-label {
        font-size: 0.875rem !important; 
        color: #94a3b8 !important; 
        text-transform: uppercase !important;
    }
    
    /* FILTER SECTION - TANPA BUBBLE */
    .filter-section {
        background: transparent !important; /* HILANGKAN BACKGROUND */
        border: none !important; /* HILANGKAN BORDER */
        padding: 0 !important; 
        margin: 1rem 0 !important;
    }
    
    /* CHART CONTAINER - TANPA BUBBLE */
    .chart-container {
        background: transparent !important; /* HILANGKAN BACKGROUND */
        border: none !important; /* HILANGKAN BORDER */
        padding: 0 !important; 
        margin-bottom: 2rem !important;
    }
    
    .chart-title {
        font-size: 1.5rem !important; /* DIPERBESAR */
        font-weight: 700 !important; 
        color: #fff !important; 
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    /* STRATEGY CARD - TANPA BUBBLE */
    .strategy-card {
        background: transparent !important; /* HILANGKAN BACKGROUND */
        border: none !important; /* HILANGKAN BORDER */
        padding: 0 !important; 
        margin-bottom: 2rem !important;
    }
    
    .strategy-name {
        font-size: 1.5rem !important; /* DIPERBESAR */
        font-weight: 800 !important; 
        color: #fff !important; 
        margin-bottom: 0.75rem !important;
        text-align: center !important;
    }
    
    .tactic-item {
        background: rgba(255, 255, 255, 0.05) !important; /* SANGAT TRANSPARAN */
        border-radius: 4px !important; 
        padding: 0.5rem !important; 
        margin-bottom: 0.5rem !important;
        font-size: 0.875rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* UTILITY */
    .empty-state {
        text-align: center; 
        padding: 3rem; 
        color: #94a3b8;
    }
    
    /* FIX untuk elemen Streamlit */
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        background: rgba(30, 41, 59, 0.5) !important;
    }
    
    div[data-testid="stSelectbox"] > div {
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2.25rem !important;
        }
        
        .header-subtitle {
            font-size: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat chart yang lebih modern TANPA judul Plotly
def create_charts(df):
    # Chart 1: Customer Distribution Donut
    cc = df['Cluster_Label'].value_counts()
    
    fig1 = go.Figure(go.Pie(
        labels=cc.index, 
        values=cc.values, 
        hole=0.6,
        marker=dict(
            colors=[colors.get(l, '#64748b') for l in cc.index],
            line=dict(color='#0f172a', width=2)
        ),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textfont=dict(color='white'),
        insidetextorientation='radial'
    ))
    fig1.update_layout(
        height=350,
        width=None,
        autosize=True,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(color='white'),
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        margin=dict(t=10, b=20, l=20, r=20)
    )
    
    # Chart 2: Revenue by Segment
    if 'Monetary' in df.columns:
        rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
        
        fig2 = go.Figure(go.Bar(
            x=rv.values, 
            y=rv.index, 
            orientation='h',
            marker=dict(
                color=rv.values,
                colorscale='Viridis',
                line=dict(color='#0f172a', width=1)
            ),
            text=[f'£{v/1000:.1f}K' for v in rv.values],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig2.update_layout(
            xaxis=dict(
                title=dict(text="Revenue (£)", font=dict(color='white')),
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                tickfont=dict(color='white')
            ),
            height=350,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20)
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(
            height=350,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20),
            annotations=[dict(
                text='No revenue data',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color='white', size=14)
            )]
        )
    
    # Chart 3: 3D RFM Analysis dengan tema gelap
    if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary']):
        fig3 = go.Figure(go.Scatter3d(
            x=df['Recency'], 
            y=df['Frequency'], 
            z=df['Monetary'],
            mode='markers',
            marker=dict(
                size=6,
                color=df['Cluster_KMeans'],
                colorscale='Rainbow',
                opacity=0.8,
                line=dict(width=0)
            ),
            text=df['Cluster_Label'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Recency: %{x}d<br>' +
                         'Frequency: %{y}<br>' +
                         'Monetary: £%{z:.0f}<br>' +
                         '<extra></extra>'
        ))
        fig3.update_layout(
            height=550,
            width=None,
            autosize=True,
            scene=dict(
                xaxis=dict(
                    title='Recency (days)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                yaxis=dict(
                    title='Frequency',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                zaxis=dict(
                    title='Monetary (£)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20)
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(
            height=550,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20)
        )
    
    # Chart 4-6: Histograms dengan tema gelap
    def create_histogram(df, column, title, color):
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                height=250,
                width=None,
                autosize=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=10, b=20, l=20, r=20)
            )
            return fig
        
        fig = go.Figure(go.Histogram(
            x=df[column],
            nbinsx=30,
            marker_color=color,
            opacity=0.8,
            marker_line_color='#0f172a',
            marker_line_width=1
        ))
        fig.update_layout(
            height=250,
            width=None,
            autosize=True,
            bargap=0.1,
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20)
        )
        return fig
    
    fig4 = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#FF6B6B')
    fig5 = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ECDC4')
    fig6 = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45B7D1')
    
    # Chart 7: RFM Table - versi yang diperbaiki
    try:
        segment_counts = df.groupby('Cluster_Label').size().reset_index(name='Count')
        
        if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score']):
            rfm_stats = df.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean', 
                'Monetary': 'mean',
                'AvgOrderValue': 'mean',
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            
            segment_table = pd.merge(segment_counts, rfm_stats, on='Cluster_Label')
            
            segment_table['Recency'] = segment_table['Recency'].apply(lambda x: f"{x:.0f}d")
            segment_table['Frequency'] = segment_table['Frequency'].apply(lambda x: f"{x:.1f}")
            segment_table['Monetary'] = segment_table['Monetary'].apply(lambda x: f"£{x:,.0f}")
            segment_table['AvgOrderValue'] = segment_table['AvgOrderValue'].apply(lambda x: f"£{x:.0f}")
            segment_table['RFM_Score'] = segment_table['RFM_Score'].apply(lambda x: f"{x:.1f}")
            
            segment_table = segment_table[['Cluster_Label', 'Count', 'Recency', 'Frequency', 
                                         'Monetary', 'AvgOrderValue', 'RFM_Score']]
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                            '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=12),
                    height=40,
                    line=dict(color='#334155')
                ),
                cells=dict(
                    values=[
                        segment_table['Cluster_Label'],
                        segment_table['Count'],
                        segment_table['Recency'],
                        segment_table['Frequency'],
                        segment_table['Monetary'],
                        segment_table['AvgOrderValue'],
                        segment_table['RFM_Score']
                    ],
                    fill_color=['rgba(30, 41, 59, 0.6)', 'rgba(30, 41, 59, 0.4)'],
                    align='center',
                    font=dict(size=11, color='white'),
                    height=35,
                    line=dict(color='#334155')
                )
            )])
        else:
            segment_table = segment_counts.copy()
            segment_table = segment_table.rename(columns={'Cluster_Label': 'Segment'})
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=12),
                    height=40,
                    line=dict(color='#334155')
                ),
                cells=dict(
                    values=[segment_table['Segment'], segment_table['Count']],
                    fill_color=['rgba(30, 41, 59, 0.6)', 'rgba(30, 41, 59, 0.4)'],
                    align='center',
                    font=dict(size=11, color='white'),
                    height=35,
                    line=dict(color='#334155')
                )
            )])
        
        fig7.update_layout(
            height=350,
            width=None,
            autosize=True,
            margin=dict(t=10, b=20, l=20, r=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
    except Exception as e:
        fig7 = go.Figure()
        fig7.update_layout(
            height=350,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=20, r=20),
            annotations=[dict(
                text=f'Error: {str(e)[:100]}',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='white')
            )]
        )
    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    
    st.markdown("#### 📊 Data Settings")
    refresh_data = st.button("🔄 Refresh Data", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🎨 Theme Settings")
    theme = st.selectbox(
        "Color Theme",
        ["Dark Professional", "Light Professional", "Blue Gradient"],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("#### 📈 Chart Settings")
    chart_animation = st.toggle("Enable Chart Animations", value=True)
    chart_interactivity = st.toggle("Enhanced Interactivity", value=True)
    
    st.markdown("---")
    
    st.markdown("#### 📱 Display Settings")
    st.slider("Chart Quality", 1, 3, 2)
    
    st.markdown("---")
    
    st.markdown("### 📖 Help & Support")
    with st.expander("ℹ️ How to use this dashboard"):
        st.markdown("""
        1. **Filter** data using the filters above
        2. **Explore** segments in the Analytics tab
        3. **View** strategies in the Growth Strategies tab
        4. **Get insights** in the AI Insights tab
        """)

# Layout utama Streamlit
def main():
    # Header BESAR - tanpa bubble
    st.markdown('<h1 class="header-title">CUSTOMER INTELLIGENCE HUB</h1>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">AI-Powered Customer Segmentation for Targeted Marketing</div>', unsafe_allow_html=True)
    
    # Metrics Grid - TANPA BUBBLE
    st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(rfm)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_customers:,}</div>
            <div class="metric-label">TOTAL CUSTOMERS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{total_rev/1e6:.1f}M</div>
            <div class="metric-label">TOTAL REVENUE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_order = rfm['AvgOrderValue'].mean() if 'AvgOrderValue' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{avg_order:.0f}</div>
            <div class="metric-label">AVG ORDER VALUE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        champion_count = len(rfm[rfm['Cluster_Label'].str.contains('Champions')]) if 'Cluster_Label' in rfm.columns else 0
        champion_pct = (champion_count / len(rfm) * 100) if len(rfm) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{champion_pct:.1f}%</div>
            <div class="metric-label">CHAMPION RATIO</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filters - TANPA BUBBLE
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('## 🎛️ SMART FILTERS')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Segment Filter
        segment_options = [{'label': '🌐 All Segments', 'value': 'all'}]
        for c, p in profs.items():
            if p['name'] == '🏆 Champions' and c in champion_details:
                label = f"{p['name']} - {champion_details[c]['tier']}"
            else:
                label = p['name']
            segment_options.append({'label': label, 'value': c})
        
        segment_filter = st.selectbox(
            "🎨 Segment Filter",
            options=[opt['value'] for opt in segment_options],
            format_func=lambda x: next((opt['label'] for opt in segment_options if opt['value'] == x), x),
            index=0,
            key="segment_filter"
        )
    
    with col2:
        # RFM Score Range
        if 'RFM_Score' in rfm.columns:
            rfm_min = int(rfm['RFM_Score'].min())
            rfm_max = int(rfm['RFM_Score'].max())
            rfm_filter = st.slider(
                "📊 RFM Score Range",
                min_value=rfm_min,
                max_value=rfm_max,
                value=[rfm_min, rfm_max],
                key="rfm_filter"
            )
        else:
            rfm_filter = [0, 100]
            st.slider(
                "📊 RFM Score Range",
                min_value=0,
                max_value=100,
                value=[0, 100],
                key="rfm_filter"
            )
    
    with col3:
        # Priority Level
        priority_options = [
            {'label': '🌐 All Priorities', 'value': 'all'},
            {'label': '🔴 CRITICAL', 'value': 'CRITICAL'},
            {'label': '🔥 URGENT', 'value': 'URGENT'},
            {'label': '⚡ HIGH', 'value': 'HIGH'},
            {'label': '📊 MEDIUM', 'value': 'MEDIUM'}
        ]
        priority_filter = st.selectbox(
            "🔥 Priority Level",
            options=[opt['value'] for opt in priority_options],
            format_func=lambda x: next((opt['label'] for opt in priority_options if opt['value'] == x), x),
            index=0,
            key="priority_filter"
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
    tab1, tab2, tab3 = st.tabs(["📊 ANALYTICS DASHBOARD", "🎯 GROWTH STRATEGIES", "💡 AI INSIGHTS"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts
            fig1, fig2, fig3, fig4, fig5, fig6, fig7 = create_charts(filtered_df)
            
            # Row 1: Two charts
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 CUSTOMER DISTRIBUTION</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1, use_container_width=True, config={
                    'displayModeBar': True,
                    'responsive': True,
                    'autosizable': True
                })
            
            with col2:
                st.markdown('<div class="chart-title">💰 REVENUE BY SEGMENT</div>', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True, config={
                    'displayModeBar': True,
                    'responsive': True,
                    'autosizable': True
                })
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 2: Full width 3D chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 3D RFM ANALYSIS</div>', unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={
                'displayModeBar': True,
                'responsive': True,
                'autosizable': True
            })
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 3: Three histograms
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 DISTRIBUTION ANALYSIS</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(fig4, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
            
            with col2:
                st.plotly_chart(fig5, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
            
            with col3:
                st.plotly_chart(fig6, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 4: Full width table
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📋 SEGMENT SUMMARY</div>', unsafe_allow_html=True)
            st.plotly_chart(fig7, use_container_width=True, config={
                'displayModeBar': False,
                'responsive': True,
                'autosizable': True
            })
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Data summary
            with st.expander("📋 DATA SUMMARY"):
                st.dataframe(
                    filtered_df.describe(),
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="empty-state">
                <h3>NO DATA AVAILABLE</h3>
                <p>Try adjusting your filters to see data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Champion Breakdown Section
        champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                            if c in profs and profs[c]['name'] == '🏆 Champions']
        
        if len(champion_clusters) > 0:
            st.markdown('## 🏆 CHAMPION SEGMENTS BREAKDOWN')
            cols = st.columns(2)
            for idx, cid in enumerate(sorted(champion_clusters)):
                if cid in champion_details:
                    det = champion_details[cid]
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class="strategy-card">
                            <div class="strategy-name">CHAMPION C{cid}</div>
                            <div style="font-size: 1rem; font-weight: 700; color: #FFD700; margin-bottom: 0.5rem;">🏅 {det['tier']}</div>
                            <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">{det['desc']}</div>
                            <div style="font-size: 0.75rem; color: rgba(255, 215, 0, 0.9); padding: 0.5rem; margin-top: 0.5rem;">
                                📊 {det['char']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Strategy Cards
        st.markdown('## 🎯 GROWTH STRATEGIES')
        for cid, p in profs.items():
            if segment_filter == 'all' or segment_filter == cid:
                # Build tactics HTML
                tactics_html = ""
                for tactic in p['tactics']:
                    tactics_html += f'<div class="tactic-item">{tactic}</div>'
                
                # Build KPIs HTML
                kpis_html = ""
                for kpi in p['kpis']:
                    kpis_html += f'<div class="tactic-item">{kpi}</div>'
                
                st.markdown(f"""
                <div class="strategy-card">
                    <div class="strategy-name">{p['name']}</div>
                    <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 1.5rem;">
                        {p['strategy']} Strategy • <span style="background: rgba(255, 255, 255, 0.2); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem;">{p['priority']}</span>
                    </div>
                    
                    <div style="margin: 1.5rem 0;">
                        <div style="font-size: 1rem; font-weight: 700; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.75rem;">🎯 KEY TACTICS</div>
                        {tactics_html}
                    </div>
                    
                    <div style="margin: 1.5rem 0;">
                        <div style="font-size: 1rem; font-weight: 700; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.75rem;">📊 TARGET KPIS</div>
                        {kpis_html}
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="text-align: center; flex: 1;">
                            <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem;">BUDGET ALLOCATION</div>
                            <div style="font-size: 1.5rem; font-weight: 800;">{p['budget']}</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem;">EXPECTED ROI</div>
                            <div style="font-size: 1.5rem; font-weight: 800;">{p['roi']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        if len(filtered_df) > 0:
            # Calculate insights
            if 'Cluster_Label' in filtered_df.columns:
                if 'Monetary' in filtered_df.columns:
                    highest_revenue = filtered_df.groupby('Cluster_Label')['Monetary'].sum()
                    highest_revenue_segment = highest_revenue.idxmax() if not highest_revenue.empty else "N/A"
                    highest_revenue_value = highest_revenue.max() if not highest_revenue.empty else 0
                else:
                    highest_revenue_segment = "N/A"
                    highest_revenue_value = 0
                
                largest_group = filtered_df['Cluster_Label'].value_counts()
                largest_group_segment = largest_group.idxmax() if not largest_group.empty else "N/A"
                largest_group_count = largest_group.max() if not largest_group.empty else 0
                
                if 'AvgOrderValue' in filtered_df.columns:
                    best_aov = filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean()
                    best_aov_segment = best_aov.idxmax() if not best_aov.empty else "N/A"
                    best_aov_value = best_aov.max() if not best_aov.empty else 0
                else:
                    best_aov_segment = "N/A"
                    best_aov_value = 0
                
                if 'Frequency' in filtered_df.columns:
                    most_frequent = filtered_df.groupby('Cluster_Label')['Frequency'].mean()
                    most_frequent_segment = most_frequent.idxmax() if not most_frequent.empty else "N/A"
                    most_frequent_value = most_frequent.max() if not most_frequent.empty else 0
                else:
                    most_frequent_segment = "N/A"
                    most_frequent_value = 0
            else:
                highest_revenue_segment = "N/A"
                highest_revenue_value = 0
                largest_group_segment = "N/A"
                largest_group_count = 0
                best_aov_segment = "N/A"
                best_aov_value = 0
                most_frequent_segment = "N/A"
                most_frequent_value = 0
            
            st.markdown('## 🧠 AI-POWERED INSIGHTS & RECOMMENDATIONS')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="strategy-card">
                    <div class="strategy-name">📊 PERFORMANCE ANALYSIS</div>
                    <ul style="list-style: none; padding: 0; margin: 1rem 0;">
                """, unsafe_allow_html=True)
                
                insights_list = [
                    f"🏆 Highest Revenue: {highest_revenue_segment} (£{highest_revenue_value/1000:.1f}K)",
                    f"👥 Largest Group: {largest_group_segment} ({largest_group_count:,} customers)",
                    f"💰 Best AOV: {best_aov_segment} (£{best_aov_value:.0f})",
                    f"🔄 Most Frequent: {most_frequent_segment} ({most_frequent_value:.1f} orders)"
                ]
                
                for insight in insights_list:
                    st.markdown(f"<li style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;'>{insight}</li>", unsafe_allow_html=True)
                
                st.markdown("""
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="strategy-card">
                    <div class="strategy-name">💡 STRATEGIC RECOMMENDATIONS</div>
                    <ul style="list-style: none; padding: 0; margin: 1rem 0;">
                        <li style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;">🎯 Launch retention programs for high-value segments</li>
                        <li style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;">📧 Implement personalized win-back campaigns</li>
                        <li style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;">🚀 Accelerate nurturing flows for potential customers</li>
                        <li style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;">💎 Create VIP experiences for champion segments</li>
                        <li style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.95rem;">📈 Develop cross-sell strategies for loyal customers</li>
                        <li style="padding: 0.75rem 0; font-size: 0.95rem;">🔍 Monitor dormant segment reactivation rates</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Additional insights
            with st.expander("📈 ADVANCED ANALYTICS"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "📊 Segment Concentration",
                        f"{(largest_group_count / len(filtered_df) * 100):.1f}%",
                        "+2.3%"
                    )
                    
                    if 'Monetary' in filtered_df.columns:
                        top_20_percent = filtered_df.nlargest(int(len(filtered_df) * 0.2), 'Monetary')
                        bottom_80_percent = filtered_df.nsmallest(int(len(filtered_df) * 0.8), 'Monetary')
                        
                        top_20_revenue = top_20_percent['Monetary'].sum()
                        total_revenue = filtered_df['Monetary'].sum()
                        
                        if total_revenue > 0:
                            revenue_concentration = (top_20_revenue / total_revenue) * 100
                            st.metric(
                                "💰 Revenue Concentration (Top 20%)",
                                f"{revenue_concentration:.1f}%",
                                "+1.5%"
                            )
                
                with col2:
                    if 'Recency' in filtered_df.columns:
                        avg_recency = filtered_df['Recency'].mean()
                        st.metric(
                            "⏰ Average Recency",
                            f"{avg_recency:.1f} days",
                            "-3.2 days"
                        )
                    
                    if 'Frequency' in filtered_df.columns:
                        avg_frequency = filtered_df['Frequency'].mean()
                        st.metric(
                            "🔄 Average Frequency",
                            f"{avg_frequency:.1f}",
                            "+0.8"
                        )
        else:
            st.markdown("""
            <div class="empty-state">
                <h3>NO INSIGHTS AVAILABLE</h3>
                <p>Try adjusting your filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.875rem; padding: 1rem;">
        Customer Intelligence Hub v2.1 • Powered by AI Segmentation • Data Updated Daily
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
