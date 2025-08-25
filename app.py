import streamlit as st
import pandas as pd
from datetime import datetime
from utils import fetch_option_chain, parse_option_chain, simulate_disparity_trades

st.set_page_config(page_title="Option Chain + Backtest", layout="wide")
st.title("📈 Live Option Chain + Disparity Backtest")

# Live Option Chain Panel
symbol = st.selectbox("Select Symbol", ["BANKNIFTY", "NIFTY"])
st.subheader(f"🔄 Fetching Option Chain for {symbol}")

try:
    raw_data = fetch_option_chain(symbol)
    df_chain, pcr = parse_option_chain(raw_data)

    st.metric(label="Put/Call Ratio (PCR)", value=pcr)
    st.dataframe(df_chain, use_container_width=True)

    # Save CSV with IST timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/{symbol}_option_chain_{timestamp}.csv"
    df_chain.to_csv(filename, index=False)
    st.success(f"✅ Option chain saved to: {filename}")

    st.download_button("📥 Download Option Chain", df_chain.to_csv(index=False), f"{symbol}_option_chain.csv", "text/csv")
except Exception as e:
    st.error(f"⚠️ Error fetching data: {e}")

# Backtest Panel
st.subheader("📂 Backtest Disparity Strategy")
uploaded_file = st.file_uploader("Upload Saved Option Chain CSV", type="csv")

if uploaded_file:
    df_backtest = pd.read_csv(uploaded_file, parse_dates=["Timestamp_IST"])
    trades = simulate_disparity_trades(df_backtest)

    st.subheader("🧾 Trade Log")
    st.dataframe(trades)

    # Daily PnL
    trades["Date"] = pd.to_datetime(trades["Exit"]).dt.date
    daily_pnl = trades.groupby("Date")["PnL"].sum().reset_index()
    st.subheader("📅 Daily PnL")
    st.dataframe(daily_pnl)

    # Monthly PnL
    trades["Month"] = pd.to_datetime(trades["Exit"]).dt.to_period("M")
    monthly_pnl = trades.groupby("Month")["PnL"].sum().reset_index()
    st.subheader("🗓️ Monthly PnL")
    st.dataframe(monthly_pnl)
