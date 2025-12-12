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
            st.error("Data file tidak ditemukan. Menggunakan sample data.")
            np.random.seed(42)
            n = 1000
            rfm = pd.DataFrame({
                'Recency': np.random.randint(1, 365, n),
                'Frequency': np.random.randint(1, 50, n),
                'Monetary': np.random.uniform(100, 50000, n),
                'AvgOrderValue': np.random.uniform(50, 500, n),
                'RFM_Score': np.random.randint(100, 600, n),
                'Cluster_KMeans': np.random.choice([0,1,2,3,4,5], n)
            })
            rfm.index = [f"CUST_{i:04d}" for i in range(n)]

    required_cols = ['Recency','Frequency','Monetary','AvgOrderValue','RFM_Score','Cluster_KMeans']
    for col in required_cols:
        if col not in rfm.columns:
            rfm[col] = 0

    return rfm

rfm = load_data()

# Cluster Strategies
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)',
                  'color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum',
                  'tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],
                  'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)',
              'color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost',
              'tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],
              'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)',
            'color':'#f093fb','priority':'CRITICAL','strategy':'Value Max',
            'tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],
            'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)',
                'color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back',
                'tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],
                'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)',
                  'color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert',
                  'tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],
                  'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)',
                 'color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage',
                 'tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],
                 'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

def get_strat(cid, data):
    cd = data[data['Cluster_KMeans'] == cid]
    if len(cd) == 0:
        return {**strats['standard'], 'cluster_id': cid}

    r, f, m = cd['Recency'].mean(), cd['Frequency'].mean(), cd['Monetary'].mean()

    if r < 50 and f > 10 and m > 1000: s = 'champions'
    elif r < 50 and f > 5: s = 'loyal'
    elif m > 1500: s = 'big'
    elif r > 100: s = 'dormant'
    elif r < 50 and f < 5: s = 'potential'
    else: s = 'standard'
    return {**strats[s], 'cluster_id': cid}

@st.cache_data
def init_data(rfm):
    profs = {}
    for c in rfm['Cluster_KMeans'].unique():
        p = get_strat(c, rfm)
        profs[c] = p
        rfm.loc[rfm['Cluster_KMeans']==c,'Cluster_Label'] = f"{p['name']} (C{c})"
        rfm.loc[rfm['Cluster_KMeans']==c,'Priority'] = p['priority']

    colors = {f"{p['name']} (C{c})": p['color'] for c,p in profs.items()}
    return profs, colors, rfm

profs, colors, rfm = init_data(rfm)

# CSS
st.markdown("""
<style>
* {margin:0;padding:0;box-sizing:border-box}
body {font-family:'Inter',sans-serif;background:#f3f5f8}
.stApp {background:transparent}

.title {font-size:3rem;font-weight:900;text-align:center;margin-bottom:10px}
.sub {color:#555;text-align:center;font-size:1.2rem;margin-bottom:40px}

.metrics {display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:30px 0}
.met {background:white;padding:25px;border-radius:15px;text-align:center;
      box-shadow:0 4px 12px rgba(0,0,0,0.08)}
.met-val {font-size:2.4rem;font-weight:800;margin:10px 0}
.met-lbl {text-transform:uppercase;font-size:.9rem;color:#777}

.chart-box {background:white;padding:30px;border-radius:18px;
            box-shadow:0 6px 22px rgba(0,0,0,0.08);margin-bottom:30px}

.strat-card {padding:25px;border-radius:18px;color:white;margin-bottom:25px}
.strat-hdr {display:flex;justify-content:space-between;font-size:1.5rem;font-weight:800;margin-bottom:14px}
.tact {padding:10px 14px;margin:6px 0;background:rgba(255,255,255,.15);border-radius:10px}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 class='title'>Customer Intelligence Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Advanced RFM + Cluster Analysis Dashboard</p>", unsafe_allow_html=True)

# TOP METRICS
total_customers = len(rfm)
avg_recency = rfm['Recency'].mean()
avg_frequency = rfm['Frequency'].mean()
avg_monetary = rfm['Monetary'].mean()

st.markdown("<div class='metrics'>", unsafe_allow_html=True)
st.markdown(f"""
<div class='met'>
    <div class='met-lbl'>Total Customers</div>
    <div class='met-val'>{total_customers:,}</div>
</div>
<div class='met'>
    <div class='met-lbl'>Avg Recency</div>
    <div class='met-val'>{avg_recency:.1f} days</div>
</div>
<div class='met'>
    <div class='met-lbl'>Avg Frequency</div>
    <div class='met-val'>{avg_frequency:.1f}</div>
</div>
<div class='met'>
    <div class='met-lbl'>Avg Monetary</div>
    <div class='met-val'>${avg_monetary:,.2f}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# TABS
tab1, tab2, tab3 = st.tabs(["📊 RFM Distribution", "👥 Cluster Explorer", "🎯 Strategy"])

# TAB 1 — RFM DISTRIBUTIONS
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig_r = go.Figure(data=[go.Histogram(x=rfm['Recency'])])
        fig_r.update_layout(title="Recency Distribution", bargap=0.1)
        st.plotly_chart(fig_r, use_container_width=True)

    with col2:
        fig_f = go.Figure(data=[go.Histogram(x=rfm['Frequency'])])
        fig_f.update_layout(title="Frequency Distribution", bargap=0.1)
        st.plotly_chart(fig_f, use_container_width=True)

    fig_m = go.Figure(data=[go.Histogram(x=rfm['Monetary'])])
    fig_m.update_layout(title="Monetary Distribution", bargap=0.1)
    st.plotly_chart(fig_m, use_container_width=True)

    st.dataframe(rfm.head(50))

# TAB 2 — CLUSTER EXPLORATION
with tab2:
    selected_cluster = st.selectbox(
        "Select Cluster",
        sorted(rfm['Cluster_KMeans'].unique())
    )
    dfc = rfm[rfm['Cluster_KMeans'] == selected_cluster]

    st.write(f"### Cluster {selected_cluster} Summary")
    st.dataframe(dfc)

# TAB 3 — STRATEGY
with tab3:
    for cid, p in profs.items():
        st.markdown(f"""
        <div class='strat-card' style='background:{p["grad"]};'>
            <div class='strat-hdr'>
                <div>{p['name']} (C{cid})</div>
                <div>{p['priority']}</div>
            </div>
            <h4>{p['strategy']}</h4>
            <b>Tactics:</b>
        """, unsafe_allow_html=True)

        for t in p['tactics']:
            st.markdown(f"<div class='tact'>{t}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
