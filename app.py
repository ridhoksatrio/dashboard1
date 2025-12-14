import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# Streamlit page configuration
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

# Full details for each cluster type - WITHOUT HTML TAGS
cluster_full_details = {
    'Champions': {
        'characteristics': 'Very low recency<br>High frequency<br>Very high monetary',
        'strategy': 'Focus on retention and long-term value enhancement',
        'actions': 'Provide early access to products before general release<br>Assign dedicated customer manager for large transactions<br>Send premium gifts for transaction milestones<br>Invite to exclusive online or offline events<br>Create VIP referral program',
        'kpis': 'Retention above 95 percent<br>Upsell rate above 40 percent<br>Referral contribution above 30 percent'
    },
    'Loyal': {
        'characteristics': 'Low recency<br>High frequency<br>Medium monetary',
        'strategy': 'Increase loyalty to move up to Champions tier',
        'actions': 'Implement point-based loyalty tiers<br>Provide exclusive benefits via app or member account<br>Send birthday and anniversary promotions<br>Encourage referrals with direct incentives<br>Provide limited flash sale access',
        'kpis': 'Retention above 85 percent<br>Minimum 20 percent increase in purchase frequency<br>NPS above 8'
    },
    'Big Spenders': {
        'characteristics': 'Very high monetary<br>Frequency not always high<br>Recency varies',
        'strategy': 'Maximize transaction value per customer',
        'actions': 'Offer flexible installment or payment methods<br>Provide free express delivery without minimum<br>Create high-value product bundles<br>Provide concierge ordering service<br>Send exclusive gifts based on purchase value',
        'kpis': 'AOV increase of at least 15 percent<br>Retention above 90 percent<br>Customer satisfaction above 4.8 out of 5'
    },
    'Dormant': {
        'characteristics': 'High recency<br>Low frequency<br>High churn risk',
        'strategy': 'Reactivate inactive customers',
        'actions': 'Send aggressive 25 to 30 percent discounts<br>Use email, WhatsApp, and retargeting ads<br>Offer time-limited promotions<br>Make personal approaches for high-value customers<br>Send reminders based on last purchased products',
        'kpis': 'Win-back rate above 25 percent<br>Response rate above 15 percent<br>Campaign ROI above 200 percent'
    },
    'Potential': {
        'characteristics': 'Low recency<br>Still low frequency<br>Low to medium monetary',
        'strategy': 'Accelerate second purchase',
        'actions': 'Send product education and use cases<br>Provide special discount for second purchase<br>Activate phased welcome email flow<br>Recommend complementary products<br>Use simple cross-sell techniques',
        'kpis': 'Conversion to repeat buyer above 35 percent<br>Second purchase within 30 days<br>LTV increase of at least 25 percent'
    },
    'Standard': {
        'characteristics': 'Average RFM<br>Large volume<br>Stable per-customer value',
        'strategy': 'Maintain engagement with cost efficiency',
        'actions': 'Send regular newsletters with relevant content<br>Run seasonal promotions<br>Use AI-based product recommendations<br>Provide unexpected small rewards<br>Build community or lightweight membership program',
        'kpis': 'Engagement rate above 40 percent<br>Stable retention<br>Customer satisfaction above 3.5 out of 5'
    }
}

# Function to convert text with <br> to proper HTML
def format_content(text):
    """Convert text with <br> tags to HTML elements with class detail-item"""
    if '<br>' in text:
        items = [item.strip() for item in text.split('<br>')]
        html_items = ''.join([f'<div class="detail-item">{item}</div>' for item in items])
        return html_items
    else:
        return f'<div class="detail-item">{text}</div>'

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

# Initialize profs and colors
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

