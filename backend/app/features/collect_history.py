
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_FILE = DATA_DIR / "market_history.csv"

COLUMNS = [
    "timestamp",
    "mid_price",
    "bid_volume",
    "ask_volume",
    "imbalance",
    "spread",
    "sentiment_score",
]


def save_market_event(event, sentiment_score=0.0):
    """Append one market observation to the history CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": event.get("timestamp"),
        "mid_price": event.get("mid_price"),
        "bid_volume": event.get("bid_volume"),
        "ask_volume": event.get("ask_volume"),
        "imbalance": event.get("imbalance"),
        "spread": event.get("spread"),
        "sentiment_score": sentiment_score,
    }

    file_exists = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0

    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


if __name__ == "__main__":
    print(f"Market history will be saved to: {HISTORY_FILE}")
