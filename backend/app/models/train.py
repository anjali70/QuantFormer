import torch
import torch.nn as nn
import torch.optim as optim

from fusion_model import QuantFormerModel
from dataset import create_dataloader


# Sample training data
market_data = [
    [100.1, 100.3, 1000, 800, 0.11],
    [100.2, 100.4, 900, 700, 0.12],
    [100.3, 100.5, 1100, 900, 0.10],
    [100.4, 100.6, 1000, 850, 0.08],
    [100.5, 100.7, 1200, 800, 0.13],
    [100.6, 100.8, 1300, 750, 0.15],
    [100.7, 100.9, 1400, 700, 0.16],
    [100.8, 101.0, 1500, 650, 0.18],
]

sentiment_data = [
    [0.5],
    [0.7],
    [-0.2],
    [0.1],
    [-0.6],
    [-0.4],
    [0.3],
    [-0.5],
]

labels = [0, 0, 1, 0, 1, 1, 0, 1]


loader = create_dataloader(
    market_data,
    sentiment_data,
    labels,
    batch_size=4
)


model = QuantFormerModel()

criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


epochs = 10

for epoch in range(epochs):

    total_loss = 0

    for market, sentiment, label in loader:

        optimizer.zero_grad()

        prediction = model(
            market,
            sentiment
        ).squeeze()

        loss = criterion(
            prediction,
            label
        )

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(
        f"Epoch {epoch + 1}/{epochs} "
        f"- Loss: {total_loss:.4f}"
    )


torch.save(
    model.state_dict(),
    "quantformer_model.pth"
)

print("Model training completed.")
print("Model saved as quantformer_model.pth")