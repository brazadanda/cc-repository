import streamlit as st
from datetime import date, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Optimizer Pro", page_icon="⚖️")

def apply_app_styles(card_name):
    # Dynamic logic for the main Result card ONLY
    card_colors = {"Customized": "#D32F2F", "Premium": "#4A148C", "Amazon": "#283593", "Costco": "#1B5E20"}
    res_bg = "#333333" 
    for key, color_code in card_colors.items():
        if key in card_name:
            res_bg = color_code
            break
            
    st.markdown(f"""
        <style>
        /* Main Result Card: High Contrast & Dynamic */
        .stAlert {{ 
            background: linear-gradient(135deg, {res_bg} 0%, #1A1A1A 160%) !important; 
            border-radius: 15px !important; 
            padding: 20px !important; 
            border: none !important; 
        }}
        .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3 {{ 
            color: #FFFFFF !important; 
            font-weight: 800 !important; 
            text-transform: uppercase !important; 
            text-align: center !important; 
        }}
        
        /* Neutral Status Plate: Uses Theme Variables for Auto Light/Dark Adaptivity */
        .status-plate {{ 
            background-color: rgba(128, 128, 128, 0.1); 
            border: 1px solid rgba(128, 128, 128, 0.2); 
            border-radius: 8px; 
            padding: 12px; 
            margin-top: 10px;
        }}
        .status-header {{ 
            font-size: 0.7rem; 
            font-weight: 700; 
            text-transform: uppercase; 
            opacity: 0.6;
            margin-bottom: 6px;
            letter-spacing: 0.05em;
        }}
        .status-val {{ 
            font-size: 0.85rem; 
            font-family: 'Source Code Pro', monospace; 
            line-height: 1.6;
        }}
        
        /* Standardized Buttons */
        .stButton>button {{ width: 100%; border-radius: 8px; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR SETTINGS ---
st.sidebar.title("Settings")

# DEFAULT: Simple Mode (False)
app_mode = st.sidebar.toggle("Detailed Strategy Mode", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Preferred Rewards")

# DEFAULT: Platinum Honors (Index 3)
tier = st.sidebar.selectbox(
    "Active Tier", 
    ["None", "Gold", "Platinum", "Plat Honors"], 
    index=3
)

# Multiplier Logic
multipliers = {"None": 1.0, "Gold": 1.25, "Platinum": 1.50, "Plat Honors": 1.75}
m = multipliers[tier]

# Rates based on tier
r_online = 0.03 * m
r_base = 0.015 * m
r_travel = 0.02 * m

# NEUTRAL SIDEBAR BOX (Adaptive to light/dark mode)
st.sidebar.markdown(f"""
    <div class="status-plate">
        <div class="status-header">{tier} Yields</div>
        <div class="status-val">
            • Online: {r_online*100:.2f}%<br>
            • Travel: {r_travel*100:.1f}%<br>
            • Other: {r_base*100:.3f}%
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(v):
    if v == 0: st.session_state.purchase_amt = 0.0
    else: st.session_state.purchase_amt += float(v)

# Quarterly pacing logic
today = date.today()
q_start = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
q_end = (date(today.year, q_start.month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_rem = (q_end - today).days + 1
pace = (( (q_end - q_start).days + 1 - days_rem) / ((q_end - q_start).days + 1)) * 2500

# --- 4. MAIN INTERFACE ---
if app_mode:
    st.subheader("Quarterly Tracking")
    spent = st.slider("CCR Category Spend ($)", 0, 2500, value=int(st.session_state.get('s_ccr', pace)), step=50)
    st.session_state['s_ccr'] = spent
    rem = 2500.0 - spent
    
    st.subheader("New Purchase")
    c1, c2, c3 = st.columns(3)
    c1.button("+$50", on_click=update_amt, args=(50,))
    c2.button("+$100", on_click=update_amt, args=(100,))
    c3.button("RESET", on_click=update_amt, args=(0,))
    
    amt = st.number_input("Amount ($)", value=float(st.session_state.purchase_amt))
else:
    amt, rem = 0.0, 2500.0

st.title("Card Optimizer")
cat = st.selectbox("Category", ["Online Shopping", "Amazon.com", "Gas Station", "Dining / Travel / Other"])

# --- 5. DECISION ENGINE ---
def decide():
    if "Online" in cat:
        if amt > rem or (app_mode and rem < 500): 
            return "BofA Premium Rewards Elite", f"{r_base*100:.3f}%", "Cap preservation."
        return "BofA Customized Cash", f"{r_online*100:.2f}%", "Max category yield."
    
    if "Amazon" in cat: return "Amazon Prime Visa", "5.0%", "Merchant specific."
    if "Gas" in cat: return "Costco Anywhere Visa", "4.0%", "Uncapped gas."
    if "Dining" in cat: return "BofA Premium Rewards Elite", f"{r_travel*100:.1f}%", f"{tier} Travel rate."
    return "BofA Premium Rewards Elite", f"{r_base*100:.3f}%", "Best catch-all."

card, rate, reason = decide()
apply_app_styles(card)
st.error(f"{card}")

if app_mode:
    st.markdown(f'<div class="insight-box"><div class="insight-text"><b>Tier:</b> {tier}<br><b>Yield:</b> {rate}<br><b>Reason:</b> {reason}</div></div>', unsafe_allow_html=True)
