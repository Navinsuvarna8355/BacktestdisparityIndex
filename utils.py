import pandas as pd
import numpy as np
import datetime
import pytz

def load_data(symbol):
    path = f"data/{symbol.lower()}_5y.csv"
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

def signal_engine(df, short=9, long=20, lower_thresh=-3, upper_thresh=4):
    df["EMA_short"] = df["close"].ewm(span=short, adjust=False).mean()
    df["EMA_long"] = df["close"].ewm(span=long, adjust=False).mean()
    df["Disparity"] = ((df["close"] - df["EMA_long"]) / df["EMA_long"]) * 100
    df["Signal"] = ""
    df.loc[df["Disparity"] < lower_thresh, "Signal"] = "BUY"
    df.loc[df["Disparity"] > upper_thresh, "Signal"] = "SELL"
    df["Price"] = df["close"].round(2)
    return df

def backtest_trades(df, symbol):
    lot_sizes = {"NIFTY": 75, "BANKNIFTY": 30}
    lot_size = lot_sizes.get(symbol, 1)
    trades = []
    position = None
    entry_price = None
    entry_time = None
    cumulative_pnl = 0
    for _, row in df.iterrows():
        signal = row["Signal"]
        price = row["Price"]
        time = row["timestamp"]
        if signal == "BUY" and position is None:
            position = "LONG"
            entry_price = price
            entry_time = time
        elif signal == "SELL" and position == "LONG":
            exit_price = price
            exit_time = time
            pnl = round((exit_price - entry_price) * lot_size, 2)
            cumulative_pnl += pnl
            trades.append({
                "Symbol": symbol,
                "Entry Time": entry_time,
                "Entry Price": entry_price,
                "Exit Time": exit_time,
                "Exit Price": exit_price,
                "PnL per lot": pnl,
                "Cumulative PnL": cumulative_pnl,
                "Lot Size": lot_size
            })
            position = None
    return pd.DataFrame(trades)

def monthly_pnl_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["Month", "Total_Trades", "Total_Profit", "Total_Loss", "Net_PnL"])
    df["Month"] = pd.to_datetime(df["Exit Time"]).dt.to_period("M").astype(str)
    summary = df.groupby("Month").agg(
        Total_Trades=("PnL per lot", "count"),
        Total_Profit=("PnL per lot", lambda x: x[x > 0].sum()),
        Total_Loss=("PnL per lot", lambda x: x[x < 0].sum()),
        Net_PnL=("PnL per lot", "sum")
    ).reset_index()
    return summary

def daily_pnl_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["Day", "Total_Trades", "Total_Profit", "Total_Loss", "Net_PnL"])
    df["Day"] = pd.to_datetime(df["Exit Time"]).dt.date
    summary = df.groupby("Day").agg(
        Total_Trades=("PnL per lot", "count"),
        Total_Profit=("PnL per lot", lambda x: x[x > 0].sum()),
        Total_Loss=("PnL per lot", lambda x: x[x < 0].sum()),
        Net_PnL=("PnL per lot", "sum")
    ).reset_index()
    return summary

def reasoning_panel(df):
    latest = df.iloc[-1]
    return {
        "Disparity": round(latest["Disparity"], 2),
        "EMA_short": round(latest["EMA_short"], 2),
        "EMA_long": round(latest["EMA_long"], 2),
        "Signal": latest["Signal"]
    }

