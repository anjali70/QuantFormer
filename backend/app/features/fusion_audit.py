from app.features.alignment import align_market_and_news
from app.models.dataset import create_dataloader


def main():
    market = [
        {
            "timestamp": "2026-01-01T10:00:00Z",
            "mid_price": 100.0,
            "bid_volume": 1200,
            "ask_volume": 900,
            "imbalance": 0.14,
            "spread": 0.02,
        },
        {
            "timestamp": "2026-01-01T10:00:01Z",
            "mid_price": 100.1,
            "bid_volume": 1300,
            "ask_volume": 850,
            "imbalance": 0.21,
            "spread": 0.02,
        },
        {
            "timestamp": "2026-01-01T10:00:02Z",
            "mid_price": 99.8,
            "bid_volume": 800,
            "ask_volume": 1400,
            "imbalance": -0.27,
            "spread": 0.03,
        },
        {
            "timestamp": "2026-01-01T10:00:03Z",
            "mid_price": 99.7,
            "bid_volume": 750,
            "ask_volume": 1500,
            "imbalance": -0.33,
            "spread": 0.03,
        },
    ]

    news = [
        {
            "timestamp": "2026-01-01T09:59:59Z",
            "sentiment_score": 0.6,
            "embedding": [0.1] * 768,
        },
        {
            "timestamp": "2026-01-01T10:00:02Z",
            "sentiment_score": -0.7,
            "embedding": [-0.1] * 768,
        },
    ]

    aligned = align_market_and_news(market, news)

    market_features = aligned[
        ["mid_price", "bid_volume", "ask_volume", "imbalance", "spread"]
    ].values.tolist()

    sentiment_features = aligned[
        ["sentiment_score"]
    ].values.tolist()

    # Demo labels only; these are not real crash labels.
    labels = [0, 0, 1, 1]

    loader = create_dataloader(
        market_features,
        sentiment_features,
        labels,
        batch_size=2,
        shuffle=False,
    )

    batch = next(iter(loader))

    print("Aligned rows:", len(aligned))
    print("Batch tensor shapes:", [tuple(t.shape) for t in batch])
    print("Fusion audit passed on synthetic sample data.")


if __name__ == "__main__":
    main()