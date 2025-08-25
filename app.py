import streamlit as st
import pandas as pd
from utils import (
    fetch_option_chain,
    parse_option_chain,
    save_option_chain,
    get_latest_csv,
    simulate_disparity_trades
)

st.set_page_config(page_title="Buy-Only Disparity Dashboard", layout="wide")
st.title("📊 Buy-Only Disparity Strategy — CE & PE")

symbol = st.selectbox("Select Symbol", ["BANKNIFTY", "NIFTY"])

if st.button("🔄 Fetch Live Option Chain"):
    try:
        raw_data = fetch_option_chain(symbol)
        df_chain, pcr = parse_option_chain(raw_data)

        if not df_chain.empty:
            st.metric(label="Put/Call Ratio (PCR)", value=pcr)
            st.dataframe(df_chain, use_container_width=True)
            saved_path = save_option_chain(df_chain, symbol)
            st.success(f"✅ Saved to: {saved_path}")
        else:
            st.warning("⚠️ No data fetched — CSV not saved.")
    except Exception as e:
        st.error(f"❌ Fetch failed: {e}")

st.subheader("📂 Backtest — Buy CE & Buy PE Only")
latest_file = get_latest_csv(symbol)

if latest_file:
    df_backtest = pd.read_csv(latest_file)
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
    st.info("ℹ️ No saved option chain file found.")
