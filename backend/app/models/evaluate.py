import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from fusion_model import QuantFormerModel


# Test data
market_data = torch.tensor([
    [100.1, 100.3, 1000, 800, 0.11],
    [100.2, 100.4, 900, 700, 0.12],
    [100.3, 100.5, 1100, 900, 0.10],
    [100.4, 100.6, 1000, 850, 0.08],
    [100.5, 100.7, 1200, 800, 0.13],
    [100.6, 100.8, 1300, 750, 0.15],
    [100.7, 100.9, 1400, 700, 0.16],
    [100.8, 101.0, 1500, 650, 0.18]
], dtype=torch.float32)

sentiment_data = torch.tensor([
    [0.5],
    [0.7],
    [-0.2],
    [0.1],
    [-0.6],
    [-0.4],
    [0.3],
    [-0.5]
], dtype=torch.float32)

actual_labels = [0, 0, 1, 0, 1, 1, 0, 1]


# Load trained model
model = QuantFormerModel()
model.load_state_dict(
    torch.load(
        "quantformer_model.pth",
        map_location="cpu"
    )
)

model.eval()


# Make predictions
with torch.no_grad():
    probabilities = model(
        market_data,
        sentiment_data
    ).squeeze()

predicted_labels = (
    probabilities >= 0.5
).int().tolist()


# Calculate metrics
accuracy = accuracy_score(
    actual_labels,
    predicted_labels
)

precision = precision_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

recall = recall_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

f1 = f1_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

matrix = confusion_matrix(
    actual_labels,
    predicted_labels
)


print("QuantFormer Model Evaluation")
print("----------------------------")
print("Accuracy :", round(accuracy, 3))
print("Precision:", round(precision, 3))
print("Recall   :", round(recall, 3))
print("F1 Score :", round(f1, 3))
print("\nConfusion Matrix:")
print(matrix)