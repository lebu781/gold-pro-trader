import streamlit as st
import json
import os
import pandas as pd
import websocket
import time

st.set_page_config(page_title="GOLD PRO TRADER", layout="wide")
st.title("🔥 GOLD PRO TRADER - ULTRA REAL")

if not os.path.exists("balance.json"):
    json.dump({"balance": 0.0, "trades": []}, open("balance.json","w"))
data = json.load(open("balance.json"))
st.metric("Balance (Demo Log)", f"${data['balance']:.2f}")

st.line_chart(pd.DataFrame({"Gold": [2650,2652,2648,2655,2660,2658,2662,2659]}))

st.divider()
st.subheader("💰 REAL MONEY - DERIV")
dep = st.number_input("Stake Amount $", value=1.0, min_value=1.0, step=1.0)
colA,colB = st.columns(2)
with colA:
    st.link_button("🔵 Deposit via DERIV", "https://app.deriv.com/cashier/deposit", use_container_width=True)
with colB:
    st.link_button("🔴 Withdraw via DERIV", "https://app.deriv.com/cashier/withdrawal", use_container_width=True)

st.divider()
st.subheader("🔗 Connect Your Deriv API")
deriv_token = st.text_input("Deriv API Token", type="password", help="app.deriv.com > Account Settings > API Token")
if deriv_token:
    st.session_state['deriv_token'] = deriv_token

is_real = 'deriv_token' in st.session_state and st.session_state['deriv_token']

def deriv_real_trade(token, is_buy=True, stake=1.0):
    try:
        ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089", timeout=15)
        # Authorize
        ws.send(json.dumps({"authorize": token}))
        auth = json.loads(ws.recv())
        if "error" in auth:
            return False, auth["error"]["message"]
        
        contract = "CALL" if is_buy else "PUT"
        # Proposal
        ws.send(json.dumps({
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": contract,
            "currency": "USD",
            "duration": 5,
            "duration_unit": "t",
            "symbol": "frxXAUUSD"
        }))
        prop = json.loads(ws.recv())
        if "error" in prop:
            return False, prop["error"]["message"]
        
        # Buy
        ws.send(json.dumps({"buy": prop["proposal"]["id"], "price": stake}))
        buy_res = json.loads(ws.recv())
        ws.close()
        
        if "error" in buy_res:
            return False, buy_res["error"]["message"]
        return True, f"Contract ID {buy_res['buy']['contract_id']} - {contract} Gold ${stake}"
    except Exception as e:
        return False, str(e)

if is_real:
    st.success("✅ Deriv Connected! ULTRA REAL MODE")
    st.error("🔴 LIVE: Trades will execute in your Deriv account!")
else:
    st.info("🟢 DEMO: Enter token for ULTRA REAL Deriv execution")

st.link_button("Get FREE API Token", "https://app.deriv.com/account/api-token", use_container_width=True)

st.divider()
st.subheader("📈 Trade Gold - ULTRA REAL")
col_buy, col_sell = st.columns(2)

with col_buy:
    if st.button("🟢 BUY GOLD - REAL", use_container_width=True):
        if is_real:
            with st.spinner("Executing REAL trade on Deriv..."):
                ok, msg = deriv_real_trade(st.session_state['deriv_token'], True, dep)
                if ok:
                    st.success(f"✅ REAL BUY EXECUTED! {msg}")
                    st.balloons()
                    data["trades"].append({"time":str(pd.Timestamp.now())[:19], "side":"BUY REAL EXECUTED", "profit":float(dep)})
                else:
                    st.error(f"Deriv Failed: {msg}")
        else:
            st.warning("Enter Deriv Token first!")
            data["trades"].append({"time":str(pd.Timestamp.now())[:19], "side":"BUY DEMO", "profit":1})
        json.dump(data, open("balance.json","w"))
        time.sleep(1)
        st.rerun()

with col_sell:
    if st.button("🔴 SELL GOLD - REAL", use_container_width=True):
        if is_real:
            with st.spinner("Executing REAL trade on Deriv..."):
                ok, msg = deriv_real_trade(st.session_state['deriv_token'], False, dep)
                if ok:
                    st.success(f"✅ REAL SELL EXECUTED! {msg}")
                    data["trades"].append({"time":str(pd.Timestamp.now())[:19], "side":"SELL REAL EXECUTED", "profit":-float(dep)})
                else:
                    st.error(f"Deriv Failed: {msg}")
        else:
            st.warning("Enter Deriv Token first!")
            data["trades"].append({"time":str(pd.Timestamp.now())[:19], "side":"SELL DEMO", "profit":-1})
        json.dump(data, open("balance.json","w"))
        time.sleep(1)
        st.rerun()

st.divider()
if data["trades"]:
    st.write("### History")
    for t in reversed(data["trades"][-10:]):
        st.write(f"{t['time']} - {t['side']}")
    st.caption("Check your trades live at: app.deriv.com -> Portfolio / Profit Table")
