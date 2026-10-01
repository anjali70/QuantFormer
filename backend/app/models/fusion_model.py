import torch
import torch.nn as nn


class QuantFormerModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.market_layer = nn.Linear(5, 32)
        self.news_layer = nn.Linear(1, 32)

        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=32,
                nhead=4,
                batch_first=True
            ),
            num_layers=2
        )

        self.output_layer = nn.Linear(32, 1)

    def forward(self, market, sentiment):
        market_features = self.market_layer(market)
        news_features = self.news_layer(sentiment)

        combined = market_features + news_features

        combined = combined.unsqueeze(1)

        output = self.transformer(combined)

        prediction = self.output_layer(output[:, -1, :])

        return torch.sigmoid(prediction)