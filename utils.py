import requests
import json

def fetch_option_chain(symbol="NIFTY"):
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
        pe_oi = pe.get("openInterest", 0)
        ce_iv = ce.get("impliedVolatility", None)
        pe_iv = pe.get("impliedVolatility", None)

        ce_oi_total += ce_oi
        pe_oi_total += pe_oi
        strikes.append({
            "Strike": strike,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi,
            "CE_IV": ce_iv,
            "PE_IV": pe_iv
        })

    pcr = round(pe_oi_total / ce_oi_total, 2) if ce_oi_total else None
    return strikes, pcr
