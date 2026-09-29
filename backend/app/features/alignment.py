import pandas as pd


def align_market_and_news(market_data, news_data):
    market_df = pd.DataFrame(market_data)
    news_df = pd.DataFrame(news_data)

    market_df["timestamp"] = pd.to_datetime(market_df["timestamp"])
    news_df["timestamp"] = pd.to_datetime(news_df["timestamp"])

    market_df = market_df.sort_values("timestamp")
    news_df = news_df.sort_values("timestamp")

    aligned_data = pd.merge_asof(
        market_df,
        news_df,
        on="timestamp",
        direction="backward"
    )

    aligned_data["sentiment_score"] = (
        aligned_data["sentiment_score"].fillna(0)
    )

    return aligned_data