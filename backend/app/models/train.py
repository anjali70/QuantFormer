import torch
from torch import nn
from torch.optim import Adam

from app.models.dataset import create_dataloader
from app.models.fusion_model import QuantFormerModel


def main():
    market_data = [
        [100.1, 1200, 800, 0.20, 0.02],
        [100.2, 1300, 700, 0.30, 0.02],
        [100.3, 1100, 900, 0.10, 0.03],
        [99.9, 700, 1400, -0.33, 0.04],
        [99.7, 650, 1500, -0.40, 0.05],
        [100.4, 1400, 700, 0.33, 0.02],
        [99.6, 600, 1600, -0.45, 0.05],
        [100.5, 1500, 700, 0.36, 0.02],
    ]

    sentiment_data = [
        [0.5], [0.7], [0.1], [-0.4],
        [-0.7], [0.6], [-0.8], [0.4],
    ]

    labels = [0, 0, 0, 1, 1, 0, 1, 0]

    loader = create_dataloader(
        market_data,
        sentiment_data,
        labels,
        batch_size=4,
    )

    model = QuantFormerModel()
    optimizer = Adam(model.parameters(), lr=0.001)
    loss_function = nn.BCELoss()

    for epoch in range(10):
        total_loss = 0.0

        for market, sentiment, label in loader:
            optimizer.zero_grad()

            prediction = model(
                market, sentiment
            ).squeeze(-1)

            loss = loss_function(prediction, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(
            f"Epoch {epoch + 1}/10 "
            f"- Loss: {total_loss:.4f}"
        )

    torch.save(
        model.state_dict(),
        "quantformer_model.pth",
    )

    print("Training completed.")
    print("Saved quantformer_model.pth")


if __name__ == "__main__":
    main()