from pathlib import Path

import torch

from app.config import MODEL_PATH
from app.models.fusion_model import QuantFormerModel


class CrashPredictor:
    def __init__(self):
        if not Path(MODEL_PATH).exists():
            raise FileNotFoundError(
                "Model file not found. Run "
                "`python -m app.models.train` "
                "from the backend folder first."
            )

        self.model = QuantFormerModel()
        self.model.load_state_dict(
            torch.load(MODEL_PATH, map_location="cpu")
        )
        self.model.eval()

    @torch.no_grad()
    def predict(self, market_features, sentiment_score):
        market = torch.tensor(
            [market_features], dtype=torch.float32
        )
        sentiment = torch.tensor(
            [[sentiment_score]], dtype=torch.float32
        )

        probability = self.model(
            market, sentiment
        ).item()

        return float(probability)