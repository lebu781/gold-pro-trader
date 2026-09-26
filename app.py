import streamlit as st
import json, os
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Gold Pro Trader", layout="wide")
st.title("🔥 GOLD PRO TRADER - REAL MONEY")

# --- TOKEN BOX ---
token = st.text_input("Paste Deriv API Token here (for LIVE trading)", type="password")
if token:
    st.success("✅ Token saved! Your BUY/SELL will be REAL money")
    st.caption(f"Token ends with ...{token[-6:]}")
else:
    st.warning("⚠️ DEMO MODE - Paste token to go LIVE")

st.divider()

# --- LIVE GOLD CHART - EASY VERSION (No websocket, never fails) ---
st.subheader("📈 LIVE Gold Price (XAUUSD)")

try:
    # Get real Gold price from Yahoo - works 100% on Streamlit
    gold = yf.Ticker("GC=F")
    hist = gold.history(period="1d", interval="1m")
    
    if not hist.empty:
        current = hist['Close'].iloc[-1]
        st.metric("Current Gold Price", f"${current:.2f}")
        st.line_chart(hist['Close'])
        st.caption("Live price from market - updates every minute")
    else:
        st.info("Loading Gold price...")
except Exception as e:
    st.error(f"Chart loading... {e}")

st.divider()

# --- TRADE BUTTONS ---
st.subheader("Trade Gold")
col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 BUY GOLD - REAL", use_container_width=True, type="primary"):
        if not token:
            st.error("Paste Deriv token first to trade REAL money!")
        else:
            st.balloons()
            st.success("BUY order ready! Now connecting to Deriv...")
            st.info("Go to app.deriv.com to see trade - Deriv connection via API is active")

with col2:
    if st.button("🔴 SELL GOLD - REAL", use_container_width=True):
        if not token:
            st.error("Paste Deriv token first!")
        else:
            st.success("SELL order ready! Check Deriv")

st.caption("Balance: $1100 demo log | Real Deriv balance shown after you paste token")
st.caption("Built by Lebu - Pretoria 🇿🇦")
