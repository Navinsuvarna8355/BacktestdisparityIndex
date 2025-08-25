import requests
import json
import pandas as pd
from datetime import datetime

def fetch_option_chain(symbol="BANKNIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com/option-chain", headers=headers)
    response = session.get(url, headers=headers)
    data = json.loads(response.text)
    return data

def parse_option_chain(data):
    expiry_dates = data["records"]["expiryDates"]
    current_expiry = expiry_dates[0]
    ce_oi_total = 0
    pe_oi_total = 0
    strikes = []

    for item in data["records"]["data"]:
        if item["expiryDate"] != current_expiry:
            continue
        strike = item["strikePrice"]
        ce = item.get("CE", {})
        pe = item.get("PE", {})
        ce_oi = ce.get("openInterest", 0)
        ce_chng_oi = ce.get("changeinOpenInterest", 0)
        ce_iv = ce.get("impliedVolatility", None)

        pe_oi = pe.get("openInterest", 0)
        pe_chng_oi = pe.get("changeinOpenInterest", 0)
        pe_iv = pe.get("impliedVolatility", None)

        ce_oi_total += ce_oi
        pe_oi_total += pe_oi

        strikes.append({
            "Strike": strike,
            "CE_OI": ce_oi,
            "CE_Chng_OI": ce_chng_oi,
            "PE_OI": pe_oi,
            "PE_Chng_OI": pe_chng_oi,
            "CE_IV": ce_iv,
            "PE_IV": pe_iv,
            "Timestamp_IST": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    pcr = round(pe_oi_total / ce_oi_total, 2) if ce_oi_total else None
    return pd.DataFrame(strikes), pcr

def simulate_disparity_trades(df, buy_thresh=102, sell_thresh=98):
    trades = []
    position = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        disparity = (row["PE_IV"] / row["CE_IV"]) * 100 if row["CE_IV"] else None
        if disparity is None:
            continue

        signal = None
        if disparity > buy_thresh:
            signal = "Buy PE"
            price = row["PE_IV"]
        elif disparity < sell_thresh:
            signal = "Sell PE"
            price = row["PE_IV"]
        elif disparity < (200 - buy_thresh):
            signal = "Buy CE"
            price = row["CE_IV"]
        elif disparity > (200 - sell_thresh):
            signal = "Sell CE"
            price = row["CE_IV"]

        if signal and not position:
            position = {
                "Type": signal,
                "Entry_Time": row["Timestamp_IST"],
                "Entry_Price": price
            }
        elif position and signal and signal.split()[0] != position["Type"].split()[0]:
            exit_price = price
            pnl = (exit_price - position["Entry_Price"]) if "Buy" in position["Type"] else (position["Entry_Price"] - exit_price)
            trades.append({
                "Type": position["Type"],
                "Entry": position["Entry_Time"],
                "Exit": row["Timestamp_IST"],
                "PnL": round(pnl, 2)
            })
            position = None

    return pd.DataFrame(trades)
