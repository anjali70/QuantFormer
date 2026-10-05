from dataset import create_dataloader


market_data = [
    [100.1, 100.3, 1000, 800, 0.11],
    [100.2, 100.4, 900, 700, 0.12],
    [100.3, 100.5, 1100, 900, 0.10],
    [100.4, 100.6, 1000, 850, 0.08],
    [100.5, 100.7, 1200, 800, 0.13],
    [100.6, 100.8, 1300, 750, 0.15],
]

sentiment_data = [
    [0.5],
    [0.7],
    [-0.2],
    [0.1],
    [-0.6],
    [-0.4],
]

# 1 = crash, 0 = no crash
labels = [0, 0, 1, 0, 1, 1]


loader = create_dataloader(
    market_data,
    sentiment_data,
    labels
)


for market, sentiment, label in loader:
    print("Market shape:", market.shape)
    print("Sentiment shape:", sentiment.shape)
    print("Labels:", label)
    break