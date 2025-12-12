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
    initial_sidebar_state="collapsed"
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
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
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

# CSS Custom untuk Streamlit yang Diperbarui
st.markdown("""
<style>
/* ====== RESET & BASE STYLES ====== */
/* ===== RESET ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

body {
    background: linear-gradient(145deg, #eef1f6, #d9dee8);
    padding: 24px;
    min-height: 100vh;
}

.stApp {
    background: transparent !important;
}

/* ===== MAIN CONTAINER ===== */
.main-container {
    background: #ffffff;
    border-radius: 26px;
    padding: 36px 44px;
    box-shadow:
        0 8px 20px rgba(0, 0, 0, 0.06),
        0 20px 40px rgba(0, 0, 0, 0.04);
    animation: fadeIn 0.7s ease-out;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* ===== HEADER ===== */
.hdr {
    text-align: center;
    padding: 36px 24px;
    border-radius: 22px;
    margin-bottom: 36px;
    background: linear-gradient(135deg, #7185ff, #6c47c6);
    box-shadow: 0 12px 35px rgba(113, 133, 255, 0.28);
    position: relative;
    overflow: hidden;
}

.hdr::before {
    content: "";
    position: absolute;
    width: 180%;
    height: 180%;
    top: -40%;
    left: -40%;
    background: radial-gradient(circle, rgba(255,255,255,0.12), transparent 70%);
    animation: pulse 5.5s infinite ease-in-out;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.title {
    color: #fff;
    font-size: 2.9rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    text-shadow: 0 3px 12px rgba(0,0,0,0.2);
}

.sub {
    color: rgba(255, 255, 255, 0.92);
    margin-top: 12px;
    font-size: 1.15rem;
}

/* ===== METRICS ===== */
.metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
}

.met {
    background: #ffffff;
    border-radius: 18px;
    padding: 26px;
    border: 1px solid #ececec;
    text-align: center;
    transition: 0.25s ease;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
}

.met:hover {
    transform: translateY(-4px);
    border-color: #7280ff;
    box-shadow:
        0 10px 28px rgba(113, 133, 255, 0.18),
        0 4px 10px rgba(0,0,0,0.05);
}

.met-icon {
    font-size: 2.4rem;
    color: #7280ff;
    margin-bottom: 10px;
}

.met-val {
    font-size: 2.3rem;
    font-weight: 800;
    color: #283046;
}

.met-lbl {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1.1px;
    color: #7280ff;
    margin-bottom: 6px;
}

.met-sub {
    font-size: 0.9rem;
    color: #687385;
}

/* ===== FILTERS ===== */
.filt {
    background: #fff;
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #ececec;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
}

.filt-t {
    font-size: 1.5rem;
    font-weight: 700;
    color: #253044;
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
}

.filt-g {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: #f3f4f7;
    border-radius: 16px;
    padding: 8px;
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 14px 20px;
    font-weight: 600;
    color: #6b7685;
    transition: 0.25s;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(113, 133, 255, 0.15);
    color: #7280ff;
}

.stTabs [aria-selected="true"] {
    background: #7280ff !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(113,133,255,0.25) !important;
}

/* ===== CHARTS ===== */
.charts {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 26px;
}

.chart {
    background: #fff;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid #ececec;
    transition: 0.25s ease;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

.chart:hover {
    transform: translateY(-3px);
    border-color: #7280ff;
    box-shadow: 0 10px 25px rgba(113,133,255,0.15);
}

.chart-full {
    grid-column: 1 / -1;
}

/* ===== STRATEGY CARD ===== */
.strat-g {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 26px;
}

.strat {
    padding: 28px;
    border-radius: 20px;
    background-size: cover;
    color: #fff;
    min-height: 400px;
    backdrop-filter: brightness(0.85);
    transition: 0.3s ease;
}

.strat:hover {
    transform: translateY(-5px);
    filter: brightness(1.1);
}

/* ===== CHAMPION BREAKDOWN ===== */
.champ-break {
    background: linear-gradient(135deg, #ffdd55, #ffb037);
    padding: 28px;
    border-radius: 18px;
    color: #fff;
    box-shadow: 0 12px 30px rgba(255,185,70,0.28);
}

.champ-card {
    background: rgba(255,255,255,0.22);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(8px);
    transition: 0.25s;
}

.champ-card:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-3px);
}

/* ===== INSIGHTS ===== */
.ins {
    background: linear-gradient(135deg, #4ebbff, #00e0ff);
    padding: 28px;
    border-radius: 18px;
    color: #fff;
    box-shadow: 0 12px 30px rgba(0,185,255,0.25);
}

.ins-card {
    background: rgba(255,255,255,0.22);
    padding: 20px;
    border-radius: 16px;
    transition: 0.25s;
    backdrop-filter: blur(8px);
}

.ins-card:hover {
    background: rgba(255,255,255,0.3);
}

.ins-list li {
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.25);
}

/* ===== FOOTER ===== */
.foot {
    text-align: center;
    padding: 20px;
    margin-top: 40px;
    color: #6f7b8a;
    font-weight: 500;
}

/* ===== STREAMLIT WIDGET FIX ===== */
div[data-testid="stSelectbox"] div {
    border-radius: 10px;
    border: 1px solid #ddd;
}

div[data-testid="stSelectbox"]:hover div {
    border-color: #7280ff;
}

# Fungsi untuk membuat chart yang lebih sederhana dan efektif
def create_charts(df):
    # Pastikan Cluster_Label ada
    if 'Cluster_Label' not in df.columns:
        df['Cluster_Label'] = df['Cluster_KMeans'].apply(lambda x: f"Cluster {x}")
    
    # Chart 1: Customer Distribution Pie
    cc = df['Cluster_Label'].value_counts()
    
    f1 = go.Figure(go.Pie(
        labels=cc.index, 
        values=cc.values, 
        hole=.5,
        marker=dict(
            colors=[colors.get(l, '#95A5A6') for l in cc.index]
        ),
        textinfo='label+percent',
        hoverinfo='label+value'
    ))
    f1.update_layout(
        title={'text': "🎯 Customer Distribution", 'x': 0.5},
        height=400,
        showlegend=True
    )
    
    # Chart 2: Revenue by Segment
    if 'Monetary' in df.columns:
        rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
        
        f2 = go.Figure(go.Bar(
            x=rv.values, 
            y=rv.index, 
            orientation='h',
            marker=dict(
                color=rv.values,
                colorscale='Viridis'
            ),
            text=[f'£{v/1000:.1f}K' for v in rv.values],
            textposition='outside'
        ))
        f2.update_layout(
            title={'text': "💰 Revenue by Segment", 'x': 0.5},
            xaxis_title="Revenue (£)",
            height=400
        )
    else:
        f2 = go.Figure()
        f2.update_layout(
            title={'text': "💰 Revenue by Segment", 'x': 0.5},
            height=400,
            annotations=[dict(
                text='No revenue data',
                x=0.5, y=0.5,
                showarrow=False
            )]
        )
    
    # Chart 3: 3D RFM Analysis
    if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary']):
        f3 = go.Figure(go.Scatter3d(
            x=df['Recency'], 
            y=df['Frequency'], 
            z=df['Monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=df['Cluster_KMeans'],
                colorscale='Rainbow',
                opacity=0.8
            ),
            text=df['Cluster_Label']
        ))
        f3.update_layout(
            title={'text': "📈 3D RFM Analysis", 'x': 0.5},
            height=600,
            scene=dict(
                xaxis_title='Recency (days)',
                yaxis_title='Frequency',
                zaxis_title='Monetary (£)'
            )
        )
    else:
        f3 = go.Figure()
        f3.update_layout(
            title={'text': "📈 3D RFM Analysis", 'x': 0.5},
            height=600
        )
    
    # Chart 4-6: Histograms
    def create_histogram(df, column, title, color):
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                title={'text': title, 'x': 0.5},
                height=300
            )
            return fig
        
        fig = go.Figure(go.Histogram(
            x=df[column],
            nbinsx=30,
            marker_color=color,
            opacity=0.8
        ))
        fig.update_layout(
            title={'text': title, 'x': 0.5},
            height=300,
            bargap=0.1
        )
        return fig
    
    f4 = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#FF6B6B')
    f5 = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ECDC4')
    f6 = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45B7D1')
    
    # Chart 7: RFM Table - FIXED VERSION
    try:
        # Pertama, hitung jumlah data per segment
        segment_counts = df.groupby('Cluster_Label').size().reset_index(name='Count')
        
        # Lalu hitung statistik RFM per segment
        if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score']):
            # Hitung rata-rata untuk setiap segment
            rfm_stats = df.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean', 
                'Monetary': 'mean',
                'AvgOrderValue': 'mean',
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            
            # Gabungkan dengan counts
            segment_table = pd.merge(segment_counts, rfm_stats, on='Cluster_Label')
            
            # Format nilai
            segment_table['Recency'] = segment_table['Recency'].apply(lambda x: f"{x:.0f}d")
            segment_table['Frequency'] = segment_table['Frequency'].apply(lambda x: f"{x:.1f}")
            segment_table['Monetary'] = segment_table['Monetary'].apply(lambda x: f"£{x:,.0f}")
            segment_table['AvgOrderValue'] = segment_table['AvgOrderValue'].apply(lambda x: f"£{x:.0f}")
            segment_table['RFM_Score'] = segment_table['RFM_Score'].apply(lambda x: f"{x:.1f}")
            
            # Urutkan kolom
            segment_table = segment_table[['Cluster_Label', 'Count', 'Recency', 'Frequency', 
                                         'Monetary', 'AvgOrderValue', 'RFM_Score']]
            
            # Buat tabel
            f7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                            '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#667eea',
                    align='center',
                    font=dict(color='white', size=12)
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
                    fill_color='white',
                    align='center',
                    font=dict(size=11)
                )
            )])
        else:
            # Jika tidak semua kolom RFM tersedia, buat tabel sederhana
            segment_table = segment_counts.copy()
            segment_table = segment_table.rename(columns={'Cluster_Label': 'Segment'})
            
            f7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>'],
                    fill_color='#667eea',
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[segment_table['Segment'], segment_table['Count']],
                    fill_color='white',
                    align='center',
                    font=dict(size=11)
                )
            )])
        
        f7.update_layout(
            title={'text': "📊 RFM Segment Summary", 'x': 0.5},
            height=400,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
    except Exception as e:
        f7 = go.Figure()
        f7.update_layout(
            title={'text': "📊 Segment Summary", 'x': 0.5},
            height=400,
            annotations=[dict(
                text=f'Error: {str(e)[:100]}',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12)
            )]
        )
    
    return f1, f2, f3, f4, f5, f6, f7

# Layout utama Streamlit
def main():
    # Container utama
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
   # Header
st.markdown(
    """
    <div class="hdr">
        <h1 class="title">🎯 Customer Intelligence Hub</h1>
        <p class="sub">Customer Segmentation for Personalized Retail Marketing</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="met">
            <div class="met-icon">👥</div>
            <div class="met-val">{len(rfm):,}</div>
            <div class="met-lbl">Customers</div>
            <div class="met-sub">Active Database</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="met">
            <div class="met-icon">🎯</div>
            <div class="met-val">{rfm['Cluster_KMeans'].nunique()}</div>
            <div class="met-lbl">Segments</div>
            <div class="met-sub">AI-Classified</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
    avg_rev = rfm['Monetary'].mean() if 'Monetary' in rfm.columns else 0

    st.markdown(
        f"""
        <div class="met">
            <div class="met-icon">💰</div>
            <div class="met-val">£{total_rev/1e6:.1f}M</div>
            <div class="met-lbl">Revenue</div>
            <div class="met-sub">Avg £{avg_rev:.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    avg_order = rfm['AvgOrderValue'].mean() if 'AvgOrderValue' in rfm.columns else 0
    max_order = rfm['AvgOrderValue'].max() if 'AvgOrderValue' in rfm.columns else 0

    st.markdown(
        f"""
        <div class="met">
            <div class="met-icon">📈</div>
            <div class="met-val">£{avg_order:.0f}</div>
            <div class="met-lbl">Avg Order</div>
            <div class="met-sub">Peak £{max_order:.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Filters
    st.markdown('<div class="filt">', unsafe_allow_html=True)
    st.markdown('<div class="filt-t">🎛️ Smart Filters</div>', unsafe_allow_html=True)
    
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
            rfm_min = 0
            rfm_max = 100
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
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts based on filtered data
            f1, f2, f3, f4, f5, f6, f7 = create_charts(filtered_df)
            
            # Row 1: Two charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart">', unsafe_allow_html=True)
                st.plotly_chart(f1, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart">', unsafe_allow_html=True)
                st.plotly_chart(f2, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 2: Full width 3D chart
            st.markdown('<div class="chart chart-full">', unsafe_allow_html=True)
            st.plotly_chart(f3, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 3: Three histograms
            st.markdown('<div class="charts">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="chart">', unsafe_allow_html=True)
                st.plotly_chart(f4, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart">', unsafe_allow_html=True)
                st.plotly_chart(f5, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="chart">', unsafe_allow_html=True)
                st.plotly_chart(f6, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 4: Full width table
            st.markdown('<div class="chart chart-full">', unsafe_allow_html=True)
            st.plotly_chart(f7, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-message">No data available for the selected filters.</div>', unsafe_allow_html=True)
    
    with tab2:
        # Champion Breakdown Section
        champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                            if c in profs and profs[c]['name'] == '🏆 Champions']
        
        if len(champion_clusters) > 0:
            champ_cards_html = ""
            for cid in sorted(champion_clusters):
                if cid in champion_details:
                    det = champion_details[cid]
                    champ_cards_html += f"""
                    <div class="champ-card">
                        <div class="champ-num">Champion C{cid}</div>
                        <div class="champ-tier">🏅 {det['tier']}</div>
                        <div class="champ-desc">{det['desc']}</div>
                        <div class="champ-char">📊 Characteristics: {det['char']}</div>
                    </div>
                    """
            
            if champ_cards_html:
                st.markdown(f"""
                <div class="champ-break">
                    <div class="champ-break-t">🏆 Champion Segments Breakdown</div>
                    <div style="text-align:center; font-size:1.1rem; margin-bottom:24px; opacity:0.95">
                        Understanding the 4 Different Champion Tiers
                    </div>
                    <div class="champ-grid">
                        {champ_cards_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Strategy Cards
        st_cards_html = ""
        for cid, p in profs.items():
            if segment_filter == 'all' or segment_filter == cid:
                # Build tactics HTML
                tactics_html = ""
                for tactic in p['tactics']:
                    tactics_html += f'<div class="tact">{tactic}</div>'
                
                # Build KPIs HTML
                kpis_html = ""
                for kpi in p['kpis']:
                    kpis_html += f'<div class="kpi">{kpi}</div>'
                
                st_cards_html += f"""
                <div class="strat" style="background: {p['grad']}">
                    <div class="strat-hdr">
                        <div class="strat-name">{p['name']}</div>
                        <div class="pri-badge">{p['priority']}</div>
                    </div>
                    <div class="strat-sub">📋 {p['strategy']} Strategy</div>
                    <div class="tactics">
                        <div class="tact-t">🎯 Key Tactics</div>
                        {tactics_html}
                    </div>
                    <div class="tactics">
                        <div class="tact-t">📊 Target KPIs</div>
                        <div class="kpi-g">
                            {kpis_html}
                        </div>
                    </div>
                    <div class="budget">
                        <div>
                            <div class="budget-l">Budget Allocation</div>
                            <div class="budget-v">{p['budget']}</div>
                        </div>
                        <div>
                            <div class="budget-l">ROI Target</div>
                            <div class="budget-v">{p['roi']}</div>
                        </div>
                    </div>
                </div>
                """
        
        if st_cards_html:
            st.markdown(f'<div class="strat-g">{st_cards_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-message">No strategy cards available for the selected filters.</div>', unsafe_allow_html=True)
    
    with tab3:
        if len(filtered_df) > 0:
            # Calculate insights
            if 'Cluster_Label' in filtered_df.columns:
                if 'Monetary' in filtered_df.columns:
                    highest_revenue = filtered_df.groupby('Cluster_Label')['Monetary'].sum()
                    highest_revenue_segment = highest_revenue.idxmax() if not highest_revenue.empty else "N/A"
                else:
                    highest_revenue_segment = "N/A"
                
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
                largest_group_segment = "N/A"
                largest_group_count = 0
                best_aov_segment = "N/A"
                best_aov_value = 0
                most_frequent_segment = "N/A"
                most_frequent_value = 0
            
            insights_html = f"""
            <div class="ins">
                <div class="ins-t">🧠 AI-Powered Insights & Recommendations</div>
                <div class="ins-g">
                    <div class="ins-card">
                        <div class="ins-h">📊 Top Performers</div>
                        <ul class="ins-list">
                            <li>🏆 Highest Revenue: {highest_revenue_segment}</li>
                            <li>👥 Largest Group: {largest_group_segment} ({largest_group_count:,} customers)</li>
                            <li>💰 Best AOV: {best_aov_segment} (£{best_aov_value:.0f})</li>
                            <li>🔄 Most Frequent: {most_frequent_segment} ({most_frequent_value:.1f} orders)</li>
                        </ul>
                    </div>
                    <div class="ins-card">
                        <div class="ins-h">💡 Smart Recommendations</div>
                        <ul class="ins-list">
                            <li>🎯 Prioritize high-value segment retention programs</li>
                            <li>📧 Launch win-back campaigns for dormant customers</li>
                            <li>🚀 Accelerate potential customer nurturing flows</li>
                            <li>💎 Create exclusive VIP experiences for champions</li>
                            <li>📈 Implement cross-sell strategies for loyal segments</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
            st.markdown(insights_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-message">No insights available for the selected filters.</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="foot">
        Customer Intelligence Hub v2.0 • Powered by AI Segmentation • Data Updated Daily
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
