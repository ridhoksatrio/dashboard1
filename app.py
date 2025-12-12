import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        return pd.read_csv("final_customer_segments (1).csv", index_col=0)
    except:
        return pd.read_csv("final_customer_segments.csv", index_col=0)

rfm = load_data()

# ---------------------------------------------------------
# STRATEGY DEFINITIONS
# ---------------------------------------------------------
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# ---------------------------------------------------------
# FUNCTION TO ASSIGN STRATEGY
# ---------------------------------------------------------
def get_strat(cid, data):
    cd = data[data["Cluster_KMeans"] == cid]
    r, f, m = cd["Recency"].mean(), cd["Frequency"].mean(), cd["Monetary"].mean()

    if r < 50 and f > 10 and m > 1000:
        s = "champions"
    elif r < 50 and f > 5:
        s = "loyal"
    elif m > 1500:
        s = "big"
    elif r > 100:
        s = "dormant"
    elif r < 50 and f < 5:
        s = "potential"
    else:
        s = "standard"

    return {**strats[s], "cluster_id": cid}

# ---------------------------------------------------------
# ENRICH DATA
# ---------------------------------------------------------
@st.cache_data
def init_data(rfm):
    profs = {}
    for c in rfm["Cluster_KMeans"].unique():
        p = get_strat(c, rfm)
        profs[c] = p
        label = f"{p['name']} (C{c})"
        rfm.loc[rfm["Cluster_KMeans"] == c, "Cluster_Label"] = label
        rfm.loc[rfm["Cluster_KMeans"] == c, "Priority"] = p["priority"]

    colors = {f"{p['name']} (C{c})": p["color"] for c, p in profs.items()}
    return profs, colors, rfm

profs, colors, rfm = init_data(rfm)

# ---------------------------------------------------------
# GLOBAL CSS (FULL & FIXED)
# ---------------------------------------------------------
st.markdown("""
<style>
body { font-family: 'Inter', sans-serif; }

/* HEADER */
.hdr {text-align:center;padding:30px;background:linear-gradient(135deg,#667eea,#764ba2);
      border-radius:25px;color:white;margin-bottom:35px;box-shadow:0 15px 40px rgba(102,126,234,.35);}
.title {font-size:3.4rem;font-weight:900;margin-bottom:8px;}
.sub {font-size:1.2rem;opacity:.9;}

/* METRICS */
.metrics {display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:35px;}
.met {background:white;border-radius:22px;padding:25px;text-align:center;
      box-shadow:0 10px 25px rgba(0,0,0,.15);}
.met-icon {font-size:40px;margin-bottom:10px;}
.met-val {font-size:2.5rem;font-weight:900;margin:5px 0;}

/* CHARTS */
.charts {display:grid;grid-template-columns:repeat(2,1fr);gap:20px;}
.chart {background:white;border-radius:22px;padding:25px;box-shadow:0 10px 25px rgba(0,0,0,.1);}
.chart-full {grid-column:1/ -1;}

/* STRATEGY CARDS */
.strat-g {display:grid;grid-template-columns:repeat(2,1fr);gap:22px;}
.strat {border-radius:24px;padding:30px;color:white;box-shadow:0 15px 40px rgba(0,0,0,.22);}
.strat-name {font-size:2rem;font-weight:900;margin-bottom:15px;}
.strat-sub {font-size:1.2rem;font-weight:700;margin-bottom:15px;}
.tact {background:rgba(255,255,255,.25);padding:12px;margin:8px 0;border-radius:12px;}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER UI
# ---------------------------------------------------------
st.markdown("""
<div class="hdr">
    <div class="title">Customer Intelligence Hub</div>
    <div class="sub">AI-Driven Targeting • Segmentation • Strategic Insights</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Customers", f"{len(rfm):,}")
m2.metric("Clusters", rfm["Cluster_KMeans"].nunique())
m3.metric("Avg Monetary", f"£{rfm['Monetary'].mean():,.0f}")
m4.metric("Avg Frequency", f"{rfm['Frequency'].mean():.1f}")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 RFM Overview", "🎯 Cluster Profiles", "🧠 Strategy Playbook"])

# ---------------------------------------------------------
# TAB 1 — RFM CHARTS
# ---------------------------------------------------------
with tab1:
    st.subheader("RFM Distribution")

    colA, colB = st.columns(2)

    with colA:
        fig = px.scatter(
            rfm,
            x="Recency",
            y="Monetary",
            color="Cluster_Label",
            title="Recency vs Monetary",
            color_discrete_map=colors
        )
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        fig = px.box(
            rfm,
            x="Cluster_Label",
            y="Frequency",
            color="Cluster_Label",
            title="Frequency Distribution",
            color_discrete_map=colors
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB 2 — CLUSTER PROFILES
# ---------------------------------------------------------
with tab2:
    st.subheader("Cluster Overview")

    cid = st.selectbox("Select Cluster:", sorted(rfm["Cluster_KMeans"].unique()))
    cluster_data = profs[cid]

    st.markdown(f"""
    <div class="strat" style="background:{cluster_data['grad']}">
        <div class="strat-name">{cluster_data['name']} (C{cid})</div>
        <div class="strat-sub">Priority: {cluster_data['priority']}</div>
        <div><b>Strategy:</b> {cluster_data['strategy']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("### RFM Averages")
    st.dataframe(rfm[rfm.Cluster_KMeans == cid][["Recency","Frequency","Monetary"]].mean())

# ---------------------------------------------------------
# TAB 3 — STRATEGY PLAYBOOK
# ---------------------------------------------------------
with tab3:
    st.subheader("AI-Recommended Actions")

    for cid, info in profs.items():
        st.markdown(f"""
        <div class="strat" style="background:{info['grad']}">
            <div class="strat-name">{info['name']} (C{cid})</div>
            <div class="strat-sub">Strategy: {info['strategy']}</div>

            <b>Tactics:</b>
        """, unsafe_allow_html=True)

        for t in info["tactics"]:
            st.markdown(f"<div class='tact'>{t}</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
