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
        /* Main Result Card */
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
        
        /* Neutral Status Plates */
        .status-plate {{ 
            background-color: rgba(128, 128, 128, 0.1); 
            border: 1px solid rgba(128, 128, 128, 0.2); 
            border-radius: 8px; 
            padding: 12px; 
            margin-top: 10px;
        }}
        .status-val {{ 
            font-size: 0.85rem; 
            font-family: 'Source Code Pro', monospace; 
            line-height: 1.6;
        }}

        /* --- UI/UX BUTTON IMPROVEMENTS --- */
        /* Target buttons by their labels using data-testid or generic button styling */
        div.stButton > button:first-child {{
            border-radius: 8px;
            font-weight: 600 !important;
        }}
        
        /* Unique styling for Add vs Subtract vs Reset */
        div.stButton > button:contains("+") {{
            border-color: #2E7D32 !important;
            color: #2E7D32 !important;
        }}
        div.stButton > button:contains("−") {{
            border-color: #C62828 !important;
            color: #C62828 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

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

r_online = 0.03 * m
r_base = 0.015 * m
r_travel_dining = 0.02 * m
r_fallback = 0.01 * m 

st.sidebar.markdown(f"""
    <div class="status-plate">
        <div class="status-val">
            <b>{tier} Yields</b><br>
            • Online Shopping: {fmt_pct(r_online)}<br>
            • Travel/Dining: {fmt_pct(r_travel_dining)}<br>
            • Other (Inc. Grocery): {fmt_pct(r_base)}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(v):
    if v == 0: st.session_state.purchase_amt = 0.0
    else: st.session_state.purchase_amt = max(0.0, st.session_state.purchase_amt + float(v))

today = date.today()
q_start = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
q_end = (date(today.year, q_start.month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_total = (q_end - q_start).days + 1
days_elapsed = (today - q_start).days + 1
pace = (days_elapsed / days_total) * 2500

# DYNAMIC BUFFER LOGIC
if days_elapsed <= 30:
    flex_pct = 0.25 
elif days_elapsed <= 60:
    flex_pct = 0.15 
else:
    flex_pct = 0.05 

safety_threshold = pace + (2500 * flex_pct)

# --- 4. MAIN INTERFACE ---
if app_mode:
    st.subheader("Quarterly Tracking")
    spent = st.slider("CCR Category Spend ($)", 0, 2500, value=int(st.session_state.get('s_ccr', pace)), step=50)
    st.session_state['s_ccr'] = spent
    rem = 2500.0 - spent
    
    st.subheader("New Purchase")
    # Using specific buttons with color-coded intent
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.button("+10", on_click=update_amt, args=(10,))
    c2.button("+50", on_click=update_amt, args=(50,))
    c3.button("+100", on_click=update_amt, args=(100,))
    c4.button("−10", on_click=update_amt, args=(-10,))
    c5.button("−50", on_click=update_amt, args=(-50,))
    if c6.button("RESET"): update_amt(0)
    
    amt = st.number_input("Amount ($)", value=float(st.session_state.purchase_amt))
    cat_options = ["Online Shopping", "Amazon / Whole Foods", "Gas / Fuel", "Travel / Dining", "Other / General"]
else:
    amt, rem = 0.0, 2500.0
    cat_options = ["Online Shopping", "Amazon / Whole Foods", "Gas / Fuel", "Travel / Dining / Other"]

st.title("Card Optimizer")
cat = st.selectbox("Category", cat_options)

# --- 5. DECISION ENGINE ---
def decide():
    if "Online" in cat:
        if app_mode:
            if amt > rem:
                return "BofA Premium Rewards Elite", fmt_pct(r_base), "Cap exceeded."
            if spent > safety_threshold:
                return "BofA Premium Rewards Elite", fmt_pct(r_base), f"Cap Preservation (>${safety_threshold:,.0f})."
        return "BofA Customized Cash", fmt_pct(r_online), "Max yield."
    
    if "Amazon" in cat: return "Amazon Prime Visa", "5%", "Prime Member rate."
    if "Gas" in cat: return "Costco Anywhere Visa", "4%", "Uncapped fuel."
    if "Travel / Dining" in cat: 
        return "BofA Premium Rewards Elite", fmt_pct(r_travel_dining), f"{tier} rate."
    
    return "BofA Premium Rewards Elite", fmt_pct(r_base), "Catch-all floor."

card, rate, reason = decide()
apply_app_styles(card)
st.error(f"{card}")

if app_mode:
    st.markdown(f"""
        <div class="status-plate">
            <div class="status-val">
                <b>Yield:</b> {rate} | <b>Reason:</b> {reason}<br>
                <b>Cap:</b> ${rem:,.0f} rem | <b>Limit:</b> ${safety_threshold:,.0f}
            </div>
        </div>
    """, unsafe_allow_html=True)
