# defines the tft model and dataset
from pathlib import Path

import pandas as pd
import torch

from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "tft_dataset.csv"

# Model settings
MAX_ENCODER_LENGTH = 30
MAX_PREDICTION_LENGTH = 5

QUANTILES = [0.1, 0.5, 0.9]

FEATURE_COLUMNS = [
    "mid_price",
    "bid_volume",
    "ask_volume",
    "imbalance",
    "spread",
    "sentiment_score",
]


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} not found. Run "
            "`python -m app.features.prepare_dataset` first."
        )

    df = pd.read_csv(DATA_FILE)

    required = ["timestamp"] + FEATURE_COLUMNS
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True, errors="coerce"
    )

    df = df.dropna(subset=required)
    df = df.sort_values("timestamp")
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    df = df.reset_index(drop=True)

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)

    # TFT needs an ordered integer index for each observation.
    df["time_idx"] = range(len(df))

    # One continuous simulated market series.
    df["series_id"] = "market"

    if len(df) < MAX_ENCODER_LENGTH + MAX_PREDICTION_LENGTH + 10:
        raise ValueError(
            f"Only {len(df)} usable rows found. Collect more data "
            f"before setup; aim for at least "
            f"{MAX_ENCODER_LENGTH + MAX_PREDICTION_LENGTH + 10} rows."
        )

    return df


def build_datasets(df):
    # Chronological split: first 80% for training.
    split_idx = int(len(df) * 0.8)

    train_df = df.iloc[:split_idx].copy()

    # Include the earlier history so the validation forecast
    # can use past observations, then forecast the next five rows.
    validation_df = df.iloc[
        split_idx - MAX_PREDICTION_LENGTH:
    ].copy()

    training = TimeSeriesDataSet(
        train_df,
        time_idx="time_idx",
        target="mid_price",
        group_ids=["series_id"],
        min_encoder_length=MAX_ENCODER_LENGTH,
        max_encoder_length=MAX_ENCODER_LENGTH,
        min_prediction_length=MAX_PREDICTION_LENGTH,
        max_prediction_length=MAX_PREDICTION_LENGTH,
        static_categoricals=["series_id"],
        time_varying_known_reals=["time_idx"],
        time_varying_unknown_reals=FEATURE_COLUMNS,
        target_normalizer=GroupNormalizer(
            groups=["series_id"],
        ),
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True,
    )

    validation = TimeSeriesDataSet.from_dataset(
        training,
        validation_df,
        predict=True,
        stop_randomization=True,
    )
    
    train_loader = training.to_dataloader(
        train=True,
        batch_size=32,
        num_workers=0,
    )

    validation_loader = validation.to_dataloader(
        train=False,
        batch_size=32,
        num_workers=0,
    )

    return training, validation, train_loader, validation_loader
    # return training, validation
def build_model(training):
    model = TemporalFusionTransformer.from_dataset(
        training,
        learning_rate=0.001,
        hidden_size=16,
        attention_head_size=4,
        dropout=0.1,
        hidden_continuous_size=8,
        output_size=len(QUANTILES),
        loss=QuantileLoss(quantiles=QUANTILES),
        log_interval=-1,
        reduce_on_plateau_patience=3,
    )

    return model


def main():
    df = load_data()
    
    training, validation, train_loader, validation_loader = (
        build_datasets(df)
    )

    model = build_model(training)

    print("\nTFT setup successful!")
    print(f"Total usable observations: {len(df)}")
    print(f"Training observations: {int(len(df) * 0.8)}")
    print(f"Encoder length: {MAX_ENCODER_LENGTH}")
    print(f"Forecast horizon: {MAX_PREDICTION_LENGTH} steps")
    print(f"Quantiles: {QUANTILES}")
    print(f"Training batches: {len(train_loader)}")
    print(f"Validation batches: {len(validation_loader)}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    print("\nModel is configured, but not trained yet.")

if __name__ == "__main__":
    main()
