import streamlit as st
from datetime import date, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Optimizer Pro", page_icon="⚖️")

def apply_app_styles(card_name):
    card_colors = {"Customized": "#D32F2F", "Premium": "#4A148C", "Amazon": "#283593", "Costco": "#1B5E20"}
    res_bg = "#333333" 
    for key, color_code in card_colors.items():
        if key in card_name:
            res_bg = color_code
            break
            
    st.markdown(f"""
        <style>
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
        .disclaimer {{
            font-size: 0.65rem;
            opacity: 0.7;
            line-height: 1.2;
            margin-top: 10px;
        }}
        .stButton>button {{ width: 100%; border-radius: 8px; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# Formatting Helper: Removes ".00" or extra zeros
def fmt_pct(val):
    return f"{val*100:g}%"

# --- 2. SIDEBAR SETTINGS ---
st.sidebar.title("Settings")
app_mode = st.sidebar.toggle("Detailed Strategy Mode", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Preferred Rewards")

tier_options = ["None", "Gold", "Platinum", "Platinum Honors"]
tier = st.sidebar.selectbox("Active Tier", tier_options, index=3)

multipliers = {"None": 1.0, "Gold": 1.25, "Platinum": 1.50, "Platinum Honors": 1.75}
m = multipliers[tier]

# Rates based on tier
r_online = 0.03 * m
r_base = 0.015 * m
r_travel_dining = 0.02 * m
r_fallback = 0.01 * m 

# SIDEBAR YIELD PLATE
st.sidebar.markdown(f"""
    <div class="status-plate">
        <div class="status-header">{tier} Yields</div>
        <div class="status-val">
            • Online Shopping: {fmt_pct(r_online)}<br>
            • Travel/Dining: {fmt_pct(r_travel_dining)}<br>
            • Other: {fmt_pct(r_base)}
        </div>
        <div class="disclaimer">
            *Online Shopping rate applies to the first $2,500 of combined choice category/grocery 
            purchases each quarter. After the cap, yield reverts to {fmt_pct(r_fallback)}. 
            Travel/Dining rates are uncapped on Premium Rewards cards.
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(v):
    if v == 0: st.session_state.purchase_amt = 0.0
    else: st.session_state.purchase_amt += float(v)

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
            return "BofA Premium Rewards Elite", fmt_pct(r_base), "Cap preservation."
        return "BofA Customized Cash", fmt_pct(r_online), "Max category yield."
    
    if "Amazon" in cat: return "Amazon Prime Visa", "5%", "Merchant specific."
    if "Gas" in cat: return "Costco Anywhere Visa", "4%", "Uncapped gas."
    if "Dining" in cat: return "BofA Premium Rewards Elite", fmt_pct(r_travel_dining), f"{tier} Travel rate."
    return "BofA Premium Rewards Elite", fmt_pct(r_base), "Best catch-all."

card, rate, reason = decide()
apply_app_styles(card)
st.error(f"{card}")

if app_mode:
    st.markdown(f'<div class="insight-box"><div class="insight-text"><b>Tier:</b> {tier}<br><b>Yield:</b> {rate}<br><b>Reason:</b> {reason}</div></div>', unsafe_allow_html=True)
