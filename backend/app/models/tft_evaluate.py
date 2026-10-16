
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from app.models.tft_setup import (
    DATA_DIR,
    load_data,
    build_datasets,
    build_model,
    MAX_PREDICTION_LENGTH,
)


def calculate_metrics(actual, predicted):
    """Calculate basic regression metrics."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    return float(mae), float(rmse)


def main():
    model_file = DATA_DIR / "tft_model.ckpt"

    if not model_file.exists():
        raise FileNotFoundError(
            f"Model not found: {model_file}\n"
            "Run python -m app.models.tft_train first."
        )

    # Load the historical dataset.
    df = load_data()

    # Build the same dataset configuration used during training.
    training, validation = build_datasets(df)

    validation_loader = validation.to_dataloader(
        train=False,
        batch_size=1,
        num_workers=0,
    )

    # Load the trained TFT model.
    model = build_model(training)

    checkpoint = torch.load(
        model_file,
        map_location="cpu",
        weights_only=False,
    )

    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    # Generate quantile predictions.
    with torch.no_grad():
        predictions = model.predict(
            validation_loader,
            mode="quantiles",
        )

    predictions = predictions.detach().cpu().numpy()

    # Collect the actual prices for the validation forecast.
    actual_values = []

    for batch in validation_loader:
        target = batch[1][0]
        actual_values.extend(
            target.detach().cpu().numpy().reshape(-1).tolist()
        )

    actual_values = np.asarray(actual_values, dtype=float)

    # TFT output contains lower, median, and upper quantiles.
    predicted_median = predictions[..., 1].reshape(-1)

    # Compare only the matching number of observations.
    count = min(len(actual_values), len(predicted_median))

    if count == 0:
        raise ValueError(
            "No validation predictions were generated. "
            "Collect more market data and retrain the model."
        )

    actual_values = actual_values[:count]
    predicted_median = predicted_median[:count]

    mae, rmse = calculate_metrics(
        actual_values,
        predicted_median,
    )

    # Save predictions so you can inspect them later.
    report = pd.DataFrame({
        "actual_price": actual_values,
        "predicted_median": predicted_median,
    })

    report["absolute_error"] = np.abs(
        report["actual_price"] - report["predicted_median"]
    )

    report_file = DATA_DIR / "tft_evaluation.csv"
    report.to_csv(report_file, index=False)

    print("\n========== TFT EVALUATION ==========")
    print(f"Validation samples compared: {count}")
    print(f"Forecast horizon configured: {MAX_PREDICTION_LENGTH} steps")
    print(f"MAE:  {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Report saved to: {report_file}")
    print("====================================")
    print("\nFirst five comparisons:")
    print(report.head().to_string(index=False))


if __name__ == "__main__":
    main()
