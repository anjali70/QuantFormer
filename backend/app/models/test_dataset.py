from dataset import create_dataloader


market_data = [
    [100.1, 100.3, 1000, 800, 0.11],
    [100.2, 100.4, 900, 700, 0.12],
    [100.3, 100.5, 1100, 900, 0.10],
    [100.4, 100.6, 1000, 850, 0.08],
]

sentiment_data = [
    [0.5],
    [0.7],
    [-0.2],
    [0.1],
]

labels = [0, 0, 1, 0]

loader = create_dataloader(
    market_data,
    sentiment_data,
    labels
)

for batch in loader:
    print("Market:", batch["market"])
    print("Sentiment:", batch["sentiment"])
    print("Label:", batch["label"])
    break