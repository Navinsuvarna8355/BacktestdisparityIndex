import requests, json, pandas as pd, os
from datetime import datetime
import pytz

def fetch_and_save_chain(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}
        session = requests.Session()
        session.get("https://www.nseindia.com/option-chain", headers=headers)
        res = session.get(url, headers=headers, timeout=10)
        data = json.loads(res.text)

        expiry = data["records"]["expiryDates"][0]
        rows, ce_total, pe_total = [], 0, 0

        for item in data["records"]["data"]:
            if item["expiryDate"] != expiry: continue
            strike = item["strikePrice"]
            ce = item.get("CE", {})
            pe = item.get("PE", {})
            ce_oi, pe_oi = ce.get("openInterest", 0), pe.get("openInterest", 0)
            ce_iv, pe_iv = ce.get("impliedVolatility", None), pe.get("impliedVolatility", None)
            ce_total += ce_oi
            pe_total += pe_oi

            rows.append({
                "Strike": strike,
                "CE_OI": ce_oi,
                "PE_OI": pe_oi,
                "CE_IV": ce_iv,
                "PE_IV": pe_iv,
                "Timestamp_IST": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
            })

        df = pd.DataFrame(rows)
        if df.empty: return None, None

        os.makedirs("data", exist_ok=True)
        fname = f"data/{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(fname, index=False)
        return fname, round(pe_total / ce_total, 2)
    except Exception:
        return None, None

def get_latest_csv(symbol):
    files = sorted([f for f in os.listdir("data") if f.startswith(symbol)], reverse=True)
    return os.path.join("data", files[0]) if files else None
