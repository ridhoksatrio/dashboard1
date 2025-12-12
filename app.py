# app_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Customer Intelligence Hub", layout="wide")

# ---------------------
# Load & Prepare Data
# ---------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except Exception:
        df = pd.read_csv('final_customer_segments.csv', index_col=0)
    return df

rfm = load_data()
st.experimental_set_query_params()  # no-op just to make interactive

# quick status
st.write(f"✅ **{len(rfm):,} customers loaded**")

# ---------------------
# Static data structures (same as original)
# ---------------------
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

def get_strat(cid,data):
    cd=data[data['Cluster_KMeans']==cid]
    r,f,m=cd['Recency'].mean(),cd['Frequency'].mean(),cd['Monetary'].mean()
    if r<50 and f>10 and m>1000: s='champions'
    elif r<50 and f>5: s='loyal'
    elif m>1500: s='big'
    elif r>100: s='dormant'
    elif r<50 and f<5: s='potential'
    else: s='standard'
    return {**strats[s],'cluster_id':cid}

profs={}
for c in sorted(rfm['Cluster_KMeans'].unique()):
    p=get_strat(c,rfm)
    profs[c]=p
    rfm.loc[rfm['Cluster_KMeans']==c,'Cluster_Label']=f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans']==c,'Priority']=p['priority']

colors={f"{p['name'][:2]} {p['name'][2:]} (C{c})":p['color'] for c,p in profs.items()}

