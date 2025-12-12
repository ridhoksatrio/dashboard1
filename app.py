import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Customer Intelligence Hub", layout="wide")

# ---- Configuration / helper data ----
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# ---- Utilities ----
@st.cache_data(show_spinner=False)
def load_data():
    # Try both filenames to be flexible (same logic as original)
    try:
        df = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except Exception:
        df = pd.read_csv('final_customer_segments.csv', index_col=0)
    return df


def get_strat(cid, data):
    cd = data[data['Cluster_KMeans'] == cid]
    r,f,m = cd['Recency'].mean(), cd['Frequency'].mean(), cd['Monetary'].mean()
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

# ---- Load data ----
rfm = load_data()
st.write(f"✅ {len(rfm):,} customers loaded")

# Build profiles and labels
profs = {}
for c in sorted(rfm['Cluster_KMeans'].unique()):
    p = get_strat(c, rfm)
    profs[c] = p
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']

colors = {f"{p['name'][:2]} {p['name'][2:]} (C{c})": p['color'] for c, p in profs.items()}

# ---- Sidebar filters ----
st.sidebar.header("🎛️ Smart Filters")
segment_options = ['all'] + sorted(list(profs.keys()))
seg_map = {'all':'🌐 All Segments'}
for c,p in profs.items():
    label = p['name']
    if p['name'] == '🏆 Champions' and c in champion_details:
        label = f"{p['name']} - {champion_details[c]['tier']}"
    seg_map[c] = label

selected_seg = st.sidebar.selectbox("🎨 Segment Filter", options=segment_options, format_func=lambda x: seg_map[x])
rf_min = int(rfm['RFM_Score'].min())
rf_max = int(rfm['RFM_Score'].max())
selected_rfm = st.sidebar.slider("📊 RFM Score Range", min_value=rf_min, max_value=rf_max, value=(rf_min, rf_max))
selected_prio = st.sidebar.selectbox("🔥 Priority Level", options=['all','CRITICAL','URGENT','HIGH','MEDIUM'], index=0)

# ---- Filter dataframe ----
df = rfm[(rfm['RFM_Score'] >= selected_rfm[0]) & (rfm['RFM_Score'] <= selected_rfm[1])]
if selected_seg != 'all':
    df = df[df['Cluster_KMeans'] == selected_seg]
if selected_prio != 'all':
    df = df[df['Priority'] == selected_prio]

