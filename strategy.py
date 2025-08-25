import pandas as pd
from datetime import datetime
import pytz

def simulate_disparity_trades(df, buy_thresh=102, ce_thresh=98):
    trades, position = [], None
    for i in range(1, len(df)):
        row = df.iloc[i]
        disparity = (row["PE_IV"] / row["CE_IV"]) * 100 if row["CE_IV"] else None
        if disparity is None: continue

        signal = None
        if disparity > buy_thresh:
            signal = "Buy PE"
            entry_iv = row["PE_IV"]
        elif disparity < ce_thresh:
            signal = "Buy CE"
            entry_iv = row["CE_IV"]

        if signal and not position:
            position = {
                "Type": signal,
                "Entry": row["Timestamp_IST"],
                "Entry_IV": entry_iv,
                "Strike": row["Strike"]
            }
        elif position and signal and signal.split()[1] == position["Type"].split()[1]:
            exit_iv = row["PE_IV"] if position["Type"] == "Buy PE" else row["CE_IV"]
            pnl = exit_iv - position["Entry_IV"]
            trades.append({
                "Type": position["Type"],
                "Strike": position["Strike"],
                "Entry": position["Entry"],
                "Exit": row["Timestamp_IST"],
                "Entry_IV": position["Entry_IV"],
                "Exit_IV": exit_iv,
                "PnL": round(pnl, 2),
                "Date": datetime.strptime(row["Timestamp_IST"], "%Y-%m-%d %H:%M:%S").date()
            })
            position = None
    return pd.DataFrame(trades)

