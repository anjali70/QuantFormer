
import pandas as pd

from app.features import news_history


def test_save_and_load_news_event(tmp_path, monkeypatch):
    """Check that a news event is saved and loaded correctly."""
    monkeypatch.setattr(
        news_history,
        "DATA_DIR",
        tmp_path,
    )
    monkeypatch.setattr(
        news_history,
        "NEWS_FILE",
        tmp_path / "news_history.csv",
    )

    event = {
        "timestamp": "2026-10-20T10:04:00Z",
        "headline": "Example market news",
        "source": "Test Source",
    }

    news_history.save_news_event(
        event,
        sentiment_score=-0.7,
    )

    results = news_history.load_recent_news(limit=10)

    assert len(results) == 1
    assert results[0]["headline"] == "Example market news"
    assert results[0]["source"] == "Test Source"
    assert results[0]["sentiment_score"] == -0.7
    assert results[0]["sentiment_label"] == "Negative"


def test_empty_news_history(tmp_path, monkeypatch):
    """Check that missing news history returns an empty list."""
    monkeypatch.setattr(
        news_history,
        "NEWS_FILE",
        tmp_path / "missing_news.csv",
    )

    assert news_history.load_recent_news() == []


def test_invalid_timestamp_is_ignored(tmp_path, monkeypatch):
    """Check that invalid timestamps do not break news loading."""
    file_path = tmp_path / "news_history.csv"

    pd.DataFrame([{
        "timestamp": "not-a-date",
        "headline": "Invalid date example",
        "source": "Test",
        "sentiment_label": "Neutral",
        "sentiment_score": 0.0,
    }]).to_csv(file_path, index=False)

    monkeypatch.setattr(
        news_history,
        "NEWS_FILE",
        file_path,
    )

    assert news_history.load_recent_news() == []
