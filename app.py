import streamlit as st
import pandas as pd
from utils import fetch_option_chain, parse_option_chain

st.set_page_config(page_title="Live Option Chain — BANKNIFTY", layout="wide")
st.title("📊 BANKNIFTY Option Chain Dashboard")

symbol = st.selectbox("Select Symbol", ["BANKNIFTY", "NIFTY"])

st.subheader(f"🔄 Fetching Option Chain for {symbol}")
try:
    raw_data = fetch_option_chain(symbol)
    strikes, pcr = parse_option_chain(raw_data)
    df = pd.DataFrame(strikes)

    st.metric(label="Put/Call Ratio (PCR)", value=pcr)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("📥 Download Option Chain", csv, f"{symbol}_option_chain.csv", "text/csv")
except Exception as e:
    st.error(f"⚠️ Error fetching data: {e}")
