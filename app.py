import streamlit as st
from datetime import date, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Optimizer Pro", page_icon="⚖️")

def apply_card_style(card_name):
    card_colors = {"Customized": "#D32F2F", "Premium": "#4A148C", "Amazon": "#283593", "Costco": "#1B5E20"}
    bg_color = next((v for k, v in card_colors.items() if k in card_name), "#333333")
    st.markdown(f"""
        <style>
        .stAlert {{ background: linear-gradient(135deg, {bg_color} 0%, #1A1A1A 160%) !important; border-radius: 15px !important; padding: 20px !important; border: none !important; }}
        .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert div {{ color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; text-align: center !important; }}
        .insight-box {{ background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-top: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .insight-title {{ font-weight: bold; color: #1a1a1a; font-size: 0.8rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        .insight-text {{ color: #444; font-size: 0.85rem; line-height: 1.5; }}
        .stButton>button {{ width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; background-color: #f0f2f6; border: 1px solid #dcdfe6; }}
        .pace-marker {{ color: #888; font-size: 0.75rem; margin-top: -10px; margin-bottom: 15px; font-family: monospace; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED TIME & PACE LOGIC ---
today = date.today()
q_start_month = ((today.month - 1) // 3) * 3 + 1
q_start_date = date(today.year, q_start_month, 1)
q_end_date = (date(today.year, q_start_month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_total = (q_end_date - q_start_date).days + 1
days_left = (q_end_date - today).days + 1
days_elapsed = days_total - days_left

# Ideal linear pace
ideal_pace_val = (days_elapsed / days_total) * 2500

# --- 3. UI INPUTS ---
st.sidebar.title("Settings")
app_mode = st.sidebar.toggle("Detailed Strategy Mode", value=True)

if 'purchase_amt' not in st.session_state: st.session_state.purchase_amt = 0.0

if app_mode:
    st.subheader("1. CCR Cap Progress")
    ccr_spent = st.slider("Quarter-to-Date 5.25% Spend ($)", 0, 2500, value=int(st.session_state.get('saved_ccr', ideal_pace_val)), step=50)
    st.markdown(f'<div class="pace-marker">On-track Target: ${ideal_pace_val:.0f} | Days Remaining: {days_left}</div>', unsafe_allow_html=True)
    st.session_state['saved_ccr'] = ccr_spent
    
    cap_rem = 2500.0 - ccr_spent
    # Calculate Daily Allowance BEFORE this purchase
    daily_allowance_pre = cap_rem / days_left
    
    st.subheader("2. New Purchase Amount")
    c1, c2, c3 = st.columns(3); m1, m2, m3 = st.columns(3)
    with c1: 
        if st.button("+$10"): st.session_state.purchase_amt += 10
    with c2: 
        if st.button("+$50"): st.session_state.purchase_amt += 50
    with c3: 
        if st.button("+$100"): st.session_state.purchase_amt += 100
    with m1: 
        if st.button("-$10"): st.session_state.purchase_amt = max(0, st.session_state.purchase_amt - 10)
    with m2: 
        if st.button("-$50"): st.session_state.purchase_amt = max(0, st.session_state.purchase_amt - 50)
    with m3: 
        if st.button("RESET"): st.session_state.purchase_amt = 0
    
    amt = st.number_input("Amount ($)", value=float(st.session_state.purchase_amt), step=1.0)
    # Calculate Daily Allowance AFTER this purchase
    daily_allowance_post = max(0, cap_rem - amt) / days_left
else:
    amt, cap_rem, daily_allowance_pre, daily_allowance_post = 0.0, 2500.0, 27.0, 27.0

# --- 4. CATEGORY SELECT ---
st.title("Card Optimizer")
category = st.selectbox("Purchase Category", [
    "Online Shopping (General)", 
    "Amazon.com / Whole Foods", 
    "Gas Station / Fuel", 
    "In-Store / Dining / Everything Else"
])
st.markdown("---")

# --- 5. ROBUST DECISION ENGINE ---
def get_robust_decision():
    if "Online" in category:
        # STRATEGIC LOGIC:
        # 1. If cap is gone, use Elite.
        if cap_rem <= 0: return "BofA Premium Rewards Elite", "2.625%", "Cap exhausted."
        
        # 2. If purchase is huge (> $500), always flag for Elite to protect daily spend.
        if amt > 500: return "BofA Premium Rewards Elite", "2.625%", "Protecting cap for smaller daily needs."
        
        # 3. Dynamic Pace Check: If this purchase drops daily allowance below $15/day, use Elite.
        # This ensures we have at least some "high yield" room for the rest of the quarter.
        if daily_allowance_post < 15.0 and daily_allowance_pre > 15.0:
             return "BofA Premium Rewards Elite", "2.625%", "Spend pace too high; rationing cap."
             
        return "BofA Customized Cash Rewards", "5.25%", "Optimal use of quarterly cap."

    if "Amazon" in category: return "Amazon Prime Visa", "5.0%", "Best fixed rate."
    if "Gas" in category: return "Costco Anywhere Visa", "4.0%", "Dedicated gas rate."
    return "BofA Premium Rewards Elite", "2.625%+", "Best catch-all rate."

card, rate, reason = get_robust_decision()
apply_card_style(card)
st.error(f"{card}")

# --- 6. STRATEGY INSIGHT ---
if app_mode:
    # Calculate "Sacrifice" - how many days of high-yield spending this purchase 'eats'
    days_consumed = amt / max(daily_allowance_pre, 1)
    
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">Strategic Analysis</div>
        <div class="insight-text">
            • <b>Yield:</b> This card earns <b>{rate}</b> cash back.<br>
            • <b>Rationing:</b> You currently have <b>${daily_allowance_pre:.2f}/day</b> of "Online" cap remaining.<br>
            • <b>Impact:</b> This purchase "consumes" <b>{days_consumed:.1f} days</b> of your remaining quarterly high-yield budget.<br>
            • <b>Verdict:</b> {reason}
        </div>
    </div>
    """, unsafe_allow_html=True)
