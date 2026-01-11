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
        /* REVERTED TO STACKED: Optimized for vertical flow */
        
        /* Reduce gap between Streamlit elements globally */
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}

        .stButton>button {{ 
            width: 100% !important; 
            height: 3em !important; 
            background-color: #262730 !important; 
            color: white !important;           
            border: 1px solid #464855 !important;
            font-weight: bold !important;
        }}

        .stAlert {{ 
            background: linear-gradient(135deg, {bg_color} 0%, #1A1A1A 160%) !important; 
            padding: 15px !important; 
            border-radius: 12px !important;
        }}
        .stAlert h2 {{ font-size: 1.1rem !important; margin: 0px !important; }}

        .insight-box {{ 
            background-color: #ffffff; 
            padding: 10px; 
            border-radius: 8px; 
            border: 1px solid #e0e0e0; 
            margin-top: 5px; 
        }}
        .insight-text {{ color: #444; font-size: 0.8rem; line-height: 1.3; }}
        
        /* Hide the header anchor icons */
        .element-container h1, .element-container h2, .element-container h3 {{ margin-top: -10px !important; }}
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
app_mode = st.sidebar.toggle("Detailed Mode", value=True)

if app_mode:
    # Compacted Slider
    ccr_spent = st.slider("CCR QTD Spend", 0, 2500, value=int(st.session_state.get('saved_ccr', ideal_pace_val)), step=50)
    st.session_state['saved_ccr'] = ccr_spent
    cap_rem = 2500.0 - ccr_spent
    daily_allowance_pre = cap_rem / max(days_left, 1)

    # Reverted to stacked columns for iPhone stability
    c1, c2, c3 = st.columns(3)
    c1.button("+$10", on_click=update_amt, args=(10,))
    c2.button("+$50", on_click=update_amt, args=(50,))
    c3.button("+$100", on_click=update_amt, args=(100,))
    
    m1, m2, m3 = st.columns(3)
    m1.button("-$10", on_click=update_amt, args=(-10,))
    m2.button("-$50", on_click=update_amt, args=(-50,))
    m3.button("RESET", on_click=update_amt, args=(0,))
    
    amt = st.number_input("Purchase Amount ($)", value=float(st.session_state.purchase_amt), step=1.0)
    daily_allowance_post = max(0.0, cap_rem - amt) / max(days_left, 1)
else:
    amt, cap_rem, daily_allowance_pre, daily_allowance_post = 0.0, 2500.0, 27.0, 27.0

st.title("Card Optimizer")
category = st.selectbox("Category", ["Online", "Amazon", "Gas", "Other"])

# --- 5. ENGINE ---
def get_decision():
    if "Online" in category:
        if amt > cap_rem: return "BofA Premium Elite", "2.625%", "Over cap."
        days_impact = amt / max(daily_allowance_pre, 1)
        if days_impact > 4.0 and cap_rem < 1000:
            return "BofA Premium Elite", "2.625%", f"Eats {days_impact:.1f} days budget."
        if daily_allowance_post < 10.0 and daily_allowance_pre > 10.0:
             return "BofA Premium Elite", "2.625%", "$10/day floor reached."
        return "BofA Customized Cash", "5.25%", "Optimal use of cap."
    if "Amazon" in category: return "Amazon Prime Visa", "5.0%", "Merchant rate."
    if "Gas" in category: return "Costco Visa", "4.0%", "Gas rate."
    return "BofA Premium Elite", "2.625%+", "Catch-all."

card, rate_str, reason = get_decision()
apply_card_style(card)
st.error(f"**{card}**")

if app_mode:
    try: clean_rate = float(rate_str.replace('%', '').replace('+', '')) / 100
    except: clean_rate = 0.02625
    is_ccr = "Customized Cash" in card
    total_earned = (min(amt, cap_rem) * 0.0525) if is_ccr else (amt * clean_rate)
    st.markdown(f'<div class="insight-box"><div class="insight-text"><b>{rate_str} (${total_earned:.2f})</b> | {reason}</div></div>', unsafe_allow_html=True)
