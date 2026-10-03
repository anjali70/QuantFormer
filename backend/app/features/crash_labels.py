import pandas as pd


def create_crash_labels(data, drop_threshold=0.02):
    df = pd.DataFrame(data)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    df["future_price"] = df["mid_price"].shift(-5)

    df["crash_label"] = (
        df["future_price"] < df["mid_price"] * (1 - drop_threshold)
    ).astype(int)

    return df