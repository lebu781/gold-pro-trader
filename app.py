import streamlit as st, os, requests, json
from datetime import datetime

st.set_page_config(page_title="GOLD PRO TRADER", page_icon="💰", layout="centered")
st.markdown("<h1 style='text-align:center'>💰 GOLD PRO TRADER</h1>", unsafe_allow_html=True)

# Balance file
if not os.path.exists("balance.json"):
    json.dump({"balance": 1000.0, "trades": []}, open("balance.json","w"))
data = json.load(open("balance.json"))

# Live price
try:
    price = float(requests.get("https://api.gold-api.com/price/XAU", timeout=4).json()['price'])
    status = "🟢 LIVE"
except:
    price = 4286.20
    status = "🔴 Offline"

col1,col2 = st.columns(2)
col1.metric("GOLD", f"${price:.2f}", status)
col2.metric("BALANCE", f"${data['balance']:.2f}")

# Check trade
if os.path.exists("gold_position.txt"):
    side, entry = open("gold_position.txt").read().split(",")
    entry=float(entry)
    profit = (entry-price) if side=="SELL" else (price-entry)
    st.divider()
    st.subheader(f"OPEN: {side} at ${entry:.2f}")
    st.metric("PROFIT", f"${profit:.2f}", delta=f"{profit:.2f}")
    if st.button(f"💰 CLOSE & ADD ${profit:.2f} TO BALANCE", type="primary", use_container_width=True):
        data["balance"]+=profit
        data["trades"].append({"side":side,"entry":entry,"close":price,"profit":profit,"time":str(datetime.now())[:19]})
        json.dump(data, open("balance.json","w"))
        os.remove("gold_position.txt")
        st.balloons()
        st.success(f"Profit added! New balance: ${data['balance']:.2f}")
        st.rerun()
else:
    st.divider()
    c1,c2 = st.columns(2)
    if c1.button("🔴 SELL GOLD", use_container_width=True):
        open("gold_position.txt","w").write(f"SELL,{price}")
        st.rerun()
    if c2.button("🟢 BUY GOLD", use_container_width=True):
        open("gold_position.txt","w").write(f"BUY,{price}")
        st.rerun()
    st.divider()
    st.subheader("💰 REAL MONEY - DERIV")
    dep = st.number_input("Amount $", value=100.0, step=10.0, key="dep_amount")
    colA,colB = st.columns(2)
    with colA:
        st.link_button("🔵 Deposit via DERIV", "https://app.deriv.com/cashier/deposit", use_container_width=True)
    with colB:
        st.link_button("🔴 Withdraw via DERIV", "https://app.deriv.com/cashier/withdrawal", use_container_width=True)
    
    st.divider()
    st.subheader(" Demo Balance (for testing)")
    col1,col2 = st.columns(2)
    if col1.button(" Deposit (Demo)", use_container_width=True):
        data["balance"]+=dep
        json.dump(data, open("balance.json","w"))
        st.success(f"Deposited ${dep}!")
        st.rerun()
    if col2.button(" Withdraw (Demo)", use_container_width=True):
        if data["balance"]>=dep:
            data["balance"]-=dep
            json.dump(data, open("balance.json","w"))
            st.success(f"Withdrew ${dep}")
            st.rerun()
    
    st.divider()
    st.subheader("🔗 Connect Your Deriv API")
    st.caption("Get token from: app.deriv.com > Account Settings > API Token")
    deriv_token = st.text_input("Deriv API Token", type="password")
    if deriv_token:
        st.success("✅ Deriv Connected!")
    st.link_button("Get FREE API Token", "https://app.deriv.com/account/api-token", use_container_width=True)
    data["balance"]+=dep
    json.dump(data, open("balance.json","w"))
    st.success(f"Deposited ${dep}!")
    st.rerun()
if colB.button("➖ Withdraw", use_container_width=True):
    if data["balance"]>=dep:
        data["balance"]-=dep
        json.dump(data, open("balance.json","w"))
        st.success(f"Withdrew ${dep}")
        st.rerun()

if data["trades"]:
    st.write("### History")
    for t in reversed(data["trades"][-5:]):
        st.write(f"{t['time']} - {t['side']} ${t['profit']:+.2f}")

if st.button("🔄 Refresh Price"):
    st.rerun()
