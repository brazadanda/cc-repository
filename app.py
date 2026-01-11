import streamlit as st
from datetime import date, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Optimizer Pro", page_icon="⚖️")

def apply_card_style(card_name):
    card_colors = {"Customized": "#D32F2F", "Premium": "#4A148C", "Amazon": "#283593", "Costco": "#1B5E20"}
    bg_color = "#333333" 
    for key, color_code in card_colors.items():
        if key in card_name:
            bg_color = color_code
            break
    st.markdown(f"""
        <style>
        /* FORCE 3-COL GRID WITHOUT OVERFLOW */
        [data-testid="column"] {{
            flex: 1 1 0% !important;
            width: 100% !important;
            min-width: 0px !important;
        }}
        [data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.5rem !important;
        }}

        /* BUTTON STYLING */
        .stButton>button {{ 
            width: 100% !important; 
            border-radius: 8px !important; 
            height: 3.2em !important; 
            font-weight: bold !important; 
            background-color: #262730 !important; 
            color: #ffffff !important;           
            border: 1px solid #464855 !important;
            font-size: 0.85rem !important;
            padding: 0px !important;
            margin: 0px !important;
        }}

        .stAlert {{ background: linear-gradient(135deg, {bg_color} 0%, #1A1A1A 160%) !important; border-radius: 15px !important; padding: 20px !important; border: none !important; }}
        .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert div {{ color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; text-align: center !important; }}
        
        .insight-box {{ background-color: #ffffff; padding: 12px; border-radius: 12px; border: 1px solid #e0e0e0; margin-top: 10px; }}
        .insight-title {{ font-weight: bold; color: #1a1a1a; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid #eee; }}
        .insight-text {{ color: #444; font-size: 0.8rem; line-height: 1.4; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. CALLBACKS ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(value):
    if value == 0:
        st.session_state.purchase_amt = 0.0
    else:
        st.session_state.purchase_amt += float(value)

# --- 3. LOGIC ---
today = date.today()
q_start_month = ((today.month - 1) // 3) * 3 + 1
q_start_date = date(today.year, q_start_month, 1)
q_end_date = (date(today.year, q_start_month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_total = (q_end_date - q_start_date).days + 1
days_left = (q_end_date - today).days + 1
ideal_pace_val = ((days_total - days_left) / days_total) * 2500

# --- 4. UI ---
st.sidebar.title("Settings")
app_mode = st.sidebar.toggle("Detailed Strategy Mode", value=True)

if app_mode:
    st.subheader("1. Quarterly CCR Cap Spend")
    ccr_spent = st.slider("Total 5.25% Spend ($)", 0, 2500, value=int(st.session_state.get('saved_ccr', ideal_pace_val)), step=50)
    st.session_state['saved_ccr'] = ccr_spent
    cap_rem = 2500.0 - ccr_spent
    daily_allowance_pre = cap_rem / max(days_left, 1)

    st.subheader("2. Purchase Amount")
    # THE GRID: Forced 3-across, no overflow
    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.button("+$10", on_click=update_amt, args=(10,))
    r1c2.button("+$50", on_click=update_amt, args=(50,))
    r1c3.button("+$100", on_click=update_amt, args=(100,))
    
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.button("-$10", on_click=update_amt, args=(-10,))
    r2c2.button("-$50", on_click=update_amt, args=(-50,))
    r2c3.button("RESET", on_click=update_amt, args=(0,))
    
    amt = st.number_input("Amount ($)", value=float(st.session_state.purchase_amt), step=1.0)
    daily_allowance_post = max(0.0, cap_rem - amt) / max(days_left, 1)
else:
    amt, cap_rem, daily_allowance_pre, daily_allowance_post = 0.0, 2500.0, 27.0, 27.0

st.title("Card Optimizer")
category = st.selectbox("Select Purchase Category", [
    "Online Shopping (General)", "Amazon.com / Whole Foods", 
    "Gas Station / Fuel", "In-Store / Dining / Everything Else"
])
st.markdown("---")

# --- 5. ENGINE ---
def get_robust_decision():
    if "Online" in category:
        if amt > cap_rem: return "BofA Premium Rewards Elite", "2.625%", "Over cap."
        days_impact = amt / max(daily_allowance_pre, 1)
        if days_impact > 4.0 and cap_rem < 1000:
            return "BofA Premium Rewards Elite", "2.625%", f"Rationing: Eats {days_impact:.1f} days."
        if daily_allowance_post < 10.0 and daily_allowance_pre > 10.0:
             return "BofA Premium Rewards Elite", "2.625%", "Protecting $10/day floor."
        return "BofA Customized Cash Rewards", "5.25%", "Optimal use of cap."
    if "Amazon" in category: return "Amazon Prime Visa", "5.0%", "Merchant rate."
    if "Gas" in category: return "Costco Anywhere Visa", "4.0%", "Gas rate."
    return "BofA Premium Rewards Elite", "2.625%+", "Catch-all rate."

card, rate_str, reason = get_robust_decision()
apply_card_style(card)
st.error(f"{card}")

if app_mode:
    try: clean_rate = float(rate_str.replace('%', '').replace('+', '')) / 100
    except: clean_rate = 0.02625
    is_ccr = "Customized Cash" in card
    total_earned = (min(amt, cap_rem) * 0.0525) if is_ccr else (amt * clean_rate)
    st.markdown(f'<div class="insight-box"><div class="insight-title">Analysis</div><div class="insight-text">• <b>Yield:</b> {rate_str} (${total_earned:.2f})<br>• <b>Verdict:</b> {reason}</div></div>', unsafe_allow_html=True)
