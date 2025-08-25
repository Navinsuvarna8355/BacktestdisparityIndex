import pandas as pd

def load_saved_option_chain(path):
    df = pd.read_csv(path, parse_dates=["Timestamp_IST"])
    df.sort_values("Timestamp_IST", inplace=True)
    return df

def simulate_disparity_trades(df, buy_thresh=102, sell_thresh=98):
    trades = []
    position = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        disparity = (row["PE_IV"] / row["CE_IV"]) * 100 if row["CE_IV"] else None
        if disparity is None:
            continue

        signal = None
        if disparity > buy_thresh:
            signal = "Buy PE"
            price = row["PE_IV"]
        elif disparity < sell_thresh:
            signal = "Sell PE"
            price = row["PE_IV"]
        elif disparity < (200 - buy_thresh):
            signal = "Buy CE"
            price = row["CE_IV"]
        elif disparity > (200 - sell_thresh):
            signal = "Sell CE"
            price = row["CE_IV"]

        if signal and not position:
            position = {
                "Type": signal,
                "Entry_Time": row["Timestamp_IST"],
                "Entry_Price": price
            }
        elif position and signal and signal.split()[0] != position["Type"].split()[0]:
            exit_price = price
            pnl = (exit_price - position["Entry_Price"]) if "Buy" in position["Type"] else (position["Entry_Price"] - exit_price)
            trades.append({
                "Type": position["Type"],
                "Entry": position["Entry_Time"],
                "Exit": row["Timestamp_IST"],
                "PnL": round(pnl, 2)
            })
            position = None

    return pd.DataFrame(trades)
