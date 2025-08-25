import streamlit as st
import pandas as pd
from utils import fetch_and_save_chain, get_latest_csv
from strategy import simulate_disparity_trades

st.set_page_config(page_title="Disparity Dashboard", layout="wide")
st.title("📈 Buy-Only Disparity Strategy")

symbol = st.selectbox("Symbol", ["BANKNIFTY", "NIFTY"])

if st.button("🔄 Fetch & Save Option Chain"):
    path, pcr = fetch_and_save_chain(symbol)
    if path:
        st.success(f"Saved: {path}")
        st.metric("PCR", pcr)
    else:
        st.error("Fetch failed or empty response.")

latest = get_latest_csv(symbol)
if latest:
    df = pd.read_csv(latest)
    trades = simulate_disparity_trades(df)

    st.subheader("🧾 Trade Log")
    st.dataframe(trades)

    st.subheader("📅 Daily PnL")
    st.dataframe(trades.groupby("Date")["PnL"].sum().reset_index())

    st.subheader("🗓️ Monthly PnL")
    trades["Month"] = pd.to_datetime(trades["Exit"]).dt.to_period("M")
    st.dataframe(trades.groupby("Month")["PnL"].sum().reset_index())
else:
    st.info("No saved file found.")
