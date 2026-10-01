import torch
from fusion_model import QuantFormerModel


model = QuantFormerModel()

market = torch.randn(4, 5)
sentiment = torch.randn(4, 1)

prediction = model(market, sentiment)

print("Crash Probability:")
print(prediction)