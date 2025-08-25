import streamlit as st
from utils import (
    load_data,
    signal_engine,
    backtest_trades,
    monthly_pnl_summary,
    daily_pnl_summary,
    reasoning_panel
)

st.set_page_config(page_title="5-Year Backtest — NIFTY & BANKNIFTY", layout="wide")
st.title("📊 5-Year Strategy Backtest")
symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY"])

df = load_data(symbol)
df = signal_engine(df)
trades = backtest_trades(df, symbol)

st.subheader("📈 Signal Table")
st.dataframe(df.tail(50), use_container_width=True)

st.subheader("📘 Trade Log")
st.dataframe(trades, use_container_width=True)
st.download_button("Download Trade Log", trades.to_csv(index=False).encode("utf-8"), f"{symbol}_backtest_trades.csv", "text/csv")

st.subheader("📆 Monthly PnL")
monthly_df = monthly_pnl_summary(trades)
st.dataframe(monthly_df, use_container_width=True)
st.download_button("Download Monthly PnL", monthly_df.to_csv(index=False).encode("utf-8"), f"{symbol}_monthly_pnl.csv", "text/csv")

st.subheader("📅 Daily PnL")
daily_df = daily_pnl_summary(trades)
st.dataframe(daily_df.tail(30), use_container_width=True)
st.download_button("Download Daily PnL", daily_df.to_csv(index=False).encode("utf-8"), f"{symbol}_daily_pnl.csv", "text/csv")

st.subheader("🧠 Reasoning Panel")
st.json(reasoning_panel(df))

