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
        .stAlert {{ background: linear-gradient(135deg, {bg_color} 0%, #1A1A1A 160%) !important; border-radius: 15px !important; padding: 20px !important; border: none !important; }}
        .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert div {{ color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; text-align: center !important; }}
        
        .stButton>button {{ 
            width: 100%; 
            border-radius: 8px; 
            height: 3.5em; 
            font-weight: bold; 
            background-color: #262730 !important; 
            color: #ffffff !important;           
            border: 1px solid #464855 !important;
        }}

        .insight-box {{ background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-top: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .insight-title {{ font-weight: bold; color: #1a1a1a; font-size: 0.8rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        .insight-text {{ color: #444; font-size: 0.85rem; line-height: 1.5; }}
        .pace-marker {{ color: #888; font-size: 0.75rem; margin-top: -10px; margin-bottom: 15px; font-family: monospace; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. CALLBACK FUNCTIONS ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(value):
    if value == 0:
        st.session_state.purchase_amt = 0.0
    else:
        st.session_state.purchase_amt += float(value)

# --- 3. TIME & PACE LOGIC ---
today = date.today()
q_start_month = ((today.month - 1) // 3) * 3 + 1
q_start_date = date(today.year, q_start_month, 1)
q_end_date = (date(today.year, q_start_month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_total = (q_end_date - q_start_date
