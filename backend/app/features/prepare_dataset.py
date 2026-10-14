
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
INPUT_FILE = DATA_DIR / "market_history.csv"
OUTPUT_FILE = DATA_DIR / "tft_dataset.csv"

FEATURE_COLUMNS = [
    "mid_price",
    "bid_volume",
    "ask_volume",
    "imbalance",
    "spread",
    "sentiment_score",
]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} not found. Start the backend and Kafka producers first."
        )

    df = pd.read_csv(INPUT_FILE)

    if len(df) < 10:
        raise ValueError(
            f"Only {len(df)} rows found. Collect more market events first."
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True, errors="coerce"
    )

    df = df.dropna(subset=["timestamp", "mid_price"])
    df = df.sort_values("timestamp")
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    df = df.reset_index(drop=True)

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Predict the mid-price five observations into the future.
    df["target_price_5_steps"] = df["mid_price"].shift(-5)

    # The last five rows do not have known future targets.
    df = df.dropna(
        subset=FEATURE_COLUMNS + ["target_price_5_steps"]
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDay 1 dataset prepared successfully.")
    print(f"Rows available: {len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nDataset preview:")
    print(
        df[
            ["timestamp", "mid_price", "sentiment_score",
             "target_price_5_steps"]
        ].head()
    )


if __name__ == "__main__":
    main()
