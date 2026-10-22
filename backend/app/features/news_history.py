
import csv
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
NEWS_FILE = DATA_DIR / "news_history.csv"

COLUMNS = [
    "timestamp",
    "headline",
    "source",
    "sentiment_label",
    "sentiment_score",
]


def save_news_event(event, sentiment_score=None):
    """Save one processed news event to a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    headline = (
        event.get("headline")
        or event.get("title")
        or event.get("text")
        or "Headline unavailable"
    )

    timestamp = event.get("timestamp")

    if not timestamp:
        timestamp = pd.Timestamp.now(tz="UTC").isoformat()

    score = sentiment_score

    if score is None:
        score = event.get("sentiment_score", 0.0)

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    label = event.get("sentiment_label")

    if not label:
        if score < -0.05:
            label = "Negative"
        elif score > 0.05:
            label = "Positive"
        else:
            label = "Neutral"

    row = {
        "timestamp": str(timestamp),
        "headline": str(headline),
        "source": str(event.get("source", "Unknown")),
        "sentiment_label": str(label),
        "sentiment_score": score,
    }

    file_exists = (
        NEWS_FILE.exists()
        and NEWS_FILE.stat().st_size > 0
    )

    with NEWS_FILE.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=COLUMNS,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def load_recent_news(limit=10):
    """Return the latest stored news events."""
    if not NEWS_FILE.exists():
        return []

    df = pd.read_csv(NEWS_FILE)

    if df.empty:
        return []

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = None

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce",
    )

    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp", ascending=False)
    df = df.head(max(1, min(int(limit), 100)))

    results = []

    for _, row in df.iterrows():
        results.append({
            "timestamp": row["timestamp"].isoformat(),
            "headline": str(row["headline"]),
            "source": str(row["source"]),
            "sentiment_label": str(row["sentiment_label"]),
            "sentiment_score": float(
                row["sentiment_score"]
            ),
        })

    return results
