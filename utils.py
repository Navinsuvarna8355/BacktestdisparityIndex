import requests, json, pandas as pd, os
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
    ce_oi_total, pe_oi_total = 0, 0
    rows = []

    for item in data["records"]["data"]:
        if item["expiryDate"] != current_expiry:
            continue
        strike = item["strikePrice"]
        ce = item.get("CE", {})
        pe = item.get("PE", {})
        ce_oi = ce.get("openInterest", 0)
        pe_oi = pe.get("openInterest", 0)
        ce_iv = ce.get("impliedVolatility", None)
        pe_iv = pe.get("impliedVolatility", None)

        ce_oi_total += ce_oi
        pe_oi_total += pe_oi

        rows.append({
            "Strike": strike,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi,
            "CE_IV": ce_iv,
            "PE_IV": pe_iv,
            "Timestamp_IST": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    pcr = round(pe_oi_total / ce_oi_total, 2) if ce_oi_total else None
    return pd.DataFrame(rows), pcr

def save_option_chain(df, symbol):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data", exist_ok=True)
    filename = f"data/{symbol}_option_chain_{timestamp}.csv"
    df.to_csv(filename, index=False)
    return filename

def get_latest_csv(symbol):
    files = [f for f in os.listdir("data") if f.startswith(symbol) and f.endswith(".csv")]
    files.sort(reverse=True)
    return os.path.join("data", files[0]) if files else None

def simulate_disparity_trades(df, buy_thresh=102, ce_thresh=98):
    trades, position = [], None
    for i in range(1, len(df)):
        row = df.iloc[i]
        disparity = (row["PE_IV"] / row["CE_IV"]) * 100 if row["CE_IV"] else None
        if disparity is None:
            continue

        signal, price = None, None
        if disparity > buy_thresh:
            signal, price = "Buy PE", row["PE_IV"]
        elif disparity < ce_thresh:
            signal, price = "Buy CE", row["CE_IV"]

        if signal and not position:
            position = {"Type": signal, "Entry_Time": row["Timestamp_IST"], "Entry_Price": price}
        elif position and signal and signal.split()[1] == position["Type"].split()[1]:
            exit_price = price
            pnl = exit_price - position["Entry_Price"]
            trades.append({
                "Type": position["Type"],
                "Entry": position["Entry_Time"],
                "Exit": row["Timestamp_IST"],
                "PnL": round(pnl, 2)
            })
            position = None
    return pd.DataFrame(trades)
