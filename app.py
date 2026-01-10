import streamlit as st
from datetime import date

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Selector", page_icon="💳")

def apply_card_style(card_name):
    # Fixed the NameError by ensuring the dictionary is defined inside the function
    card_colors = {
        "Customized": "#D32F2F", 
        "Premium": "#4A148C", 
        "Amazon": "#283593", 
        "Costco": "#1B5E20"
    }
    # Default to dark grey if no match found
    bg_color = "#333333"
    for key, hex_val in card_colors.items():
        if key in card_name:
            bg_color = hex_val
            break

    st.markdown(f"""
        <style>
        .stAlert {{ 
            background: linear-gradient(135deg, {bg_color} 0%, #1A1A1A 160%) !important; 
            border-radius: 15px !important; 
            padding: 20px !important; 
        }}
        .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert div {{ 
            color: #FFFFFF !important; 
            font-weight: 800 !important; 
            text-transform: uppercase !important; 
            text-align: center !important; 
        }}
        .insight-box {{ 
            background-color: #f9f9f9; 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 5px solid #ccc; 
            margin-top: 15px; 
            border: 1px solid #eee; 
        }}
        .insight-title {{ 
            font-weight: bold; 
            color: #333; 
            font-size: 0.9rem; 
            margin-bottom: 5px; 
            text-transform: uppercase; 
        }}
        .insight-text {{ color: #555; font-size: 0.85rem; line-height: 1.4; }}
        .stButton>button {{ width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }}
        .pace-marker {{ color: #666; font-size: 0.8rem; margin-top: -15px; margin-bottom: 10px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTS ---
BOFA_ELITE_BASE = 0.02625
BOFA_CCR_RATE = 0.0525
AMZ_RATE = 0.05
COSTCO_GAS = 0.04
LARGE_PURCHASE_LIMIT = 150.0  
PACE_CUSHION_REQUIRED = -250.0 

# --- 3. INPUTS ---
st.sidebar.title("App Settings")
app_mode = st.sidebar.toggle("Detailed Mode", value=False)

if 'purchase_amt' not in st.session_state: 
    st.session_state.purchase_amt = 0.0

if app_mode:
    # Accurate Pacing Logic
    today = date.today()
    q_start_month = ((today.month - 1) // 3) * 3 + 1
    q_start_date = date(today.year, q_start_month, 1)
    days_elapsed = (today - q_start_date).days
    ideal_pace = (days_elapsed / 91) * 2500

    st.subheader("1. Quarterly CCR Cap Spend")
    ccr_spent = st.slider("Total 5.25% Category Spend ($)", 0, 2500, value=int(st.session_state.get('saved_ccr', ideal_pace)), step=25)
    st.markdown(f'<div class="pace-marker">Target spend for {today.strftime("%b %d")}: <b>${ideal_pace:.0f}</b></div>', unsafe_allow_html=True)
    
    st.session_state['saved_ccr'] = ccr_spent
    cap_rem = max(0.0, 2500.0 - ccr_spent)
    pace_delta = ccr_spent - ideal_pace

    st.subheader("2. Purchase Amount")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("+$10"): st.session_state.purchase_amt += 10
    with c2: 
        if st.button("+$50"): st.session_state.purchase_amt += 50
    with c3:
        if st.button("+$100"): st.session_state.purchase_amt += 100
    m1, m2, m3 = st.columns(3)
    with m1:
        if st.button("-$10"): st.session_state.purchase_amt = max(0.0, st.session_state.purchase_amt - 10)
    with m2:
        if st.button("-$50"): st.session_state.purchase_amt = max(0.0, st.session_state.purchase_amt - 50)
    with m3:
        if st.button("RESET"): st.session_state.purchase_amt = 0.0
        
    amt = st.number_input("Purchase Amount ($)", value=float(st.session_state.purchase_amt), step=1.0)
else:
    amt, cap_rem, pace_delta = 20.0, 2500.0, 0.0

# --- 4. MAIN UI ---
st.title("Card Optimizer")
purchase_type = st.selectbox("Select Purchase Category", [
    "Online Shopping (General)", 
    "Amazon.com / Whole Foods", 
    "Gas Station / Fuel", 
    "In-Store / Dining / Other"
])
st.markdown("---")

def get_decision():
    if "Online" in purchase_type:
        earnings = (min(amt, cap_rem) * BOFA_CCR_RATE)
        if not app_mode: return "BofA Customized Cash Rewards Visa", earnings
        if cap_rem <= 0: return "BofA Premium Rewards Elite Visa", amt * BOFA_ELITE_BASE
        if amt >= LARGE_PURCHASE_LIMIT and pace_delta > PACE_CUSHION_REQUIRED:
            return "BofA Premium Rewards Elite Visa", amt * BOFA_ELITE_BASE
        return "BofA Customized Cash Rewards Visa", earnings
    
    if "Amazon" in purchase_type: return "Amazon Prime Visa", amt * AMZ_RATE
    if "Gas" in purchase_type: return "Costco Anywhere Visa", amt * COSTCO_GAS
    return "BofA Premium Rewards Elite Visa", amt * BOFA_ELITE_BASE

card, total_earnings = get_decision()
apply_card_style(card)
st.error(f"{card}")

# --- 5. STRATEGY INSIGHT (DETAILED ONLY) ---
if app_mode:
    if pace_delta > 100:
        pace_status = "You're spending above pace. Be selective with the 5.25% rate."
    elif pace_delta < -250:
        pace_status = "You're well under pace. Use the 5.25% rate freely."
    else:
        pace_status = "Your spending is on track with the quarterly pace."
    
    cap_impact = (amt / 2500) * 100 if "Online" in purchase_type else 0
    
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">Strategy Insight</div>
        <div class="insight-text">
            • Earning <b>${total_earnings:.2f}</b> in cash back.<br>
            • {pace_status}<br>
            {"• This purchase consumes <b>" + f"{cap_impact:.1f}%" + "</b> of your quarterly limit." if cap_impact > 0 else "• This transaction does not impact your BofA $2,500 limit."}
        </div>
    </div>
    """, unsafe_allow_html=True)