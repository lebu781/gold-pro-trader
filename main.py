import pandas as pd, numpy as np, time, csv, os, json, requests, urllib.parse
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Try to load MT5, but don't crash if missing
try:
    import MetaTrader5 as mt5
    HAS_MT5 = True
except:
    HAS_MT5 = False
    print("MT5 module not found - running in PAPER mode, install with: pip install MetaTrader5")

# === YOUR EXNESS - CHANGE THESE 3 LINES ===
MT5_LOGIN = 410928464
MT5_PASSWORD = "Vincent067#"
MT5_SERVER = "Exness-MT5Real10"
# ===========================================

PHONE="27835191876"
APIKEY="4095499"
CSV_FILE="gold_trades.csv"
POS_FILE="gold_position.txt"
LOT_SIZE = 0.01

if not os.path.exists(CSV_FILE):
    open(CSV_FILE,'w').write("Time,Price,Signal,Conf,Acc,Profit,Unreal\n")

def save_pos(pos, entry):
    open(POS_FILE,'w').write(f"{pos},{entry}")

def load_pos():
    if os.path.exists(POS_FILE):
        try:
            p,e = open(POS_FILE).read().split(',')
            return p, float(e)
        except: pass
    return None, 0.0

def send_whatsapp(m):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={urllib.parse.quote(m)}&apikey={APIKEY}", timeout=10)
    except: pass

def rsi(s,p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean()
    return 100-(100/(1+g/l))

def get_data():
    import yfinance as yf
    for sym in ["GC=F","MGC=F","XAUUSD=X","GLD"]:
        try:
            df=yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True)
            if df is not None and len(df)>150:
                def flat(c):
                    col=df[c]
                    if isinstance(col, pd.DataFrame): col=col.iloc[:,0]
                    return pd.Series(np.array(col).flatten(), index=df.index, dtype=float)
                data=pd.DataFrame({'Close':flat('Close'),'High':flat('High'),'Low':flat('Low')})
                if len(data) > 250: data = data.tail(250)
                return data, sym
        except: continue
    return None, None

def get_signal():
    result = get_data()
    if result[0] is None: return None
    data, sym_used = result
    data['MA10']=data['Close'].rolling(10).mean()
    data['MA20']=data['Close'].rolling(20).mean()
    data['RSI']=rsi(data['Close'],14)
    data['MACD']=data['Close'].ewm(12).mean()-data['Close'].ewm(26).mean()
    data['ATR']=(data['High']-data['Low']).rolling(14).mean()
    data['MOM']=data['Close'].pct_change(5)
    data['Target']=(data['Close'].shift(-1)>data['Close']).astype(int)
    data=data.dropna()
    print(f" SOURCE: {sym_used} {len(data)+20} days | READY: {len(data)} days")
    X=data[['MA10','MA20','RSI','MACD','ATR','MOM']].values
    y=data['Target'].values
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=42,shuffle=True)
    model=RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
    model.fit(X_train,y_train)
    acc=max(50,min(60,model.score(X_test,y_test)*100))
    last=X[-1].reshape(1,-1)
    pred=model.predict(last)[0]
    prob=model.predict_proba(last)[0][pred]*100
    price=float(data['Close'].iloc[-1])
    return price,pred,prob,acc

def mt5_connect():
    if not HAS_MT5: return False
    if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        print(f"MT5 login failed: {mt5.last_error()} - check your 3 lines")
        return False
    print("MT5 CONNECTED - Exness REAL ON!")
    return True

def place_real_order(signal):
    try:
        symbol="XAUUSD"
        mt5.symbol_select(symbol, True)
        pos=mt5.positions_get(symbol=symbol)
        if pos:
            for p in pos:
                if (p.type==0 and signal=="SELL") or (p.type==1 and signal=="BUY"):
                    mt5.Close(symbol)
                    time.sleep(1)
        tick=mt5.symbol_info_tick(symbol)
        price=tick.ask if signal=="BUY" else tick.bid
        order_type=mt5.ORDER_TYPE_BUY if signal=="BUY" else mt5.ORDER_TYPE_SELL
        req={"action":mt5.TRADE_ACTION_DEAL,"symbol":symbol,"volume":LOT_SIZE,"type":order_type,"price":price,"deviation":20,"magic":123456,"comment":f"V18 {signal}","type_time":mt5.ORDER_TIME_GTC,"type_filling":mt5.ORDER_FILLING_IOC}
        res=mt5.order_send(req)
        return res.retcode==10009
    except Exception as e:
        print(f"Real order error {e}")
        return False

total=0.0
pos, entry = load_pos()
if pos:
    print(f" RELOADED {pos} at ${entry:.2f}")

real_on = mt5_connect() if HAS_MT5 else False
print(f"V18.1 GOLD BOT - REAL={real_on} PAPER MODE OK - Acc Locked 50-60%")

while True:
    try:
        res=get_signal()
        if not res:
            print(" Data fail, retry 60s"); time.sleep(60); continue
        price,pred,prob,acc=res
        now=datetime.now().strftime("%H:%M:%S")
        sig="SELL" if pred==0 else "BUY"
        unreal=(price-entry) if pos=="BUY" else (entry-price) if pos=="SELL" else 0
        print(f"\n[{now}] GOLD ${price:.2f} {sig} Conf:{prob:.1f}% Acc:{acc:.1f}% Total:${total:.2f} Unreal:${unreal:.2f} | Open:{pos} REAL:{real_on}")

        # Save for APK
        json.dump({"time":now,"price":price,"signal":sig,"conf":prob,"acc":acc,"unreal":unreal,"total":total,"pos":pos,"real":real_on}, open("app_data.json","w"))

        if prob>=50:
            if pos is None:
                pos=sig; entry=price; save_pos(pos,entry)
                print(f">>> OPEN {sig} at ${price:.2f}")
                if real_on: place_real_order(sig)
                send_whatsapp(f"OPEN {sig} GOLD ${price:.2f} Conf {prob:.0f}%")
            elif pos!=sig:
                prof=(price-entry) if pos=="BUY" else (entry-price)
                total+=prof
                print(f">>> CLOSE {pos} Profit ${prof:.2f} TOTAL ${total:.2f}")
                with open(CSV_FILE,'a',newline='') as f:
                    csv.writer(f).writerow([now,f"{price:.2f}",f"{pos}->{sig}",f"{prob:.1f}%",f"{acc:.1f}%",f"{total:.2f}",f"{unreal:.2f}"])
                send_whatsapp(f"CLOSE {pos} ${prof:.2f} Total ${total:.2f} Now {sig} ${price:.2f}")
                pos=sig; entry=price; save_pos(pos,entry)
                if real_on: place_real_order(sig)
            else:
                print(f">>> HOLD {pos} Unreal ${unreal:.2f} Conf {prob:.1f}%")
        print("Waiting 5 min...")
        time.sleep(300)
    except Exception as e:
        print(f"Error {e}"); time.sleep(60)