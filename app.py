import streamlit as st
from datetime import date, timedelta
from logic import get_recommendations, CCR_QUARTERLY_CAP
import pathlib

# --- Styles: load external CSS ---
css_path = pathlib.Path(__file__).with_name("styles.css")
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Card Optimizer Pro [FEATURE BRANCH]", page_icon="⚖️")

# Visible test banner for branch verification
st.markdown("""
<div style='background:#ffe6e6;padding:12px;border-radius:8px;border:2px solid #ff4d4d;margin-bottom:12px'>
  <strong style='color:#b30000'>TEST DEPLOY: feature/streamlit-test</strong> — this deployment is from the feature branch for verification.
</div>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE & HELPERS ---
if 'purchase_amt' not in st.session_state:
    st.session_state.purchase_amt = 0.0

def update_amt(value):
    if value == 0:
        st.session_state.purchase_amt = 0.0
    else:
        st.session_state.purchase_amt = max(0.0, st.session_state.purchase_amt + float(value))

# --- 3. TIME & PACE LOGIC ---
today = date.today()
q_start_month = ((today.month - 1) // 3) * 3 + 1
q_start_date = date(today.year, q_start_month, 1)
q_end_date = (date(today.year, q_start_month + 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
days_total = (q_end_date - q_start_date).days + 1
days_left = max(1, (q_end_date - today).days + 1)
ideal_pace_val = ((days_total - days_left) / days_total) * CCR_QUARTERLY_CAP

# --- 4. UI INPUTS ---
st.sidebar.title("Settings")
app_mode = st.sidebar.toggle("Detailed Strategy Mode", value=True)

if app_mode:
    st.subheader("1. Quarterly CCR Cap Spend")
    ccr_spent = st.slider("Total 5.25% Category Spend ($)", 0, int(CCR_QUARTERLY_CAP), value=int(st.session_state.get('saved_ccr', ideal_pace_val)), step=50)
    st.markdown(f'<div class="pace-marker">Target: ${ideal_pace_val:.0f} | Days Remaining: {days_left}</div>', unsafe_allow_html=True)
    st.session_state['saved_ccr'] = ccr_spent
    cap_rem = max(0.0, CCR_QUARTERLY_CAP - ccr_spent)
    daily_allowance_pre = cap_rem / days_left

    st.subheader("2. New Purchase Amount")
    c1, c2, c3 = st.columns(3)
    c1.button("+$10", on_click=update_amt, args=(10,))
    c2.button("+$50", on_click=update_amt, args=(50,))
    c3.button("+$100", on_click=update_amt, args=(100,))
    m1, m2, m3 = st.columns(3)
    m1.button("-$10", on_click=update_amt, args=(-10,))
    m2.button("-$50", on_click=update_amt, args=(-50,))
    m3.button("RESET", on_click=update_amt, args=(0,))

    amt = st.number_input("Amount ($)", value=float(st.session_state.purchase_amt), step=1.0, min_value=0.0)
    st.session_state.purchase_amt = float(amt)
    daily_allowance_post = max(0.0, cap_rem - amt) / days_left
else:
    amt, cap_rem, daily_allowance_pre, daily_allowance_post = 0.0, CCR_QUARTERLY_CAP, 27.0, 27.0

# --- 5. CATEGORY SELECT ---
st.title("Card Optimizer")
category = st.selectbox("Select Purchase Category", [
    "Online Shopping (General)", "Amazon.com / Whole Foods",
    "Gas Station / Fuel", "In-Store / Dining / Everything Else"
])
st.markdown("---")

# --- 6. DECISION (via logic.py) ---
recs = get_recommendations(category, amt, cap_rem)
if recs:
    top = recs[:2]
    # Display top recommendations as a small table
    rows = []
    for r in top:
        rows.append({
            "Card": r.card.name,
            "Estimated $ Back": f"${r.cashback:.2f}",
            "Notes": r.reason
        })
    st.table(rows)
    best = recs[0]
    st.error(f"{best.card.name} — Estimated ${best.cashback:.2f}")
else:
    st.warning("No recommendation available.")

# --- 7. STRATEGY INSIGHT (keeps existing UX) ---
if app_mode:
    st.markdown('<div class="insight-box"><div class="insight-title">Strategic Analysis</div><div class="insight-text">', unsafe_allow_html=True)
    st.write(f"• **Amount:** ${amt:.2f} • **CCR remaining:** ${cap_rem:.2f}")
    st.write(f"• **Top recommendation:** {recs[0].card.name if recs else '—'} (${recs[0].cashback:.2f} if recs else '')")
    if "Online" in category:
        st.write(f"• **Daily allowance (pre):** ${daily_allowance_pre:.2f}/day")
        st.write(f"• **Daily allowance (post):** ${daily_allowance_post:.2f}/day")
    st.write(f"• **Verdict:** {recs[0].reason if recs else ''}")
    st.markdown('</div></div>', unsafe_allow_html=True)
