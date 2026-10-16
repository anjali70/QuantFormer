
from pathlib import Path
import pickle

import pandas as pd
import torch

from pytorch_forecasting import TimeSeriesDataSet
from pytorch_forecasting import TemporalFusionTransformer

from app.models.tft_setup import (
    DATA_DIR,
    DATA_FILE,
    FEATURE_COLUMNS,
    MAX_ENCODER_LENGTH,
    MAX_PREDICTION_LENGTH,
    QUANTILES,
)


MODEL_FILE = DATA_DIR / "tft_model.ckpt"
PARAMETERS_FILE = DATA_DIR / "tft_dataset_parameters.pkl"
HISTORY_FILE = DATA_DIR / "market_history.csv"


class TFTPredictor:
    def __init__(self):
        for file in (MODEL_FILE, PARAMETERS_FILE):
            if not file.exists():
                raise FileNotFoundError(
                    f"{file} not found. Complete Day 3 training first."
                )

        self.model = TemporalFusionTransformer.load_from_checkpoint(
            str(MODEL_FILE),
            map_location="cpu",
        )
        self.model.eval()

        with PARAMETERS_FILE.open("rb") as file:
            self.dataset_parameters = pickle.load(file)

    def predict(self):
        if not HISTORY_FILE.exists():
            raise FileNotFoundError(
                "Market history is missing. Start the backend and producers."
            )

        df = pd.read_csv(HISTORY_FILE)
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], utc=True, errors="coerce"
        )

        for column in FEATURE_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df = (
            df.dropna(subset=["timestamp"] + FEATURE_COLUMNS)
            .sort_values("timestamp")
            .drop_duplicates(subset=["timestamp"], keep="last")
            .reset_index(drop=True)
        )

        if len(df) < MAX_ENCODER_LENGTH:
            raise ValueError(
                f"Need at least {MAX_ENCODER_LENGTH} market observations."
            )

        # Use the most recent observed rows as the encoder history.
        recent = df.tail(MAX_ENCODER_LENGTH).copy()
        recent["time_idx"] = range(len(recent))
        recent["series_id"] = "market"

        last_row = recent.iloc[-1]
        future_rows = []

        # Add placeholder rows for the decoder horizon. Future market
        # values are unknown; the placeholders only provide the required
        # dataset structure and are not actual observations.
        for step in range(1, MAX_PREDICTION_LENGTH + 1):
            row = last_row.to_dict()
            row["time_idx"] = len(recent) - 1 + step
            row["timestamp"] = (
                last_row["timestamp"]
                + pd.Timedelta(seconds=step)
            )

            for column in FEATURE_COLUMNS:
                row[column] = last_row[column]

            row["series_id"] = "market"
            future_rows.append(row)

        inference_df = pd.concat(
            [recent, pd.DataFrame(future_rows)],
            ignore_index=True,
        )

        inference_dataset = TimeSeriesDataSet.from_parameters(
            self.dataset_parameters,
            inference_df,
            predict=True,
            stop_randomization=True,
        )

        loader = inference_dataset.to_dataloader(
            train=False,
            batch_size=1,
            num_workers=0,
        )

        with torch.no_grad():
            quantile_predictions = self.model.predict(
                loader,
                mode="quantiles",
            )

        values = quantile_predictions.detach().cpu().numpy()

        # Expected shape: batch, forecast step, quantile.
        if values.ndim != 3 or values.shape[1] < MAX_PREDICTION_LENGTH:
            raise RuntimeError(
                f"Unexpected TFT output shape: {values.shape}"
            )

        values = values[0, :MAX_PREDICTION_LENGTH, :]

        # Quantiles were configured in this order: 0.1, 0.5, 0.9.
        forecasts = []

        last_time = recent["timestamp"].iloc[-1]
        for index, quantiles in enumerate(values, start=1):
            lower, median, upper = map(float, quantiles)

            forecasts.append({
                "step": index,
                "timestamp": (
                    last_time + pd.Timedelta(milliseconds=100 * index)
                ).isoformat(),
                "lower": min(lower, upper),
                "median": median,
                "upper": max(lower, upper),
            })

        return {
            "forecast_steps": MAX_PREDICTION_LENGTH,
            "quantiles": QUANTILES,
            "forecasts": forecasts,
            "note": (
                "Forecasts are model estimates using simulated market data; "
                "the future timestamps are approximate."
            ),
        }
