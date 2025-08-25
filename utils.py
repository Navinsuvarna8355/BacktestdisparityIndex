import requests
import json
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
    return strikes, pcr