# ---------------------
# Inject CSS (from original app.index_string style block)
# ---------------------
# Note: Streamlit may not support all CSS the exact same way, but this preserves look & feel
css = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Poppins',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);padding:16px;min-height:100vh}
.dash{background:rgba(255,255,255,0.98);border-radius:32px;padding:40px;box-shadow:0 40px 100px rgba(0,0,0,0.4);animation:fadeIn .8s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.hdr{text-align:center;padding:28px 24px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:24px;margin-bottom:36px;position:relative;overflow:hidden;box-shadow:0 15px 40px rgba(102,126,234,0.35)}
.title{font-size:34px;font-weight:900;color:#fff;text-shadow:4px 4px 8px rgba(0,0,0,.35);margin:0;letter-spacing:-1.5px;line-height:1.1}
.sub{color:rgba(255,255,255,.95);font-size:16px;margin-top:10px;font-weight:500;letter-spacing:0.5px}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-bottom:36px}
.met{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:22px;padding:24px;text-align:center;color:#fff;box-shadow:0 15px 40px rgba(102,126,234,.45);transition:all .4s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden}
.met-icon{font-size:28px;margin-bottom:8px}
.met-val{font-size:28px;font-weight:900;margin:8px 0}
.met-lbl{font-size:12px;text-transform:uppercase;letter-spacing:2.5px;font-weight:700;margin-bottom:6px}
.filt{background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);border-radius:22px;padding:20px;margin-bottom:32px;box-shadow:0 10px 30px rgba(0,0,0,.12)}
.filt-t{font-size:18px;font-weight:800;color:#2c3e50;margin-bottom:12px;display:flex;align-items:center;gap:12px}
.charts{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;margin-bottom:26px}
.chart{background:#fff;border-radius:16px;padding:12px;box-shadow:0 10px 35px rgba(0,0,0,.08);transition:all .35s ease;border:3px solid transparent}
.chart-full{grid-column:1/-1}
.strat-g{display:grid;grid-template-columns:repeat(2,1fr);gap:26px}
.strat{border-radius:12px;padding:18px;color:#fff;box-shadow:0 15px 40px rgba(0,0,0,.22);transition:all .45s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden}
.champ-break{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:16px;padding:18px;color:#fff;margin:16px 0}
.champ-card{background:rgba(255,255,255,.16);border-radius:8px;padding:12px;backdrop-filter:blur(10px);margin-bottom:10px}
.ins{background:linear-gradient(135deg,#4facfe 0%,#00f2fe 100%);border-radius:16px;padding:18px;color:#fff;margin:16px 0}
@media(max-width:1200px){
    .metrics,.charts,.strat-g{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:768px){
    .metrics,.charts,.strat-g{grid-template-columns:1fr}
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------------
# Header
# ---------------------
st.markdown('<div class="dash">', unsafe_allow_html=True)
st.markdown('<div class="hdr"><h1 class="title">🎯 Customer Intelligence Hub</h1><p class="sub">Customer Segmentation for Personalized Retail Marketing</p></div>', unsafe_allow_html=True)

# ---------------------
# Metrics (top)
# ---------------------
cols = st.columns(4)
with cols[0]:
    st.markdown('<div class="met"><div class="met-icon">👥</div><div class="met-val">{:,}</div><div class="met-lbl">Customers</div><div>Active Database</div></div>'.format(len(rfm)), unsafe_allow_html=True)
with cols[1]:
    st.markdown('<div class="met"><div class="met-icon">🎯</div><div class="met-val">{}</div><div class="met-lbl">Segments</div><div>AI-Classified</div></div>'.format(rfm['Cluster_KMeans'].nunique()), unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="met"><div class="met-icon">💰</div><div class="met-val">£{:.2f}M</div><div class="met-lbl">Revenue</div><div>Avg £{:.0f}</div></div>'.format(rfm['Monetary'].sum()/1e6, rfm['Monetary'].mean()), unsafe_allow_html=True)
with cols[3]:
    st.markdown('<div class="met"><div class="met-icon">📈</div><div class="met-val">£{:.0f}</div><div class="met-lbl">Avg Order</div><div>Peak £{:.0f}</div></div>'.format(rfm['AvgOrderValue'].mean(), rfm['AvgOrderValue'].max()), unsafe_allow_html=True)

# ---------------------
# Filters
# ---------------------
st.markdown('<div class="filt"><div class="filt-t">🎛️ Smart Filters</div>', unsafe_allow_html=True)
fcols = st.columns(3)
# segment options: 'all' + cluster ids
seg_options = ['all'] + [int(c) for c in profs.keys()]
seg_labels = { 'all': '🌐 All Segments' }
for c,p in profs.items():
    label = p['name']
    if p['name'] == '🏆 Champions' and c in champion_details:
        # add tier name to label (similar to original)
        label = f"{p['name']} - {champion_details[c]['tier']}"
    seg_labels[c] = label

with fcols[0]:
    cf = st.selectbox("🎨 Segment Filter", options=seg_options, format_func=lambda x: seg_labels[x], index=0)
with fcols[1]:
    rf_min = int(rfm['RFM_Score'].min())
    rf_max = int(rfm['RFM_Score'].max())
    rr = st.slider("📊 RFM Score Range", min_value=rf_min, max_value=rf_max, value=(rf_min, rf_max))
with fcols[2]:
    pf = st.selectbox("🔥 Priority Level", options=['all','CRITICAL','URGENT','HIGH','MEDIUM'], index=0)

st.markdown('</div>', unsafe_allow_html=True)  # close filt div

# ---------------------
# Filter data according to widgets
# ---------------------
df = rfm[(rfm['RFM_Score']>=rr[0]) & (rfm['RFM_Score']<=rr[1])]
if cf != 'all':
    df = df[df['Cluster_KMeans']==cf]
if pf != 'all':
    df = df[df['Priority']==pf]

# ---------------------
# Tabs (Analytics, Strategies, Insights)
# ---------------------
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard","🎯 Growth Strategies","💡 AI Insights"])

# ----- Tab 1: Analytics Dashboard -----
with tab1:
    st.markdown('<div class="charts">', unsafe_allow_html=True)

    # Chart 1: Customer Distribution Pie
    cc = df['Cluster_Label'].value_counts()
    f1 = go.Figure(go.Pie(labels=cc.index,values=cc.values,hole=.68,
        marker=dict(colors=[colors.get(l,'#95A5A6') for l in cc.index],
                   line=dict(color='white',width=5)),
        textfont=dict(size=14,family='Inter, Poppins',weight=700),
        textposition='outside',
        pull=[0.05]*len(cc)))
    f1.update_layout(title={'text':"<b>🎯 Customer Distribution</b>",'x':.5,'font':{'size':20,'family':'Inter, Poppins','color':'#2c3e50'}},
        height=420,
        annotations=[dict(text=f'<b>{len(df):,}</b><br><span style="font-size:14px">Customers</span>',
                         x=.5,y=.5,font={'size':24,'color':'#667eea','family':'Inter, Poppins'},showarrow=False)],
        margin=dict(t=80,b=40,l=40,r=40))

    # Chart 2: Revenue by Segment
    rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
    f2 = go.Figure(go.Bar(x=rv.values,y=rv.index,orientation='h',
        marker=dict(color=rv.values,colorscale='Sunset',
                   line=dict(color='white',width=3)),
        text=[f'£{v/1000:.1f}K' for v in rv.values],
        textposition='outside',
        textfont={'size':13,'weight':700,'family':'Inter, Poppins'}))
    f2.update_layout(title={'text':"<b>💰 Revenue by Segment</b>",'x':.5,'font':{'size':20,'family':'Inter, Poppins','color':'#2c3e50'}},
        xaxis={'title':'<b>Revenue (£)</b>','titlefont':{'size':14,'family':'Inter, Poppins'},'gridcolor':'rgba(0,0,0,0.05)'},
        yaxis={'titlefont':{'size':14,'family':'Inter, Poppins'}},
        height=420,
        plot_bgcolor='rgba(245,247,250,.6)',
        margin=dict(t=80,b=60,l=140,r=60))

    # layout: place f1 and f2 side by side
    left_col, right_col = st.columns(2)
    with left_col:
        st.plotly_chart(f1, use_container_width=True, config={'displayModeBar': False})
    with right_col:
        st.plotly_chart(f2, use_container_width=True, config={'displayModeBar': False})

    st.markdown('</div>', unsafe_allow_html=True)  # close charts

    # Chart 3: 3D RFM Analysis (full width)
    f3 = go.Figure(go.Scatter3d(x=df['Recency'],y=df['Frequency'],z=df['Monetary'],mode='markers',
        marker=dict(size=7,color=df['Cluster_KMeans'],colorscale='Rainbow',showscale=True,
                   line=dict(width=.8,color='white'),opacity=.88,
                   colorbar=dict(title='Cluster',thickness=20,len=0.7)),
        text=df['Cluster_Label'],
        hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'))
    f3.update_layout(title={'text':"<b>📈 3D RFM Customer Analysis</b>",'x':.5,'font':{'size':20,'family':'Inter, Poppins','color':'#2c3e50'}},
        height=650,
        scene=dict(xaxis=dict(title='<b>Recency (days)</b>',backgroundcolor='rgba(245,247,250,.4)',gridcolor='rgba(0,0,0,0.08)'),
                  yaxis=dict(title='<b>Frequency</b>',backgroundcolor='rgba(245,247,250,.4)',gridcolor='rgba(0,0,0,0.08)'),
                  zaxis=dict(title='<b>Monetary (£)</b>',backgroundcolor='rgba(245,247,250,.4)',gridcolor='rgba(0,0,0,0.08)'),
                  camera=dict(eye=dict(x=1.5,y=1.5,z=1.3))),
        paper_bgcolor='rgba(245,247,250,.4)',
        margin=dict(t=80,b=40,l=40,r=40))

    st.plotly_chart(f3, use_container_width=True, config={'displayModeBar': False})

    # Charts 4-6: histograms side by side
    def mh(d,col,ttl,clr):
        fig=go.Figure(go.Histogram(x=d[col],nbinsx=35,
            marker=dict(color=clr,line=dict(color='white',width=2),opacity=.85)))
        fig.update_layout(title={'text':f"<b>{ttl}</b>",'x':.5,'font':{'size':18,'family':'Inter, Poppins','color':'#2c3e50'}},
            xaxis={'title':f'<b>{col}</b>','titlefont':{'size':13,'family':'Inter, Poppins'},'gridcolor':'rgba(0,0,0,0.05)'},
            yaxis={'title':'<b>Count</b>','titlefont':{'size':13,'family':'Inter, Poppins'},'gridcolor':'rgba(0,0,0,0.05)'},
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)',
            margin=dict(t=70,b=50,l=60,r=40))
        return fig

    f4 = mh(df,'Recency','⏰ Recency Distribution','#ff6b6b')
    f5 = mh(df,'Frequency','🔄 Frequency Distribution','#4ecdc4')
    f6 = mh(df,'Monetary','💵 Monetary Distribution','#45b7d1')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(f4, use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.plotly_chart(f5, use_container_width=True, config={'displayModeBar': False})
    with c3:
        st.plotly_chart(f6, use_container_width=True, config={'displayModeBar': False})

    # Chart 7: Segment Summary Table
    tb = df.groupby('Cluster_Label').agg({'Recency':'mean','Frequency':'mean','Monetary':'mean','AvgOrderValue':'mean','RFM_Score':'mean'}).round(1).reset_index()
    if not tb.empty:
        tb['Count'] = df.groupby('Cluster_Label').size().values
    else:
        tb['Count'] = []

    f7 = go.Figure(go.Table(
        header=dict(values=['<b>Segment</b>','<b>Count</b>','<b>Recency</b>','<b>Frequency</b>',
                           '<b>Monetary</b>','<b>Avg Order</b>','<b>RFM Score</b>'],
                   fill_color='#667eea',
                   font=dict(color='white',size=13,family='Inter, Poppins'),
                   align='center',
                   height=42,
                   line=dict(color='white',width=2)),
        cells=dict(values=[tb['Cluster_Label'] if not tb.empty else [],
                          tb['Count'] if not tb.empty else [],
                          [f"{v:.0f}d" for v in tb['Recency']] if not tb.empty else [],
                          tb['Frequency'].round(1) if not tb.empty else [],
                          [f"£{v:,.0f}" for v in tb['Monetary']] if not tb.empty else [],
                          [f"£{v:.0f}" for v in tb['AvgOrderValue']] if not tb.empty else [],
                          tb['RFM_Score'] if not tb.empty else []],
                  fill_color=[['white','#f8f9fc']*len(tb)] if not tb.empty else [['white']],
                  align='center',
                  font={'size':12,'family':'Inter, Poppins'},
                  height=38,
                  line=dict(color='#e0e0e0',width=1))))
    f7.update_layout(height=380,margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(f7, use_container_width=True, config={'displayModeBar': False})


# ----- Tab 2: Growth Strategies -----
with tab2:
    # Champion Breakdown Section (only show if champions present)
    champion_clusters = [c for c in df['Cluster_KMeans'].unique() if profs[c]['name'] == '🏆 Champions']
    if len(champion_clusters) > 0:
        st.markdown('<div class="champ-break">', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;"><h2>🏆 Champion Segments Breakdown</h2><p>Understanding the 4 Different Champion Tiers</p></div>', unsafe_allow_html=True)
        # display cards in two columns
        cols = st.columns(2)
        i = 0
        for cid in sorted(champion_clusters):
            if cid in champion_details:
                det = champion_details[cid]
                with cols[i % 2]:
                    st.markdown(f'<div class="champ-card"><div style="font-size:20px;font-weight:900">Champion C{cid}</div><div style="font-weight:800;margin-top:6px">🏅 {det["tier"]}</div><div style="margin-top:8px">{det["desc"]}</div><div style="margin-top:8px;background:rgba(255,255,255,.2);padding:6px;border-radius:6px;font-weight:600">📊 Characteristics: {det["char"]}</div></div>', unsafe_allow_html=True)
                i += 1
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No Champion segments in the current filter selection.")

    # Strategy Cards (show cards for each cluster)
    st.markdown('<div style="margin-top:18px"><h3>🎯 Growth Strategies by Segment</h3></div>', unsafe_allow_html=True)
    strat_cols = st.columns(2)
    idx = 0
    for cid,p in profs.items():
        if cf == 'all' or cf == cid:
            col = strat_cols[idx % 2]
            with col:
                # Use background gradient text via inline style (approximate)
                tactics_html = "".join([f'<div style="padding:8px;margin:6px 0;background:rgba(255,255,255,.18);border-radius:8px;font-weight:600">{t}</div>' for t in p['tactics']])
                kpis_html = "".join([f'<div style="padding:8px;margin:6px 0;background:rgba(255,255,255,.16);border-radius:8px;font-weight:700;text-align:center">{k}</div>' for k in p['kpis']])
                st.markdown(f'''
                <div class="strat" style="background:{p['grad']}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div style="font-size:18px;font-weight:900">{p['name']}</div>
                        <div style="padding:6px 12px;border-radius:12px;background:rgba(255,255,255,.25);font-weight:800">{p['priority']}</div>
                    </div>
                    <div style="font-weight:700;margin-top:8px">📋 {p['strategy']} Strategy</div>
                    <div style="margin-top:10px"><div style="font-weight:800">🎯 Key Tactics</div>{tactics_html}</div>
                    <div style="margin-top:10px"><div style="font-weight:800">📊 Target KPIs</div><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:6px">{kpis_html}</div></div>
                    <div style="display:flex;justify-content:space-between;margin-top:12px;background:rgba(255,255,255,.16);padding:8px;border-radius:8px">
                        <div style="text-align:center"><div style="font-size:12px">Budget Allocation</div><div style="font-weight:900">{p['budget']}</div></div>
                        <div style="text-align:center"><div style="font-size:12px">ROI Target</div><div style="font-weight:900">{p['roi']}</div></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            idx += 1

# ----- Tab 3: AI Insights -----
with tab3:
    st.markdown('<div class="ins">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;gap:16px;flex-wrap:wrap">', unsafe_allow_html=True)
    # Top Performers card
    if not df.empty:
        highest_revenue = df.groupby('Cluster_Label')['Monetary'].sum().idxmax()
        largest_group = df['Cluster_Label'].value_counts().idxmax()
        largest_group_count = df['Cluster_Label'].value_counts().max()
        best_aov_label = df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax()
        best_aov_val = df.groupby('Cluster_Label')['AvgOrderValue'].mean().max()
        most_freq = df.groupby('Cluster_Label')['Frequency'].mean().idxmax()
        most_freq_val = df.groupby('Cluster_Label')['Frequency'].mean().max()
    else:
        highest_revenue = largest_group = best_aov_label = most_freq = "N/A"
        largest_group_count = best_aov_val = most_freq_val = 0

    st.markdown(f'''
        <div class="ins-card" style="flex:1;min-width:280px">
            <div style="font-weight:800;font-size:18px;margin-bottom:8px">📊 Top Performers</div>
            <ul style="padding-left:18px;margin:0">
                <li>🏆 Highest Revenue: {highest_revenue}</li>
                <li>👥 Largest Group: {largest_group} ({largest_group_count:,} customers)</li>
                <li>💰 Best AOV: {best_aov_label} (£{best_aov_val:.0f})</li>
                <li>🔄 Most Frequent: {most_freq} ({most_freq_val:.1f} orders)</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

    # Recommendations card
    st.markdown('''
        <div class="ins-card" style="flex:1;min-width:280px">
            <div style="font-weight:800;font-size:18px;margin-bottom:8px">💡 Smart Recommendations</div>
            <ul style="padding-left:18px;margin:0">
                <li>🎯 Prioritize high-value segment retention programs</li>
                <li>📧 Launch win-back campaigns for dormant customers</li>
                <li>🚀 Accelerate potential customer nurturing flows</li>
                <li>💎 Create exclusive VIP experiences for champions</li>
                <li>📈 Implement cross-sell strategies for loyal segments</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# closing main dash div
st.markdown('</div>', unsafe_allow_html=True)