# ---- Layout: Header & Metrics ----
st.markdown("""
# 🎯 Customer Intelligence Hub
**Customer Segmentation for Personalized Retail Marketing**
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Customers", f"{len(rfm):,}")
col2.metric("🎯 Segments", f"{rfm['Cluster_KMeans'].nunique()}")
col3.metric("💰 Revenue", f"£{rfm['Monetary'].sum()/1e6:.2f}M", delta=f"Avg £{rfm['Monetary'].mean():.0f}")
col4.metric("📈 Avg Order", f"£{rfm['AvgOrderValue'].mean():.0f}", delta=f"Peak £{rfm['AvgOrderValue'].max():.0f}")

# ---- Charts ----
# Chart 1: Customer Distribution Pie
cc = df['Cluster_Label'].value_counts()
if len(cc) == 0:
    st.warning("No data for the selected filters. Adjust filters to see charts.")
else:
    f1 = go.Figure(go.Pie(labels=cc.index, values=cc.values, hole=.68,
                          marker=dict(colors=[colors.get(l,'#95A5A6') for l in cc.index], line=dict(color='white', width=5)),
                          textfont=dict(size=14, family='Inter, Poppins'),
                          textposition='outside',
                          pull=[0.05]*len(cc)))
    f1.update_layout(title={'text':"<b>🎯 Customer Distribution</b>", 'x':.5, 'font':{'size':20}}, height=420,
                     annotations=[dict(text=f'<b>{len(df):,}</b><br><span style="font-size:14px">Customers</span>', x=.5, y=.5, showarrow=False)],
                     margin=dict(t=80,b=40,l=40,r=40))

    f2_rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
    f2 = go.Figure(go.Bar(x=f2_rv.values, y=f2_rv.index, orientation='h',
                          marker=dict(color=f2_rv.values, colorscale='Sunset', line=dict(color='white', width=3)),
                          text=[f'£{v/1000:.1f}K' for v in f2_rv.values], textposition='outside'))
    f2.update_layout(title={'text':"<b>💰 Revenue by Segment</b>", 'x':.5, 'font':{'size':20}}, xaxis={'title':'<b>Revenue (£)</b>'}, height=420,
                     plot_bgcolor='rgba(245,247,250,.6)', margin=dict(t=80,b=60,l=140,r=60))

    f3 = go.Figure(go.Scatter3d(x=df['Recency'], y=df['Frequency'], z=df['Monetary'], mode='markers',
                                marker=dict(size=7, color=df['Cluster_KMeans'], colorscale='Rainbow', showscale=True, line=dict(width=.8, color='white'), opacity=.88,
                                            colorbar=dict(title='Cluster', thickness=20, len=0.7)),
                                text=df['Cluster_Label'], hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'))
    f3.update_layout(title={'text':"<b>📈 3D RFM Customer Analysis</b>", 'x':.5, 'font':{'size':20}}, height=650,
                     scene=dict(xaxis=dict(title='<b>Recency (days)</b>'), yaxis=dict(title='<b>Frequency</b>'), zaxis=dict(title='<b>Monetary (£)</b>'), camera=dict(eye=dict(x=1.5,y=1.5,z=1.3))),
                     paper_bgcolor='rgba(245,247,250,.4)', margin=dict(t=80,b=40,l=40,r=40))

    def mh(d, col, ttl, clr):
        fig = go.Figure(go.Histogram(x=d[col], nbinsx=35, marker=dict(color=clr, line=dict(color='white', width=2), opacity=.85)))
        fig.update_layout(title={'text':f"<b>{ttl}</b>", 'x':.5, 'font':{'size':18}}, xaxis={'title':f'<b>{col}</b>'}, yaxis={'title':'<b>Count</b>'}, height=340,
                          plot_bgcolor='rgba(245,247,250,.5)', margin=dict(t=70,b=50,l=60,r=40))
        return fig

    f4 = mh(df, 'Recency', '⏰ Recency Distribution', '#ff6b6b')
    f5 = mh(df, 'Frequency', '🔄 Frequency Distribution', '#4ecdc4')
    f6 = mh(df, 'Monetary', '💵 Monetary Distribution', '#45b7d1')

    tb = df.groupby('Cluster_Label').agg({'Recency':'mean','Frequency':'mean','Monetary':'mean','AvgOrderValue':'mean','RFM_Score':'mean'}).round(1).reset_index()
    tb['Count'] = df.groupby('Cluster_Label').size().values

    f7 = go.Figure(go.Table(
        header=dict(values=['<b>Segment</b>','<b>Count</b>','<b>Recency</b>','<b>Frequency</b>','<b>Monetary</b>','<b>Avg Order</b>','<b>RFM Score</b>'],
                    fill_color='#667eea', font=dict(color='white', size=13), align='center', height=42, line=dict(color='white', width=2)),
        cells=dict(values=[tb['Cluster_Label'], tb['Count'], [f"{v:.0f}d" for v in tb['Recency']], tb['Frequency'].round(1), [f"£{v:,.0f}" for v in tb['Monetary']], [f"£{v:.0f}" for v in tb['AvgOrderValue']], tb['RFM_Score']],
                   fill_color=[['white','#f8f9fc'] * len(tb)], align='center', font={'size':12}, height=38, line=dict(color='#e0e0e0', width=1))))
    f7.update_layout(height=380, margin=dict(t=20,b=20,l=20,r=20))

    # Display charts in a grid
    with st.container():
        st.plotly_chart(f1, use_container_width=True)
        st.plotly_chart(f2, use_container_width=True)
        st.plotly_chart(f3, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(f4, use_container_width=True)
    c2.plotly_chart(f5, use_container_width=True)
    c3.plotly_chart(f6, use_container_width=True)

    st.plotly_chart(f7, use_container_width=True)

# ---- Champion Breakdown ----
champion_clusters = [c for c in df['Cluster_KMeans'].unique() if profs[c]['name'] == '🏆 Champions']
if len(champion_clusters) > 0:
    st.markdown("## 🏆 Champion Segments Breakdown")
    st.markdown("Understanding the different Champion tiers and characteristics.")
    cols = st.columns(2)
    i = 0
    for cid in sorted(champion_clusters):
        if cid in champion_details:
            det = champion_details[cid]
            with cols[i % 2]:
                st.metric(f"Champion C{cid}", det['tier'])
                st.write(det['desc'])
                st.info(f"📊 Characteristics: {det['char']}")
            i += 1

# ---- Strategy Cards ----
st.markdown("## 🎯 Growth Strategies")
strategy_cols = st.columns(2)
idx = 0
for cid, p in profs.items():
    if selected_seg == 'all' or selected_seg == cid:
        col = strategy_cols[idx % 2]
        with col:
            st.markdown(f"### {p['name']}  |  **{p['priority']}**")
            st.write(f"**{p['strategy']} Strategy**")
            st.write("**Key Tactics**")
            for t in p['tactics']:
                st.write(f"- {t}")
            st.write("**Target KPIs**")
            for k in p['kpis']:
                st.write(f"- {k}")
            b1, b2 = st.columns(2)
            with b1:
                st.write("**Budget Allocation**")
                st.subheader(p['budget'])
            with b2:
                st.write("**ROI Target**")
                st.subheader(p['roi'])
        idx += 1

# ---- AI Insights ----
st.markdown("## 🧠 AI-Powered Insights & Recommendations")
if len(df) > 0:
    top_rev = df.groupby('Cluster_Label')['Monetary'].sum().idxmax()
    largest_group = df['Cluster_Label'].value_counts().idxmax()
    largest_count = df['Cluster_Label'].value_counts().max()
    best_aov = df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax()
    best_aov_val = df.groupby('Cluster_Label')['AvgOrderValue'].mean().max()
    most_freq = df.groupby('Cluster_Label')['Frequency'].mean().idxmax()
    most_freq_val = df.groupby('Cluster_Label')['Frequency'].mean().max()

    st.write(f"- 🏆 Highest Revenue: **{top_rev}**")
    st.write(f"- 👥 Largest Group: **{largest_group}** ({largest_count:,} customers)")
    st.write(f"- 💰 Best AOV: **{best_aov}** (£{best_aov_val:.0f})")
    st.write(f"- 🔄 Most Frequent: **{most_freq}** ({most_freq_val:.1f} orders)")

    st.write("### 💡 Smart Recommendations")
    st.write("- 🎯 Prioritize high-value segment retention programs")
    st.write("- 📧 Launch win-back campaigns for dormant customers")
    st.write("- 🚀 Accelerate potential customer nurturing flows")
    st.write("- 💎 Create exclusive VIP experiences for champions")
    st.write("- 📈 Implement cross-sell strategies for loyal segments")
else:
    st.info("No insights available — adjust filters to include data")

# ---- Footer / Notes ----
st.markdown("---")
st.caption("Built with Streamlit — convert from Dash. To run locally: `streamlit run streamlit_customer_dashboard.py`")
