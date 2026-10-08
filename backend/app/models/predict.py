import torch

from fusion_model import QuantFormerModel


class CrashPredictor:

    def __init__(self):
        self.model = QuantFormerModel()

        self.model.load_state_dict(
            torch.load(
                "quantformer_model.pth",
                map_location="cpu"
            )
        )

        self.model.eval()

    def predict(self, market_data, sentiment_score):

        market = torch.tensor(
            [market_data],
            dtype=torch.float32
        )

        sentiment = torch.tensor(
            [[sentiment_score]],
            dtype=torch.float32
        )

        with torch.no_grad():

            probability = self.model(
                market,
                sentiment
            ).item()

        return probability