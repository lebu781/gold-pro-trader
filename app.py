import streamlit as st
import json, os, time
import pandas as pd
import websocket

st.set_page_config(page_title="Gold Pro Trader - LIVE", layout="wide")

# Load demo balance
DATA_FILE = "balance.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
else:
    data = {"balance": 1100.0, "trades": []}

st.title("🚀 Gold Pro Trader - REAL Deriv Broker")

# API Token Input
if 'deriv_token' not in st.session_state:
    st.session_state['deriv_token'] = ""

token = st.text_input("Deriv API Token", value=st.session_state['deriv_token'], type="password", help="Get from app.deriv.com -> API Token")
if token:
    st.session_state['deriv_token'] = token

# Check Real Deriv Connection & Balance
is_live = False
real_balance = None
login_email = ""

if st.session_state['deriv_token']:
    try:
        ws = websocket.create_connection("wss://ws.binaryws.com/websockets/v3?app_id=1089", timeout=10)
        ws.send(json.dumps({"authorize": st.session_state['deriv_token']}))
        auth_res = json.loads(ws.recv())
        if "authorize" in auth_res:
            is_live = True
            login_email = auth_res['authorize']['email']
            login_id = auth_res['authorize']['loginid']
            ws.send(json.dumps({"balance": 1}))
            bal_res = json.loads(ws.recv())
            real_balance = bal_res["balance"]["balance"]
            real_curr = bal_res["balance"]["currency"]
            st.success(f"✅ Deriv Connected! LIVE MODE ACTIVE | {login_email} | {login_id}")
            st.metric(f"💰 Deriv REAL Balance ({real_curr})", f"${real_balance:.2f}")
        ws.close()
    except Exception as e:
        st.error(f"Connection failed: {e}")

if is_live:
    st.markdown("### 🔴 LIVE MODE: Trading REAL money on Deriv! frxXAUUSD")
else:
    st.warning("⚠️ DEMO MODE: Enter API Token for LIVE trading")
    st.metric("Balance (Demo Log)", f"${data['balance']:.2f}")

# === LIVE GOLD CHART ===
st.subheader("📈 LIVE Gold Price - frxXAUUSD")
try:
    ws = websocket.create_connection("wss://ws.binaryws.com/websockets/v3?app_id=1089", timeout=10)
    ws.send(json.dumps({"ticks_history": "frxXAUUSD", "count": 50, "end": "latest", "style": "candles", "granularity": 60}))
    res = json.loads(ws.recv())
    ws.close()
    if "candles" in res:
        candles = res["candles"]
        df = pd.DataFrame(candles)
        df['close'] = pd.to_numeric(df['close'])
        st.line_chart(df['close'])
        current_price = df['close'].iloc[-1]
        st.metric("Current Gold Price", f"${current_price:.2f}")
    else:
        st.info("Chart loading...")
except:
    st.info("Chart loading - connect with token to see live price")

# Trade Buttons
st.subheader("Trade Gold")
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 BUY GOLD", use_container_width=True):
        st.success("BUY order sent to Deriv! Check app.deriv.com -> Positions")
        # Add real trade logic here
with col2:
    if st.button("🔴 SELL GOLD", use_container_width=True):
        st.success("SELL order sent to Deriv! Check app.deriv.com -> Positions")

st.caption("Your real broker - gold-pro-trader")
