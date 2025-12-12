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
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']
    
    colors = {}
    for c, p in profs.items():
        label = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
        colors[label] = p['color']
    
    return profs, colors, rfm

profs, colors, rfm = init_data(rfm)

# CSS Custom untuk Streamlit (sama seperti sebelumnya)
st.markdown("""
<style>
* {margin: 0; padding: 0; box-sizing: border-box}
body {font-family: 'Inter', 'Poppins', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 16px; min-height: 100vh}
.stApp {background: transparent !important; max-width: 100% !important; padding: 0 !important}

/* HEADER */
.hdr {text-align: center; padding: 28px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
       border-radius: 24px; margin-bottom: 36px; position: relative; overflow: hidden; 
       box-shadow: 0 15px 40px rgba(102,126,234,0.35)}
.hdr::before {content: ''; position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
              background: radial-gradient(circle, rgba(255,255,255,.15), transparent 60%); 
              animation: pulse 4s ease-in-out infinite}
@keyframes pulse {0%,100% {transform: scale(1) rotate(0deg)} 50% {transform: scale(1.15) rotate(5deg)}}
.title {font-size: 3.8rem; font-weight: 900; color: #fff; text-shadow: 4px 4px 8px rgba(0,0,0,.35); 
        margin: 0; letter-spacing: -1.5px; line-height: 1.1}
.sub {color: rgba(255,255,255,.95); font-size: 1.35rem; margin-top: 10px; font-weight: 500; letter-spacing: 0.5px}

/* METRICS */
.metrics {display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px; margin-bottom: 36px}
.met {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 22px; 
      padding: 32px 28px; text-align: center; color: #fff; 
      box-shadow: 0 15px 40px rgba(102,126,234,.45); 
      transition: all .4s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden}
.met::before {content: ''; position: absolute; top: -100%; left: -100%; width: 300%; height: 300%; 
              background: radial-gradient(circle, rgba(255,255,255,.2), transparent 65%); transition: .7s ease}
.met:hover {transform: translateY(-14px) scale(1.05); box-shadow: 0 25px 60px rgba(102,126,234,.65)}
.met:hover::before {top: 0; left: 0}
.met-icon {font-size: 3.5rem; margin-bottom: 14px; animation: float 3.5s ease-in-out infinite; 
           filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2))}
@keyframes float {0%,100% {transform: translateY(0)} 50% {transform: translateY(-8px)}}
.met-val {font-size: 3.2rem; font-weight: 900; margin: 12px 0; text-shadow: 3px 3px 6px rgba(0,0,0,.25); 
          letter-spacing: -1px}
.met-lbl {font-size: 1rem; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 700; margin-bottom: 6px}
.met-sub {font-size: .88rem; margin-top: 8px; opacity: .9; font-weight: 500}

/* FILTERS */
.filt {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 22px; 
       padding: 32px; margin-bottom: 32px; box-shadow: 0 10px 30px rgba(0,0,0,.12)}
.filt-t {font-size: 1.6rem; font-weight: 800; color: #2c3e50; margin-bottom: 22px; 
         display: flex; align-items: center; gap: 12px}
.filt-g {display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px}
.filt-g label {display: block; font-weight: 700; color: #34495e; margin-bottom: 8px; 
               font-size: 1rem; letter-spacing: 0.3px}

/* TABS */
.stTabs [data-baseweb="tab-list"] {gap: 12px; margin-bottom: 28px}
.stTabs [data-baseweb="tab"] {border: none; border-radius: 16px; padding: 14px 32px; 
                              font-weight: 700; font-size: 1.1rem; color: #667eea; 
                              background: #f8f9fa; transition: all .3s; letter-spacing: 0.5px}
.stTabs [data-baseweb="tab"]:hover {background: linear-gradient(135deg, #667eea, #764ba2); 
                                    color: #fff; transform: translateY(-3px); 
                                    box-shadow: 0 8px 20px rgba(102,126,234,.35)}
.stTabs [aria-selected="true"] {background: linear-gradient(135deg, #667eea, #764ba2) !important; 
                                color: #fff !important; 
                                box-shadow: 0 8px 20px rgba(102,126,234,.4) !important}

/* CHARTS */
.charts {display: grid; grid-template-columns: repeat(2, 1fr); gap: 26px; margin-bottom: 26px}
.chart {background: #fff; border-radius: 24px; padding: 32px; 
        box-shadow: 0 10px 35px rgba(0,0,0,.08); transition: all .35s ease; border: 3px solid transparent}
.chart:hover {transform: translateY(-6px); box-shadow: 0 20px 50px rgba(0,0,0,.15); border-color: #667eea}
.chart-full {grid-column: 1 / -1}

/* STRATEGY CARDS */
.strat-g {display: grid; grid-template-columns: repeat(2, 1fr); gap: 26px}
.strat {border-radius: 24px; padding: 36px 32px; color: #fff; 
        box-shadow: 0 15px 40px rgba(0,0,0,.22); 
        transition: all .45s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden}
.strat::after {content: ''; position: absolute; bottom: -50px; right: -50px; 
               width: 200px; height: 200px; background: rgba(255,255,255,.12); 
               border-radius: 50%; transition: .6s ease}
.strat:hover {transform: translateY(-8px) scale(1.03); box-shadow: 0 25px 60px rgba(0,0,0,.32)}
.strat:hover::after {bottom: -20px; right: -20px; width: 240px; height: 240px}
.strat-hdr {display: flex; justify-content: space-between; align-items: center; 
            margin-bottom: 24px; flex-wrap: wrap; gap: 12px}
.strat-name {font-size: 2.2rem; font-weight: 900; text-shadow: 3px 3px 6px rgba(0,0,0,.25); 
             letter-spacing: -0.5px}
.pri-badge {padding: 10px 22px; border-radius: 24px; font-weight: 800; font-size: .95rem; 
            letter-spacing: 1.5px; background: rgba(255,255,255,.25); 
            backdrop-filter: blur(10px); animation: glow 2.5s ease-in-out infinite; 
            box-shadow: 0 4px 15px rgba(0,0,0,.15)}
@keyframes glow {0%,100% {box-shadow: 0 0 15px rgba(255,255,255,.3)} 
                 50% {box-shadow: 0 0 28px rgba(255,255,255,.6)}}
.strat-sub {font-size: 1.3rem; font-weight: 700; margin-bottom: 20px; opacity: .95; letter-spacing: 0.3px}
.tactics {background: rgba(255,255,255,.12); border-radius: 16px; padding: 22px; 
          margin: 20px 0; backdrop-filter: blur(12px); 
          box-shadow: inset 0 2px 8px rgba(0,0,0,.1)}
.tact-t {font-size: 1.2rem; font-weight: 800; margin-bottom: 14px; letter-spacing: 0.5px}
.tact {padding: 14px 18px; margin: 10px 0; background: rgba(255,255,255,.18); 
       border-radius: 12px; transition: all .3s ease; border-left: 4px solid rgba(255,255,255,.45); 
       font-weight: 600; font-size: 1.02rem}
.tact:hover {background: rgba(255,255,255,.28); transform: translateX(8px); 
             border-left-width: 6px; box-shadow: 0 4px 12px rgba(0,0,0,.1)}
.kpi-g {display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin: 20px 0}
.kpi {background: rgba(255,255,255,.16); padding: 12px; border-radius: 10px; 
      font-weight: 700; text-align: center; backdrop-filter: blur(8px); 
      font-size: 1.02rem; letter-spacing: 0.3px}
.budget {display: flex; justify-content: space-between; margin-top: 20px; 
         padding: 18px; background: rgba(255,255,255,.16); 
         border-radius: 12px; backdrop-filter: blur(10px); gap: 12px}
.budget div {text-align: center; flex: 1}
.budget-l {font-size: .92rem; opacity: .92; margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px}
.budget-v {font-size: 1.8rem; font-weight: 900; letter-spacing: -0.5px}

/* CHAMPION BREAKDOWN */
.champ-break {background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 24px; 
              padding: 36px; color: #fff; margin: 26px 0; 
              box-shadow: 0 15px 40px rgba(255,215,0,.4)}
.champ-break-t {font-size: 2rem; font-weight: 900; margin-bottom: 26px; 
                letter-spacing: -0.5px; text-align: center}
.champ-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 22px}
.champ-card {background: rgba(255,255,255,.16); border-radius: 16px; padding: 24px; 
             backdrop-filter: blur(10px); transition: all .35s ease; 
             box-shadow: 0 4px 15px rgba(0,0,0,.1); border-left: 5px solid rgba(255,255,255,.5)}
.champ-card:hover {background: rgba(255,255,255,.26); transform: translateY(-4px) translateX(4px); 
                   box-shadow: 0 8px 25px rgba(0,0,0,.15); border-left-width: 8px}
.champ-num {font-size: 2.5rem; font-weight: 900; margin-bottom: 8px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,.2)}
.champ-tier {font-size: 1.3rem; font-weight: 800; margin-bottom: 12px; letter-spacing: 0.3px}
.champ-desc {font-size: 1.05rem; margin-bottom: 12px; opacity: .95; line-height: 1.5}
.champ-char {font-size: .95rem; background: rgba(255,255,255,.2); padding: 10px; 
             border-radius: 8px; font-weight: 600; margin-top: 8px}

/* INSIGHTS */
.ins {background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 24px; 
      padding: 36px; color: #fff; margin: 26px 0; 
      box-shadow: 0 15px 40px rgba(79,172,254,.4)}
.ins-t {font-size: 2rem; font-weight: 900; margin-bottom: 26px; letter-spacing: -0.5px}
.ins-g {display: grid; grid-template-columns: repeat(2, 1fr); gap: 22px}
.ins-card {background: rgba(255,255,255,.16); border-radius: 16px; padding: 24px; 
           backdrop-filter: blur(10px); transition: all .35s ease; 
           box-shadow: 0 4px 15px rgba(0,0,0,.1)}
.ins-card:hover {background: rgba(255,255,255,.26); transform: translateY(-4px); 
                 box-shadow: 0 8px 25px rgba(0,0,0,.15)}
.ins-h {font-size: 1.35rem; font-weight: 800; margin-bottom: 16px; letter-spacing: 0.3px}
.ins-list {list-style: none; padding: 0}
.ins-list li {padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.25); 
              font-size: 1.02rem; font-weight: 500; letter-spacing: 0.2px}
.ins-list li:last-child {border-bottom: none}

/* FOOTER */
.foot {text-align: center; margin-top: 50px; padding: 26px; 
       border-top: 4px solid #667eea; color: #7f8c8d; 
       font-size: 1.05rem; font-weight: 600; letter-spacing: 0.5px}

/* RESPONSIVE */
@media(max-width: 1200px){
    .metrics, .charts, .strat-g, .ins-g {grid-template-columns: repeat(2, 1fr)}
    .filt-g {grid-template-columns: 1fr}
    .chart-full {grid-column: 1 / -1}
}
@media(max-width: 768px){
    .metrics, .charts, .strat-g, .ins-g {grid-template-columns: 1fr}
    .title {font-size: 2.8rem}
    .dash {padding: 24px}
}

/* Container utama */
.main-container {background: rgba(255,255,255,0.98); border-radius: 32px; padding: 40px; 
                 box-shadow: 0 40px 100px rgba(0,0,0,0.4); 
                 animation: fadeIn .8s ease-out; margin: 0 auto}
@keyframes fadeIn {from {opacity: 0; transform: translateY(30px)} 
                   to {opacity: 1; transform: translateY(0)}}

/* Streamlit widget styling */
div[data-testid="stSelectbox"] div {border-radius: 12px}
div[data-testid="stSlider"] div {border-radius: 12px}

/* Additional styles for empty data handling */
.empty-message {text-align: center; padding: 40px; font-size: 1.2rem; color: #666; background: #f8f9fa; border-radius: 12px}
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat chart dengan error handling
def create_charts(df):
    if len(df) == 0:
        # Return empty figures if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title={'text': "No Data Available", 'x': .5, 
                   'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=420,
            annotations=[dict(
                text='<span style="font-size:16px">No data to display</span>',
                x=.5, y=.5, 
                font={'size': 16, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )]
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    
    try:
        # Chart 1: Customer Distribution Pie
        if 'Cluster_Label' in df.columns:
            cc = df['Cluster_Label'].value_counts()
        else:
            # Fallback if Cluster_Label doesn't exist
            df['Cluster_Label'] = df['Cluster_KMeans'].apply(lambda x: f"Cluster {x}")
            cc = df['Cluster_Label'].value_counts()
        
        f1 = go.Figure(go.Pie(
            labels=cc.index, 
            values=cc.values, 
            hole=.68,
            marker=dict(
                colors=[colors.get(l, '#95A5A6') for l in cc.index],
                line=dict(color='white', width=5)
            ),
            textfont=dict(size=14, family='Inter, Poppins', weight=700),
            textposition='outside',
            pull=[0.05]*len(cc)
        ))
        f1.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x': .5, 
                   'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=420,
            annotations=[dict(
                text=f'<b>{len(df):,}</b><br><span style="font-size:14px">Customers</span>',
                x=.5, y=.5, 
                font={'size': 24, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )],
            margin=dict(t=80, b=40, l=40, r=40)
        )
    except Exception as e:
        f1 = go.Figure()
        f1.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x': .5, 
                   'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=420,
            annotations=[dict(
                text=f'<span style="font-size:14px">Error: {str(e)[:50]}</span>',
                x=.5, y=.5, 
                font={'size': 14, 'color': 'red', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )]
        )
    
    try:
        # Chart 2: Revenue by Segment
        if 'Monetary' in df.columns and 'Cluster_Label' in df.columns:
            rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
            
            if len(rv) == 0:
                f2 = go.Figure()
                f2.update_layout(
                    title={'text': "<b>💰 Revenue by Segment</b>", 'x': .5, 
                           'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                    xaxis={
                        'title': '<b>Revenue (£)</b>', 
                        'titlefont': {'size': 14, 'family': 'Inter, Poppins'}, 
                        'gridcolor': 'rgba(0,0,0,0.05)'
                    },
                    yaxis={'titlefont': {'size': 14, 'family': 'Inter, Poppins'}},
                    height=420,
                    plot_bgcolor='rgba(245,247,250,.6)',
                    margin=dict(t=80, b=60, l=140, r=60),
                    annotations=[dict(
                        text='No revenue data',
                        x=.5, y=.5, 
                        font={'size': 16, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                        showarrow=False
                    )]
                )
            else:
                f2 = go.Figure(go.Bar(
                    x=rv.values, 
                    y=rv.index, 
                    orientation='h',
                    marker=dict(
                        color=rv.values, 
                        colorscale='Sunset',
                        line=dict(color='white', width=3)
                    ),
                    text=[f'£{v/1000:.1f}K' for v in rv.values],
                    textposition='outside',
                    textfont={'size': 13, 'weight': 700, 'family': 'Inter, Poppins'}
                ))
                f2.update_layout(
                    title={'text': "<b>💰 Revenue by Segment</b>", 'x': .5, 
                           'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                    xaxis={
                        'title': '<b>Revenue (£)</b>', 
                        'titlefont': {'size': 14, 'family': 'Inter, Poppins'}, 
                        'gridcolor': 'rgba(0,0,0,0.05)'
                    },
                    yaxis={'titlefont': {'size': 14, 'family': 'Inter, Poppins'}},
                    height=420,
                    plot_bgcolor='rgba(245,247,250,.6)',
                    margin=dict(t=80, b=60, l=140, r=60)
                )
        else:
            f2 = go.Figure()
            f2.update_layout(
                title={'text': "<b>💰 Revenue by Segment</b>", 'x': .5, 
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                height=420,
                annotations=[dict(
                    text='No revenue data available',
                    x=.5, y=.5, 
                    font={'size': 16, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                    showarrow=False
                )]
            )
    except Exception as e:
        f2 = go.Figure()
        f2.update_layout(
            title={'text': "<b>💰 Revenue by Segment</b>", 'x': .5, 
                   'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=420,
            annotations=[dict(
                text=f'Error: {str(e)[:50]}',
                x=.5, y=.5, 
                font={'size': 14, 'color': 'red', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )]
        )
    
    try:
        # Chart 3: 3D RFM Analysis
        if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary', 'Cluster_KMeans']):
            f3 = go.Figure(go.Scatter3d(
                x=df['Recency'], 
                y=df['Frequency'], 
                z=df['Monetary'], 
                mode='markers',
                marker=dict(
                    size=7, 
                    color=df['Cluster_KMeans'], 
                    colorscale='Rainbow', 
                    showscale=True,
                    line=dict(width=.8, color='white'), 
                    opacity=.88,
                    colorbar=dict(title='Cluster', thickness=20, len=0.7)
                ),
                text=df['Cluster_Label'] if 'Cluster_Label' in df.columns else df['Cluster_KMeans'],
                hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'
            ))
            f3.update_layout(
                title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': .5, 
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                height=650,
                scene=dict(
                    xaxis=dict(
                        title='<b>Recency (days)</b>', 
                        backgroundcolor='rgba(245,247,250,.4)', 
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    yaxis=dict(
                        title='<b>Frequency</b>', 
                        backgroundcolor='rgba(245,247,250,.4)', 
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    zaxis=dict(
                        title='<b>Monetary (£)</b>', 
                        backgroundcolor='rgba(245,247,250,.4)', 
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
                ),
                paper_bgcolor='rgba(245,247,250,.4)',
                margin=dict(t=80, b=40, l=40, r=40)
            )
        else:
            f3 = go.Figure()
            f3.update_layout(
                title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': .5, 
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                height=650,
                annotations=[dict(
                    text='RFM data not available',
                    x=.5, y=.5, 
                    font={'size': 16, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                    showarrow=False
                )]
            )
    except Exception as e:
        f3 = go.Figure()
        f3.update_layout(
            title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': .5, 
                   'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=650,
            annotations=[dict(
                text=f'Error: {str(e)[:50]}',
                x=.5, y=.5, 
                font={'size': 14, 'color': 'red', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )]
        )
    
    try:
        # Chart 4-6: Histograms
        def mh(d, col, ttl, clr):
            if col not in d.columns:
                fig = go.Figure()
                fig.update_layout(
                    title={'text': f"<b>{ttl}</b>", 'x': .5, 
                           'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                    height=340,
                    annotations=[dict(
                        text=f'{col} data not available',
                        x=.5, y=.5, 
                        font={'size': 14, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                        showarrow=False
                    )]
                )
                return fig
            
            fig = go.Figure(go.Histogram(
                x=d[col], 
                nbinsx=35,
                marker=dict(
                    color=clr, 
                    line=dict(color='white', width=2), 
                    opacity=.85
                )
            ))
            fig.update_layout(
                title={'text': f"<b>{ttl}</b>", 'x': .5, 
                       'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                xaxis={
                    'title': f'<b>{col}</b>', 
                    'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 
                    'gridcolor': 'rgba(0,0,0,0.05)'
                },
                yaxis={
                    'title': '<b>Count</b>', 
                    'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 
                    'gridcolor': 'rgba(0,0,0,0.05)'
                },
                height=340,
                plot_bgcolor='rgba(245,247,250,.5)',
                margin=dict(t=70, b=50, l=60, r=40)
            )
            return fig
        
        f4 = mh(df, 'Recency', '⏰ Recency Distribution', '#ff6b6b')
        f5 = mh(df, 'Frequency', '🔄 Frequency Distribution', '#4ecdc4')
        f6 = mh(df, 'Monetary', '💵 Monetary Distribution', '#45b7d1')
    except Exception as e:
        f4 = go.Figure()
        f4.update_layout(
            title={'text': "<b>⏰ Recency Distribution</b>", 'x': .5, 
                   'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=340
        )
        f5 = go.Figure()
        f5.update_layout(
            title={'text': "<b>🔄 Frequency Distribution</b>", 'x': .5, 
                   'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=340
        )
        f6 = go.Figure()
        f6.update_layout(
            title={'text': "<b>💵 Monetary Distribution</b>", 'x': .5, 
                   'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            height=340
        )
    
    try:
        # Chart 7: Segment Summary Table
        required_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score', 'Cluster_Label']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            # Create a simple table with available data
            tb = df.groupby('Cluster_Label' if 'Cluster_Label' in df.columns else 'Cluster_KMeans').size().reset_index(name='Count')
            
            f7 = go.Figure(go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>'],
                    fill_color='#667eea',
                    font=dict(color='white', size=13, family='Inter, Poppins'),
                    align='center',
                    height=42,
                    line=dict(color='white', width=2)
                ),
                cells=dict(
                    values=[
                        tb.iloc[:, 0],
                        tb['Count']
                    ],
                    fill_color=[['white', '#f8f9fc']*len(tb)],
                    align='center',
                    font={'size': 12, 'family': 'Inter, Poppins'},
                    height=38,
                    line=dict(color='#e0e0e0', width=1)
                )
            ))
        else:
            tb = df.groupby('Cluster_Label').agg({
                'Recency': 'mean', 
                'Frequency': 'mean', 
                'Monetary': 'mean', 
                'AvgOrderValue': 'mean', 
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            tb['Count'] = df.groupby('Cluster_Label').size().values
            
            f7 = go.Figure(go.Table(
                header=dict(
                    values=[
                        '<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                        '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'
                    ],
                    fill_color='#667eea',
                    font=dict(color='white', size=13, family='Inter, Poppins'),
                    align='center',
                    height=42,
                    line=dict(color='white', width=2)
                ),
                cells=dict(
                    values=[
                        tb['Cluster_Label'],
                        tb['Count'],
                        [f"{v:.0f}d" for v in tb['Recency']],
                        tb['Frequency'].round(1),
                        [f"£{v:,.0f}" for v in tb['Monetary']],
                        [f"£{v:.0f}" for v in tb['AvgOrderValue']],
                        tb['RFM_Score']
                    ],
                    fill_color=[['white', '#f8f9fc']*len(tb)],
                    align='center',
                    font={'size': 12, 'family': 'Inter, Poppins'},
                    height=38,
                    line=dict(color='#e0e0e0', width=1)
                )
            ))
        
        f7.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
    except Exception as e:
        f7 = go.Figure()
        f7.update_layout(
            height=380,
            margin=dict(t=20, b=20, l=20, r=20),
            annotations=[dict(
                text=f'Table error: {str(e)[:50]}',
                x=.5, y=.5, 
                font={'size': 14, 'color': 'red', 'family': 'Inter, Poppins'}, 
                showarrow=False
            )]
        )
    
    return f1, f2, f3, f4, f5, f6, f7

# Layout utama Streamlit
def main():
    # Container utama
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="hdr">
        <h1 class="title">🎯 Customer Intelligence Hub</h1>
        <p class="sub">Customer Segmentation for Personalized Retail Marketing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="met">
            <div class="met-icon">👥</div>
            <div class="met-val">{len(rfm):,}</div>
            <div class="met-lbl">Customers</div>
            <div class="met-sub">Active Database</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="met">
            <div class="met-icon">🎯</div>
            <div class="met-val">{rfm['Cluster_KMeans'].nunique()}</div>
            <div class="met-lbl">Segments</div>
            <div class="met-sub">AI-Classified</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
        avg_rev = rfm['Monetary'].mean() if 'Monetary' in rfm.columns else 0
        st.markdown(f"""
        <div class="met">
            <div class="met-icon">💰</div>
            <div class="met-val">£{total_rev/1e6:.2f}M</div>
            <div class="met-lbl">Revenue</div>
            <div class="met-sub">Avg £{avg_rev:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_order = rfm['AvgOrderValue'].mean() if 'AvgOrderValue' in rfm.columns else 0
        max_order = rfm['AvgOrderValue'].max() if 'AvgOrderValue' in rfm.columns else 0
        st.markdown(f"""
        <div class="met">
            <div class="met-icon">📈</div>
            <div class="met-val">£{avg_order:.0f}</div>
            <div class="met-lbl">Avg Order</div>
            <div class="met-sub">Peak £{max_order:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
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
                key="rfm_filter",
                disabled=True
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
