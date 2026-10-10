import torch
import torch.nn as nn


class QuantFormerModel(nn.Module):
    def __init__(self, market_features=5, hidden=32):
        super().__init__()

        self.market_layer = nn.Linear(
            market_features, hidden
        )
        self.news_layer = nn.Linear(1, hidden)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden,
            nhead=4,
            batch_first=True,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=2,
        )

        self.output_layer = nn.Linear(hidden, 1)

    def forward(self, market, sentiment):
        market_features = self.market_layer(market)
        news_features = self.news_layer(sentiment)

        combined = market_features + news_features
        combined = combined.unsqueeze(1)

        encoded = self.transformer(combined)
        prediction = self.output_layer(encoded[:, -1, :])

        return torch.sigmoid(prediction)