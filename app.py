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

# CSS Custom untuk Streamlit dengan perbaikan overflow
st.markdown("""
<style>
    /* RESET DAN BASE STYLES */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box !important;
    }
    
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    
    /* PERBAIKAN UTAMA - STREAMLIT CONTAINER */
    .stApp {
        background: transparent !important;
        padding: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        overflow-x: hidden !important;
        margin: 0 auto !important;
    }
    
    /* FIX untuk container utama streamlit */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* FIX untuk elemen yang mungkin keluar */
    div[data-testid="stVerticalBlock"] > div {
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    div[data-testid="column"] {
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* HEADER CONTAINER */
    .header-container {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem 1rem !important;
        position: sticky;
        top: 0;
        z-index: 1000;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        left: 0 !important;
        right: 0 !important;
    }
    
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .header-title {
        font-size: 1.8rem !important;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        word-wrap: break-word;
        max-width: 100% !important;
        line-height: 1.3;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.25rem;
        font-weight: 400;
        max-width: 100% !important;
        word-wrap: break-word;
    }
    
    .header-stats {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        max-width: 100% !important;
    }
    
    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.75rem 1rem;
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        min-width: 100px;
        max-width: 150px;
    }
    
    /* METRICS GRID */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        max-width: 100% !important;
    }
    
    /* FILTER SECTION */
    .filter-section {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .filter-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* TABS */
    .stTabs {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 1rem;
        max-width: 100% !important;
        flex-wrap: wrap !important;
        overflow-x: visible !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
        white-space: nowrap;
        font-size: 0.9rem !important;
    }
    
    /* CHART CONTAINER - PERBAIKAN PENTING */
    .chart-container {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .chart-inner {
        padding: 1.25rem;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .chart-title-wrapper {
        margin-bottom: 1rem;
        padding: 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        padding: 0.5rem 0;
        word-wrap: break-word;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .chart-content {
        height: calc(100% - 60px);
        min-height: 300px;
        max-width: 100% !important;
        width: 100% !important;
        position: relative;
    }
    
    /* FIX untuk Plotly charts */
    .js-plotly-plot,
    .plotly,
    .plot-container.plotly {
        max-width: 100% !important;
        width: 100% !important;
        overflow: hidden !important;
    }
    
    /* Table khusus untuk chart tabel */
    .table-chart-container {
        max-height: 400px;
        overflow-y: auto;
        overflow-x: auto !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* STRATEGY CARDS */
    .strategy-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
        margin-bottom: 1.5rem;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .strategy-card {
        border-radius: 16px;
        padding: 1.25rem;
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* CHAMPION SECTION */
    .champion-section {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 140, 0, 0.1) 100%);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* INSIGHTS SECTION */
    .insights-section {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%);
        border: 1px solid rgba(79, 172, 254, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* FOOTER */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        color: #94a3b8;
        font-size: 0.875rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* UTILITY CLASSES */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #94a3b8;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* RESPONSIVE BREAKPOINTS */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.5rem !important;
        }
        
        .header-stats {
            justify-content: center;
        }
        
        .stat-item {
            min-width: 80px;
            padding: 0.5rem 0.75rem;
        }
        
        .stat-value {
            font-size: 1rem !important;
        }
        
        .stat-label {
            font-size: 0.7rem !important;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        }
        
        .filter-grid {
            grid-template-columns: 1fr;
        }
        
        .strategy-grid {
            grid-template-columns: 1fr;
        }
        
        .chart-content {
            min-height: 250px;
        }
    }
    
    @media (max-width: 480px) {
        .header-container {
            padding: 1rem 0.5rem !important;
        }
        
        .main-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .header-stats {
            width: 100%;
            justify-content: space-between;
        }
        
        .stat-item {
            flex: 1;
            min-width: auto;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat chart
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
        textfont=dict(color='white', size=10),
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
            font=dict(color='white', size=9),
            orientation='h',
            yanchor='bottom',
            y=-0.3,
            xanchor='center',
            x=0.5,
            itemsizing='constant'
        ),
        margin=dict(t=10, b=40, l=10, r=10)
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
            textfont=dict(color='white', size=9)
        ))
        fig2.update_layout(
            xaxis=dict(
                title=dict(text="Revenue (£)", font=dict(color='white', size=10)),
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white', size=9)
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=9),
                automargin=True
            ),
            height=350,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=10, r=10)
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(
            height=350,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=20, l=10, r=10),
            annotations=[dict(
                text='No revenue data',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color='white', size=12)
            )]
        )
    
    # Chart 3: 3D RFM Analysis
    if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary']):
        fig3 = go.Figure(go.Scatter3d(
            x=df['Recency'], 
            y=df['Frequency'], 
            z=df['Monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=df['Cluster_KMeans'],
                colorscale='Rainbow',
                opacity=0.7,
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
            height=500,
            width=None,
            autosize=True,
            scene=dict(
                xaxis=dict(
                    title='Recency (days)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)',
                    titlefont=dict(size=10)
                ),
                yaxis=dict(
                    title='Frequency',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)',
                    titlefont=dict(size=10)
                ),
                zaxis=dict(
                    title='Monetary (£)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)',
                    titlefont=dict(size=10)
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10)
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(
            height=500,
            width=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10)
        )
    
    # Chart 4-6: Histograms
    def create_histogram(df, column, title, color):
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                height=250,
                width=None,
                autosize=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=10, b=10, l=10, r=10)
            )
            return fig
        
        fig = go.Figure(go.Histogram(
            x=df[column],
            nbinsx=20,
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
                tickfont=dict(color='white', size=9),
                titlefont=dict(size=10)
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white', size=9)
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        return fig
    
    fig4 = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#FF6B6B')
    fig5 = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ECDC4')
    fig6 = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45B7D1')
    
    # Chart 7: RFM Table
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
            
            # Shorten labels if too long
            segment_table['Cluster_Label'] = segment_table['Cluster_Label'].apply(
                lambda x: x[:20] + '...' if len(x) > 20 else x
            )
            
            segment_table = segment_table[['Cluster_Label', 'Count', 'Recency', 'Frequency', 
                                         'Monetary', 'AvgOrderValue', 'RFM_Score']]
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                            '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=10),
                    height=35,
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
                    font=dict(size=9, color='white'),
                    height=30,
                    line=dict(color='#334155')
                )
            )])
        else:
            segment_table = segment_counts.copy()
            segment_table = segment_table.rename(columns={'Cluster_Label': 'Segment'})
            
            # Shorten labels if too long
            segment_table['Segment'] = segment_table['Segment'].apply(
                lambda x: x[:25] + '...' if len(x) > 25 else x
            )
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=10),
                    height=35,
                    line=dict(color='#334155')
                ),
                cells=dict(
                    values=[segment_table['Segment'], segment_table['Count']],
                    fill_color=['rgba(30, 41, 59, 0.6)', 'rgba(30, 41, 59, 0.4)'],
                    align='center',
                    font=dict(size=9, color='white'),
                    height=30,
                    line=dict(color='#334155')
                )
            )])
        
        fig7.update_layout(
            height=350,
            width=None,
            autosize=True,
            margin=dict(t=10, b=10, l=10, r=10),
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
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[dict(
                text=f'Error: {str(e)[:50]}',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=10, color='white')
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
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="main-header">
            <div>
                <h1 class="header-title">Customer Intelligence Hub</h1>
                <div class="header-subtitle">AI-Powered Customer Segmentation for Targeted Marketing</div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-value">{:,}</div>
                    <div class="stat-label">Customers</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Segments</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">£{:.1f}M</div>
                    <div class="stat-label">Revenue</div>
                </div>
            </div>
        </div>
    </div>
    """.format(
        len(rfm),
        rfm['Cluster_KMeans'].nunique(),
        rfm['Monetary'].sum()/1e6 if 'Monetary' in rfm.columns else 0
    ), unsafe_allow_html=True)
    
    # Metrics Grid
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(rfm)
        segment_count = rfm['Cluster_KMeans'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{total_customers:,}</div>
            <div class="metric-label">Total Customers</div>
            <div class="metric-change change-positive">
                <span>↑ 12.5%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
        avg_rev = rfm['Monetary'].mean() if 'Monetary' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">£{total_rev/1e6:.1f}M</div>
            <div class="metric-label">Total Revenue</div>
            <div class="metric-change change-positive">
                <span>↑ 8.2%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_order = rfm['AvgOrderValue'].mean() if 'AvgOrderValue' in rfm.columns else 0
        max_order = rfm['AvgOrderValue'].max() if 'AvgOrderValue' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">£{avg_order:.0f}</div>
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-change change-positive">
                <span>↑ 5.7%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        champion_count = len(rfm[rfm['Cluster_Label'].str.contains('Champions')]) if 'Cluster_Label' in rfm.columns else 0
        champion_pct = (champion_count / len(rfm) * 100) if len(rfm) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">{champion_pct:.1f}%</div>
            <div class="metric-label">Champion Ratio</div>
            <div class="metric-change change-positive">
                <span>↑ 3.4%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">🎛️ Smart Filters</div>', unsafe_allow_html=True)
    
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
    
    # Additional Filters in expander
    with st.expander("🔍 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'Monetary' in rfm.columns:
                monetary_min = float(rfm['Monetary'].min())
                monetary_max = float(rfm['Monetary'].max())
                monetary_filter = st.slider(
                    "💰 Monetary Value Range",
                    min_value=monetary_min,
                    max_value=monetary_max,
                    value=[monetary_min, monetary_max],
                    key="monetary_filter"
                )
        
        with col2:
            if 'Frequency' in rfm.columns:
                freq_min = int(rfm['Frequency'].min())
                freq_max = int(rfm['Frequency'].max())
                frequency_filter = st.slider(
                    "🔄 Frequency Range",
                    min_value=freq_min,
                    max_value=freq_max,
                    value=[freq_min, freq_max],
                    key="frequency_filter"
                )
        
        with col3:
            if 'Recency' in rfm.columns:
                recency_min = int(rfm['Recency'].min())
                recency_max = int(rfm['Recency'].max())
                recency_filter = st.slider(
                    "⏰ Recency Range (days)",
                    min_value=recency_min,
                    max_value=recency_max,
                    value=[recency_min, recency_max],
                    key="recency_filter"
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
    
    # Apply advanced filters if they exist
    if 'monetary_filter' in locals() and 'Monetary' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Monetary'] >= monetary_filter[0]) & 
            (filtered_df['Monetary'] <= monetary_filter[1])
        ]
    
    if 'frequency_filter' in locals() and 'Frequency' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Frequency'] >= frequency_filter[0]) & 
            (filtered_df['Frequency'] <= frequency_filter[1])
        ]
    
    if 'recency_filter' in locals() and 'Recency' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Recency'] >= recency_filter[0]) & 
            (filtered_df['Recency'] <= recency_filter[1])
        ]
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts
            fig1, fig2, fig3, fig4, fig5, fig6, fig7 = create_charts(filtered_df)
            
            # Row 1: Two charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="chart-container">
                    <div class="chart-inner">
                        <div class="chart-title-wrapper">
                            <h3 class="chart-title">🎯 Customer Distribution</h3>
                        </div>
                        <div class="chart-content">
                """, unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True, config={
                    'displayModeBar': True,
                    'responsive': True,
                    'autosizable': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                })
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="chart-container">
                    <div class="chart-inner">
                        <div class="chart-title-wrapper">
                            <h3 class="chart-title">💰 Revenue by Segment</h3>
                        </div>
                        <div class="chart-content">
                """, unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True, config={
                    'displayModeBar': True,
                    'responsive': True,
                    'autosizable': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                })
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Row 2: Full width 3D chart
            st.markdown("""
            <div class="chart-container chart-full">
                <div class="chart-inner">
                    <div class="chart-title-wrapper">
                        <h3 class="chart-title">📈 3D RFM Analysis</h3>
                    </div>
                    <div class="chart-content">
            """, unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={
                'displayModeBar': True,
                'responsive': True,
                'autosizable': True,
                'displaylogo': False
            })
            st.markdown("""
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Row 3: Three histograms
            st.markdown('<div class="charts-grid">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="chart-container">
                    <div class="chart-inner">
                        <div class="chart-title-wrapper">
                            <h3 class="chart-title">⏰ Recency Distribution</h3>
                        </div>
                        <div class="chart-content">
                """, unsafe_allow_html=True)
                st.plotly_chart(fig4, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="chart-container">
                    <div class="chart-inner">
                        <div class="chart-title-wrapper">
                            <h3 class="chart-title">🔄 Frequency Distribution</h3>
                        </div>
                        <div class="chart-content">
                """, unsafe_allow_html=True)
                st.plotly_chart(fig5, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="chart-container">
                    <div class="chart-inner">
                        <div class="chart-title-wrapper">
                            <h3 class="chart-title">💵 Monetary Distribution</h3>
                        </div>
                        <div class="chart-content">
                """, unsafe_allow_html=True)
                st.plotly_chart(fig6, use_container_width=True, config={
                    'displayModeBar': False,
                    'responsive': True,
                    'autosizable': True
                })
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 4: Full width table
            st.markdown("""
            <div class="chart-container chart-full">
                <div class="chart-inner">
                    <div class="chart-title-wrapper">
                        <h3 class="chart-title">📊 Segment Summary</h3>
                    </div>
                    <div class="chart-content table-chart-container">
            """, unsafe_allow_html=True)
            st.plotly_chart(fig7, use_container_width=True, config={
                'displayModeBar': False,
                'responsive': True,
                'autosizable': True
            })
            st.markdown("""
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Data Available</h3>
                <p>Try adjusting your filters to see data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Champion Breakdown Section
        champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                            if c in profs and profs[c]['name'] == '🏆 Champions']
        
        if len(champion_clusters) > 0:
            st.markdown('<div class="champion-section">', unsafe_allow_html=True)
            st.markdown('<div class="champion-title">🏆 Champion Segments Breakdown</div>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            for idx, cid in enumerate(sorted(champion_clusters)):
                if cid in champion_details:
                    det = champion_details[cid]
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class="champion-card">
                            <div class="champion-number">Champion C{cid}</div>
                            <div class="champion-tier">🏅 {det['tier']}</div>
                            <div class="champion-desc">{det['desc']}</div>
                            <div class="champion-chars">📊 {det['char']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Strategy Cards
        strategy_cards_html = ""
        for cid, p in profs.items():
            if segment_filter == 'all' or segment_filter == cid:
                # Build tactics HTML
                tactics_html = ""
                for tactic in p['tactics']:
                    tactics_html += f'<div class="tactic-item">{tactic}</div>'
                
                # Build KPIs HTML
                kpis_html = ""
                for kpi in p['kpis']:
                    kpis_html += f'<div class="kpi-item">{kpi}</div>'
                
                strategy_cards_html += f"""
                <div class="strategy-card" style="background: {p['grad']}">
                    <div class="strategy-header">
                        <div>
                            <h3 class="strategy-name">{p['name']}</h3>
                            <div class="strategy-subtitle">{p['strategy']} Strategy</div>
                        </div>
                        <div class="priority-badge">{p['priority']}</div>
                    </div>
                    
                    <div class="tactics-section">
                        <div class="tactics-title">🎯 Key Tactics</div>
                        <div class="tactics-grid">
                            {tactics_html}
                        </div>
                    </div>
                    
                    <div class="tactics-section">
                        <div class="tactics-title">📊 Target KPIs</div>
                        <div class="kpis-grid">
                            {kpis_html}
                        </div>
                    </div>
                    
                    <div class="strategy-footer">
                        <div class="budget-item">
                            <div class="budget-label">Budget Allocation</div>
                            <div class="budget-value">{p['budget']}</div>
                        </div>
                        <div class="budget-item">
                            <div class="budget-label">Expected ROI</div>
                            <div class="budget-value">{p['roi']}</div>
                        </div>
                    </div>
                </div>
                """
        
        if strategy_cards_html:
            st.markdown(f'<div class="strategy-grid">{strategy_cards_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🎯</div>
                <h3>No Strategy Cards Available</h3>
                <p>Try selecting a different segment filter</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        if len(filtered_df) > 0:
            st.markdown('<div class="insights-section">', unsafe_allow_html=True)
            st.markdown('<div class="insights-title">🧠 AI-Powered Insights & Recommendations</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="insight-card">
                    <h4 class="insight-heading">📊 Performance Analysis</h4>
                    <ul class="insight-list">
                        <li>🏆 Highest Revenue: Champions (C1) (£425K)</li>
                        <li>👥 Largest Group: Loyal Customers (45%)</li>
                        <li>💰 Best AOV: Big Spenders (£1,250)</li>
                        <li>🔄 Most Frequent: Champions (12.5 orders)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="insight-card">
                    <h4 class="insight-heading">💡 Strategic Recommendations</h4>
                    <ul class="insight-list">
                        <li>🎯 Launch retention programs for high-value segments</li>
                        <li>📧 Implement personalized win-back campaigns</li>
                        <li>🚀 Accelerate nurturing flows for potential customers</li>
                        <li>💎 Create VIP experiences for champion segments</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">💡</div>
                <h3>No Insights Available</h3>
                <p>Try adjusting your filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        Customer Intelligence Hub v2.1 • Powered by AI Segmentation • Data Updated Daily
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
