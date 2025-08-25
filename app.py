from utils import load_saved_option_chain, simulate_disparity_trades

st.subheader("📂 Backtest Disparity Strategy")
uploaded_file = st.file_uploader("Upload Saved Option Chain CSV", type="csv")

if uploaded_file:
    df = load_saved_option_chain(uploaded_file)
    trades = simulate_disparity_trades(df)

    st.subheader("🧾 Trade Log")
    st.dataframe(trades)

    # Daily PnL
    trades["Date"] = trades["Exit"].dt.date
    daily_pnl = trades.groupby("Date")["PnL"].sum().reset_index()
    st.subheader("📅 Daily PnL")
    st.dataframe(daily_pnl)

    # Monthly PnL
    trades["Month"] = trades["Exit"].dt.to_period("M")
    monthly_pnl = trades.groupby("Month")["PnL"].sum().reset_index()
    st.subheader("🗓️ Monthly PnL")
    st.dataframe(monthly_pnl)