# Custom CSS for more modern Streamlit - IMPROVED
st.markdown("""
<style>
    * {margin: 0; padding: 0; box-sizing: border-box}
    body {font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; min-height: 100vh}
    .stApp {background: transparent !important; padding: 0 !important; max-width: 100% !important}
    
    /* SIDEBAR */
    .st-emotion-cache-1cypcdb {background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; border-right: 1px solid #334155}
    .st-emotion-cache-16txtl3 {padding: 2rem 1.5rem !important}
    
    /* HEADER with glassmorphism */
    .header-container {
        background: rgba(15, 23, 42, 0.95); 
        backdrop-filter: blur(20px); 
        -webkit-backdrop-filter: blur(20px); 
        padding: 2rem 2.5rem; 
        position: sticky; 
        top: 0; 
        z-index: 1000;
        margin-bottom: 2rem;
        border-radius: 0 0 20px 20px;
    }
    .main-header {display: flex; justify-content: center; align-items: center; flex-direction: column; text-align: center; gap: 0.75rem}
    .header-title {font-size: 2.75rem; font-weight: 900; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1.1;
                  letter-spacing: -0.5px;}
    .header-subtitle {color: #94a3b8; font-size: 1.15rem; margin-top: 0.5rem; font-weight: 400; max-width: 800px; line-height: 1.5;}
    
    /* SECTION DIVIDER - ADDED */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(102, 126, 234, 0.3) 20%, 
            rgba(102, 126, 234, 0.6) 50%, 
            rgba(102, 126, 234, 0.3) 80%, 
            transparent 100%
        );
        margin: 2.5rem 0;
        border: none;
        width: 100%;
    }
    
    .section-divider-thick {
        height: 3px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(102, 126, 234, 0.4) 20%, 
            rgba(102, 126, 234, 0.8) 50%, 
            rgba(102, 126, 234, 0.4) 80%, 
            transparent 100%
        );
        margin: 3rem 0;
        border: none;
        width: 100%;
        border-radius: 3px;
    }
    
    /* SECTION HEADERS - ADDED */
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .section-icon {
        font-size: 1.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem;
        border-radius: 12px;
        background: rgba(102, 126, 234, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #fff;
        margin: 0;
        letter-spacing: -0.25px;
    }
    
    .section-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 0.25rem;
        font-weight: 400;
    }
    
    /* METRICS GRID with neumorphism */
    .metrics-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin: 2rem 0}
    @media (max-width: 1200px) {.metrics-grid {grid-template-columns: repeat(2, 1fr)}}
    @media (max-width: 768px) {.metrics-grid {grid-template-columns: 1fr}}
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.8) 100%); 
        border-radius: 20px; 
        padding: 1.75rem; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; 
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    .metric-card:hover {
        transform: translateY(-6px); 
        border-color: rgba(102, 126, 234, 0.4); 
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    .metric-card::before {
        content: ''; 
        position: absolute; 
        top: 0; 
        left: 0; 
        right: 0; 
        height: 4px; 
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 20px 20px 0 0;
    }
    .metric-icon {
        font-size: 2.25rem; 
        margin-bottom: 1.25rem; 
        display: inline-block;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.75rem;
        border-radius: 14px;
    }
    .metric-value {font-size: 2.25rem; font-weight: 900; color: #fff; margin: 0.5rem 0; line-height: 1}
    .metric-label {
        font-size: 0.875rem; 
        color: #94a3b8; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .metric-change {font-size: 0.8rem; display: flex; align-items: center; gap: 0.25rem; margin-top: 0.75rem}
    .change-positive {color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 0.25rem 0.5rem; border-radius: 20px;}
    .change-negative {color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 0.25rem 0.5rem; border-radius: 20px;}
  
    
    /* FILTER ITEMS - ADDED */
    .filter-column {padding: 0.5rem}
    .filter-label {font-size: 0.875rem; color: #94a3b8; margin-bottom: 0.75rem; font-weight: 600; display: block}
    
    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {gap: 0.75rem; margin: 2.5rem 0 2rem 0}
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5) !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important; 
        padding: 1rem 2rem !important; 
        color: #94a3b8 !important; 
        font-weight: 700 !important; 
        transition: all 0.3s ease;
        font-size: 1rem !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(30, 41, 59, 0.8) !important; 
        color: #fff !important; 
        border-color: rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; 
        color: #fff !important; 
        border-color: transparent !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* STRATEGY CARDS */
    .strategy-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin-bottom: 2rem}
    @media (max-width: 1200px) {.strategy-grid {grid-template-columns: 1fr}}
    .strategy-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 20px; 
        padding: 2rem; 
        color: #fff; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        position: relative; 
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        margin-top: 1.5rem;
    }
    .strategy-card:hover {
        transform: translateY(-5px); 
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border-color: rgba(102, 126, 234, 0.3);
    }
    .strategy-header {display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.25rem}
    .strategy-name {
        font-size: 1.75rem; 
        font-weight: 900; 
        margin: 0; 
        line-height: 1.2;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .priority-badge {
        padding: 0.5rem 1rem; 
        border-radius: 20px; 
        font-size: 0.75rem; 
        font-weight: 800;
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .strategy-subtitle {font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 1.5rem; font-weight: 500}
    
    /* Detail section styling for tab 4 */
    .detail-section {
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .detail-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .detail-title {
        font-size: 1.1rem; 
        font-weight: 700; 
        color: #fff; 
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .detail-content {
        font-size: 0.95rem; 
        color: rgba(255, 255, 255, 0.9); 
        line-height: 1.6;
    }
    
    .detail-item {
        margin-bottom: 0.75rem;
        padding-left: 1rem;
        position: relative;
        line-height: 1.5;
    }
    
    .detail-item:before {
        content: "•";
        color: #667eea;
        position: absolute;
        left: 0;
        font-weight: bold;
    }
    
    .strategy-footer {
        display: flex; 
        justify-content: space-between; 
        margin-top: 2rem; 
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        gap: 1rem;
    }
    .budget-item {text-align: center; flex: 1}
    .budget-label {font-size: 0.8rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;}
    .budget-value {font-size: 1.75rem; font-weight: 900}
    
    /* CHAMPION BREAKDOWN */
    .champion-section {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.08) 0%, rgba(255, 140, 0, 0.08) 100%); 
        border: 1px solid rgba(255, 215, 0, 0.2); 
        border-radius: 20px; 
        padding: 2rem; 
        margin: 2rem 0;
        box-shadow: 0 10px 25px rgba(255, 215, 0, 0.05);
    }
    .champion-title {
        font-size: 1.75rem; 
        font-weight: 900; 
        color: #FFFFFF; 
        margin-bottom: 1.5rem; 
        display: flex; 
        align-items: center; 
        gap: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(255, 215, 0, 0.3);
    }
    .champion-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem}
    @media (max-width: 768px) {.champion-grid {grid-template-columns: 1fr}}
    .champion-card {
        background: rgba(255, 215, 0, 0.08); 
        border: 1px solid rgba(255, 215, 0, 0.2); 
        border-radius: 16px; 
        padding: 1.5rem; 
        transition: all 0.3s ease;
    }
    .champion-card:hover {
        background: rgba(255, 215, 0, 0.12); 
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(255, 215, 0, 0.1);
    }
    .champion-number {
        font-size: 1.5rem; 
        font-weight: 900; 
        color: #FFD700; 
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .champion-tier {font-size: 1.1rem; font-weight: 800; color: #fff; margin-bottom: 0.75rem}
    .champion-desc {font-size: 0.95rem; color: rgba(255, 255, 255, 0.85); margin-bottom: 1rem; line-height: 1.5;}
    .champion-chars {
        font-size: 0.8rem; 
        color: rgba(255, 215, 0, 0.9); 
        background: rgba(255, 215, 0, 0.1);
        padding: 0.75rem; 
        border-radius: 10px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    /* INSIGHTS SECTION - IMPROVED */
    .insights-section {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.08) 0%, rgba(0, 242, 254, 0.08) 100%);
        border: 1px solid rgba(79, 172, 254, 0.2); 
        border-radius: 20px; 
        padding: 2rem; 
        margin: 2rem 0;
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.05);
    }
    .insights-title {
        font-size: 1.75rem; 
        font-weight: 900; 
        color: #4facfe; 
        margin-bottom: 1.5rem;
        display: flex; 
        align-items: center; 
        gap: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(79, 172, 254, 0.3);
    }
    
    /* IMPROVEMENT: Equal height cards container */
    .insights-grid-container {
        display: flex;
        gap: 2rem;
        align-items: stretch;
        margin-bottom: 2rem;
    }
    
    @media (max-width: 768px) {
        .insights-grid-container {
            flex-direction: column;
        }
    }
    
    /* IMPROVEMENT: Insight card with 100% height */
    .insight-card {
        background: rgba(79, 172, 254, 0.08); 
        border: 1px solid rgba(79, 172, 254, 0.2); 
        border-radius: 16px; 
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .insight-card-header {
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(79, 172, 254, 0.3);
    }
    
    .insight-card-title {
        font-size: 1.25rem; 
        font-weight: 800; 
        color: #4facfe; 
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .insight-card-subtitle {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    .insight-list {list-style: none; padding: 0; margin: 0; flex-grow: 1}
    .insight-list li {
        padding: 0.75rem 0; 
        border-bottom: 1px solid rgba(79, 172, 254, 0.2); 
        color: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .insight-list li:last-child {border-bottom: none}
    
    /* ADVANCED ANALYTICS SECTION */
    .advanced-analytics-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(79, 172, 254, 0.2);
    }
    
    .advanced-analytics-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .advanced-analytics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
    }
    
    @media (max-width: 1200px) {
        .advanced-analytics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .advanced-analytics-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* FOOTER */
    .footer {
        text-align: center; 
        padding: 2rem; 
        margin-top: 3rem; 
        color: #94a3b8; 
        font-size: 0.9rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(15, 23, 42, 0.8);
        border-radius: 20px 20px 0 0;
    }
    
    /* UTILITY CLASSES */
    .empty-state {text-align: center; padding: 4rem; color: #94a3b8}
    .empty-icon {font-size: 3.5rem; margin-bottom: 1.5rem; opacity: 0.5}
    
    /* STREAMLIT WIDGET OVERRIDES - IMPROVED */
    div[data-testid="stSelectbox"] > div {
        background: rgba(30, 41, 59, 0.8); 
        border-color: rgba(255, 255, 255, 0.1) !important; 
        border-radius: 12px !important; 
        overflow: hidden;
        border-width: 1px !important;
    }
    div[data-testid="stSelectbox"] svg {color: #94a3b8 !important}
    div[data-testid="stSlider"] > div {
        background: rgba(30, 41, 59, 0.8); 
        border-radius: 12px; 
        padding: 0.5rem 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stSlider"] .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px;
    }
    div[data-testid="stSlider"] .stSlider > div > div > div:first-child {
        background: rgba(102, 126, 234, 0.2) !important;
        border-radius: 10px;
    }
    
    /* CUSTOM LABELS for filter */
    .custom-label {
        display: flex; 
        align-items: center; 
        gap: 0.75rem; 
        margin-bottom: 0.75rem; 
        color: #94a3b8; 
        font-size: 0.9rem; 
        font-weight: 700;
    }
    
    /* SPACING UTILITIES */
    .spacer-sm {margin: 1rem 0}
    .spacer-md {margin: 2rem 0}
    .spacer-lg {margin: 3rem 0}
    
    /* NEW: Improved layout for strategy cards in overview */
    .strategy-overview-grid {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        margin-top: 1.5rem;
    }
    
    /* SUMMARY HEADER STYLES */
    .summary-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    
    .summary-title {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 1.1rem;
    }
    
    .summary-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* SELECT BOX STYLING for Tab 4 */
    .segment-select-container {
        margin: 2rem 0;
        padding: 1.5rem;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .segment-select-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to create more modern charts
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
        title=dict(
            text="🎯 Customer Distribution",
            font=dict(color='white', size=30),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=100, l=50, r=50),
        legend=dict(
            font=dict(color='white'),
            orientation='h',
            yanchor='bottom',
            y=-1,
            xanchor='center',
            x=0.5
        )
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
            title=dict(
                text="💰 Revenue by Segment",
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(text="Revenue (£)", font=dict(color='white')),
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                tickfont=dict(color='white')
            ),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(
            title=dict(
                text="💰 Revenue by Segment", 
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text='No revenue data',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color='white', size=14)
            )]
        )
    
    # Chart 3: 3D RFM Analysis with dark theme
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
            title=dict(
                text="📈 3D RFM Analysis",
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=600,
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
            plot_bgcolor='rgba(0,0,0,0)'
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(
            title=dict(
                text="📈 3D RFM Analysis", 
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    # Chart 4-6: Histograms with dark theme
    def create_histogram(df, column, title, color):
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                title=dict(
                    text=title, 
                    font=dict(color='white', size=18),
                    x=0.5,
                    xanchor='center'
                ),
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
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
            title=dict(
                text=title, 
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=300,
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
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    fig4 = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#FF6B6B')
    fig5 = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ECDC4')
    fig6 = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45B7D1')
    
    # Chart 7: RFM Table - fixed version
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
            title=dict(
                text="📊 Segment Summary",
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=400,
            margin=dict(t=100, b=20, l=20, r=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
    except Exception as e:
        fig7 = go.Figure()
        fig7.update_layout(
            title=dict(
                text="📊 Segment Summary", 
                font=dict(color='white', size=30),
                x=0.5,
                xanchor='center'
            ),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
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

# Main Streamlit layout
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="main-header">
            <h1 class="header-title">Customer Intelligence Hub</h1>
            <div class="header-subtitle">AI-Powered Customer Segmentation for Targeted Marketing</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 1: Key Metrics with section header
    st.markdown("""
    <div class="section-header">
        <div>
            <div class="section-title">Key Performance Metrics</div>
            <div class="section-subtitle">Real-time insights into customer behavior and business performance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Section 2: Data Filters with section header
    st.markdown("""
    <div class="section-header">
        <div>
            <div class="section-title">Smart Filters</div>
            <div class="section-subtitle">Refine and segment your customer data with precision controls</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        # Filter grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="filter-content">', unsafe_allow_html=True)
            st.markdown('<div class="custom-label">🎨 Segment Filter</div>', unsafe_allow_html=True)
            
            # Segment Filter
            segment_options = [{'label': '🌐 All Segments', 'value': 'all'}]
            for c, p in profs.items():
                if p['name'] == '🏆 Champions' and c in champion_details:
                    label = f"{p['name']} - {champion_details[c]['tier']}"
                else:
                    label = p['name']
                segment_options.append({'label': label, 'value': c})
            
            segment_filter = st.selectbox(
                "",
                options=[opt['value'] for opt in segment_options],
                format_func=lambda x: next((opt['label'] for opt in segment_options if opt['value'] == x), x),
                index=0,
                key="segment_filter",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="filter-content">', unsafe_allow_html=True)
            st.markdown('<div class="custom-label">📊 RFM Score Range</div>', unsafe_allow_html=True)
            
            # RFM Score Range
            if 'RFM_Score' in rfm.columns:
                rfm_min = int(rfm['RFM_Score'].min())
                rfm_max = int(rfm['RFM_Score'].max())
                rfm_filter = st.slider(
                    "",
                    min_value=rfm_min,
                    max_value=rfm_max,
                    value=[rfm_min, rfm_max],
                    key="rfm_filter",
                    label_visibility="collapsed"
                )
            else:
                rfm_filter = [0, 100]
                st.slider(
                    "",
                    min_value=0,
                    max_value=100,
                    value=[0, 100],
                    key="rfm_filter",
                    label_visibility="collapsed"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="filter-content">', unsafe_allow_html=True)
            st.markdown('<div class="custom-label">🔥 Priority Level</div>', unsafe_allow_html=True)
            
            # Priority Level
            priority_options = [
                {'label': '🌐 All Priorities', 'value': 'all'},
                {'label': '🔴 CRITICAL', 'value': 'CRITICAL'},
                {'label': '🔥 URGENT', 'value': 'URGENT'},
                {'label': '⚡ HIGH', 'value': 'HIGH'},
                {'label': '📊 MEDIUM', 'value': 'MEDIUM'}
            ]
            priority_filter = st.selectbox(
                "",
                options=[opt['value'] for opt in priority_options],
                format_func=lambda x: next((opt['label'] for opt in priority_options if opt['value'] == x), x),
                index=0,
                key="priority_filter",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced Filters
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
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
    
    # Tabs Section with section header
    st.markdown("""
    <div class="section-header">
        <div>
            <div class="section-title">Dashboard Analytics</div>
            <div class="section-subtitle">Explore different aspects of your customer data through interactive tabs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs - WITHOUT TAB4 (only 3 tabs now)
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts
            fig1, fig2, fig3, fig4, fig5, fig6, fig7 = create_charts(filtered_df)
            
            # Row 1: Two charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': True})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': True})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 2: Full width 3D chart
            st.markdown('<div class="chart-container chart-full">', unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': True})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 3: Three histograms
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 4: Full width table
            st.markdown('<div class="chart-container chart-full">', unsafe_allow_html=True)
            st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Data summary
            with st.expander("📋 Data Summary"):
                st.dataframe(
                    filtered_df.describe(),
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Data Available</h3>
                <p>Try adjusting your filters to see data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Part 1: Champion Breakdown (same as before)
        champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                        if c in profs and profs[c]['name'] == '🏆 Champions']

        if len(champion_clusters) > 0:
            st.markdown('<div class="champion-title">Champion Segments Breakdown</div>', unsafe_allow_html=True)
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
        
        # NEW SECTION: Selling Strategy (moved from tab4)
        st.markdown("""
        <div class="section-header">
            <div>
                <div class="section-title">Selling Strategy</div>
                <div class="section-subtitle">Interactive selling strategies based on customer segments</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


        # Dropdown section to select segment
        
        segment_names = list(cluster_full_details.keys())
        selected_segment = st.selectbox(
            "🎯 Select Customer Segment",
            segment_names,
            index=0,
            key="selling_strategy_segment"
        )
        
        
        # Two columns for strategy details (same layout as tab3)
        details = cluster_full_details[selected_segment]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-card-header">
                    <div class="insight-card-title">📊 Characteristics</div>
                    <div class="insight-card-subtitle">Customer profile and behavior</div>
                </div>
                <div class="detail-content">
                    {format_content(details['characteristics'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-card" style="margin-top: 1.5rem;">
                <div class="insight-card-header">
                    <div class="insight-card-title">🎯 Main Strategy</div>
                    <div class="insight-card-subtitle">Strategic approach for this segment</div>
                </div>
                <div class="detail-content">
                    {format_content(details['strategy'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-card-header">
                    <div class="insight-card-title">⚙️ Sales Actions</div>
                    <div class="insight-card-subtitle">Specific implementation tactics</div>
                </div>
                <div class="detail-content">
                    {format_content(details['actions'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-card" style="margin-top: 1.5rem;">
                <div class="insight-card-header">
                    <div class="insight-card-title">📈 KPI Targets</div>
                    <div class="insight-card-subtitle">Expected performance indicators</div>
                </div>
                <div class="detail-content">
                    {format_content(details['kpis'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        

    with tab3:
        if len(filtered_df) > 0:
            # Calculate insights with consistent data format
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
            
            # Build insights section HTML
            insights_list = [
                f"🏆 Highest Revenue: {highest_revenue_segment} (£{highest_revenue_value/1000:.1f}K)",
                f"👥 Largest Segment: {largest_group_segment} ({largest_group_count:,} customers)",
                f"💰 Best AOV: {best_aov_segment} (£{best_aov_value:.0f})",
                f"🔄 Most Frequent: {most_frequent_segment} ({most_frequent_value:.1f} orders)",
                f"📈 Champion Ratio: {(len(filtered_df[filtered_df['Cluster_Label'].str.contains('Champions')]) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0):.1f}%",
                f"⏰ Avg Recency: {filtered_df['Recency'].mean():.1f} days" if 'Recency' in filtered_df.columns else "⏰ Avg Recency: N/A"
            ]
            
            # Build list items HTML
            insight_items_html = ""
            for insight in insights_list:
                insight_items_html += f"<li>{insight}</li>"
            
            # Calculate advanced metrics
            concentration_pct = (largest_group_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            
            if 'Monetary' in filtered_df.columns:
                top_20_percent = filtered_df.nlargest(max(1, int(len(filtered_df) * 0.2)), 'Monetary')
                total_revenue = filtered_df['Monetary'].sum()
                revenue_concentration = (top_20_percent['Monetary'].sum() / total_revenue * 100) if total_revenue > 0 else 0
            else:
                revenue_concentration = 0
            
            avg_recency = filtered_df['Recency'].mean() if 'Recency' in filtered_df.columns else 0
            avg_frequency = filtered_df['Frequency'].mean() if 'Frequency' in filtered_df.columns else 0
            
            # Build complete insights HTML
            insights_html = f"""
            <div class="insights-section">
                <div class="insights-title">🧠 AI-Powered Insights & Recommendations</div>
                <div class="insights-grid-container">
                    <div class="insight-card">
                        <div class="insight-card-header">
                            <div class="insight-card-title">📊 Key Performance Summary</div>
                            <div class="insight-card-subtitle">Data-driven insights from customer segments</div>
                        </div>
                        <ul class="insight-list">
                            {insight_items_html}
                        </ul>
                    </div>
                    <div class="insight-card">
                        <div class="insight-card-header">
                            <div class="insight-card-title">💡 Strategic Recommendations</div>
                            <div class="insight-card-subtitle">Actionable strategies for each segment</div>
                        </div>
                        <ul class="insight-list">
                            <li>🎯 <strong>Retention Programs</strong> for high-value segments</li>
                            <li>📧 <strong>Personalized Win-Back</strong> campaigns for dormant customers</li>
                            <li>🚀 <strong>Accelerated Nurturing</strong> flows for potential customers</li>
                            <li>💎 <strong>VIP Experiences</strong> for champion segments</li>
                            <li>📈 <strong>Cross-Sell Strategies</strong> for loyal customers</li>
                            <li>🔍 <strong>Dormant Reactivation</strong> monitoring programs</li>
                        </ul>
                    </div>
                </div>
                <div class="advanced-analytics-section">
                    <div class="advanced-analytics-title">📈 Advanced Analytics</div>
                    <div class="advanced-analytics-grid">
                        <div class="metric-card">
                            <div class="metric-icon">📊</div>
                            <div class="metric-value">{concentration_pct:.1f}%</div>
                            <div class="metric-label">Segment Concentration</div>
                            <div class="metric-change change-positive">
                                <span>↑ 2.3%</span>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon">💰</div>
                            <div class="metric-value">{revenue_concentration:.1f}%</div>
                            <div class="metric-label">Revenue Concentration (Top 20%)</div>
                            <div class="metric-change change-positive">
                                <span>↑ 1.5%</span>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon">⏰</div>
                            <div class="metric-value">{avg_recency:.1f}</div>
                            <div class="metric-label">Avg Recency (days)</div>
                            <div class="metric-change change-negative">
                                <span>↓ 3.2</span>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon">🔄</div>
                            <div class="metric-value">{avg_frequency:.1f}</div>
                            <div class="metric-label">Avg Frequency</div>
                            <div class="metric-change change-positive">
                                <span>↑ 0.8</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            # Display all HTML at once
            st.markdown(insights_html, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">💡</div>
                <h3>No Insights Available</h3>
                <p>Try adjusting your filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()
