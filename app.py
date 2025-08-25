import streamlit as st
import pandas as pd
from utils import (
    fetch_option_chain,
    parse_option_chain,
    save_option_chain,
    get_latest_csv,
    simulate_disparity_trades
)

st.set_page_config(page_title="Auto Backtest Dashboard", layout="wide")
st.title("📈 Auto Option Chain + Disparity Backtest")

symbol = st.selectbox("Select Symbol", ["BANKNIFTY", "NIFTY"])
st.subheader(f"🔄 Fetching & Saving Option Chain for {symbol}")

try:
    raw_data = fetch_option_chain(symbol)
    df_chain, pcr = parse_option_chain(raw_data)
    st.metric(label="Put/Call Ratio (PCR)", value=pcr)
    st.dataframe(df_chain, use_container_width=True)

    saved_path = save_option_chain(df_chain, symbol)
    st.success(f"✅ Option chain saved to: {saved_path}")
except Exception as e:
    st.error(f"⚠️ Error fetching data: {e}")

# Backtest Panel
st.subheader("📂 Auto Backtest Disparity Strategy")
latest_file = get_latest_csv(symbol)

if latest_file:
    df_backtest = pd.read_csv(latest_file, parse_dates=["Timestamp_IST"])
    trades = simulate_disparity_trades(df_backtest)

    st.subheader("🧾 Trade Log")
    st.dataframe(trades)

    trades["Date"] = pd.to_datetime(trades["Exit"]).dt.date
    daily_pnl = trades.groupby("Date")["PnL"].sum().reset_index()
    st.subheader("📅 Daily PnL")
    st.dataframe(daily_pnl)

    trades["Month"] = pd.to_datetime(trades["Exit"]).dt.to_period("M")
    monthly_pnl = trades.groupby("Month")["PnL"].sum().reset_index()
    st.subheader("🗓️ Monthly PnL")
    st.dataframe(monthly_pnl)
else:
    st.warning("⚠️ No saved option chain file found.")
