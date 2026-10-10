import pandas as pd


def align_market_and_news(market_data, news_data):
    market = pd.DataFrame(market_data)
    news = pd.DataFrame(news_data)

    if market.empty:
        return market

    market["timestamp"] = pd.to_datetime(
        market["timestamp"], utc=True
    )
    market = market.sort_values("timestamp")

    if news.empty:
        market["sentiment_score"] = 0.0
        market["embedding"] = None
        return market

    news["timestamp"] = pd.to_datetime(
        news["timestamp"], utc=True
    )
    news = news.sort_values("timestamp")

    aligned = pd.merge_asof(
        market,
        news[["timestamp", "sentiment_score", "embedding"]],
        on="timestamp",
        direction="backward",
    )

    aligned["sentiment_score"] = (
        aligned["sentiment_score"].fillna(0.0)
    )

    return aligned