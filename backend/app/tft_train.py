
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import lightning.pytorch as pl

from pytorch_forecasting import (
    TimeSeriesDataSet,
    TemporalFusionTransformer,
)
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint

CSV_PATH = "data/market_features.csv"
OUT_DIR = Path("artifacts")
OUT_DIR.mkdir(exist_ok=True)

ENCODER_LENGTH = 60
PREDICTION_LENGTH = 5
QUANTILES = [0.1, 0.5, 0.9]

pl.seed_everything(42, workers=True)

# ----- Load and validate data -----
df = pd.read_csv(CSV_PATH)
required = [
    "time_idx", "symbol", "close", "open", "high", "low",
    "volume", "sentiment_score", "bid_volume", "ask_volume"
]
missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

df = df[required].copy()
df["symbol"] = df["symbol"].astype(str)
df["time_idx"] = df["time_idx"].astype(int)
df = df.sort_values(["symbol", "time_idx"]).reset_index(drop=True)

numeric = [
    "close", "open", "high", "low", "volume",
    "sentiment_score", "bid_volume", "ask_volume"
]
df[numeric] = df[numeric].replace([np.inf, -np.inf], np.nan)
df[numeric] = df.groupby("symbol")[numeric].transform(
    lambda x: x.ffill()
)
df = df.dropna(subset=["close", "open", "high", "low"])
df["sentiment_score"] = df["sentiment_score"].fillna(0.0)
df["volume"] = df["volume"].fillna(0.0)
df["bid_volume"] = df["bid_volume"].fillna(0.0)
df["ask_volume"] = df["ask_volume"].fillna(0.0)

# Continuous time_idx should increase by one per candle.
# This simple example expects one contiguous series per symbol.
for symbol, part in df.groupby("symbol"):
    if part["time_idx"].duplicated().any():
        raise ValueError(f"Duplicate time_idx for {symbol}")
    if len(part) < ENCODER_LENGTH + PREDICTION_LENGTH + 20:
        raise ValueError(f"Not enough history for {symbol}")

# ----- Chronological train/validation split -----
cutoff = int(df["time_idx"].max() * 0.8)

training_frame = df[df.time_idx <= cutoff].copy()

training = TimeSeriesDataSet(
    training_frame,
    time_idx="time_idx",
    target="close",
    group_ids=["symbol"],
    min_encoder_length=ENCODER_LENGTH,
    max_encoder_length=ENCODER_LENGTH,
    min_prediction_length=PREDICTION_LENGTH,
    max_prediction_length=PREDICTION_LENGTH,
    static_categoricals=["symbol"],
    time_varying_known_reals=["time_idx"],
    time_varying_unknown_reals=[
        "close", "open", "high", "low", "volume",
        "sentiment_score", "bid_volume", "ask_volume",
    ],
    target_normalizer=GroupNormalizer(
        groups=["symbol"], transformation="softplus"
    ),
    add_relative_time_idx=True,
    add_target_scales=True,
    add_encoder_length=True,
)

validation = TimeSeriesDataSet.from_dataset(
    training,
    df,
    min_prediction_idx=cutoff + 1,
    stop_randomization=True,
)

train_loader = training.to_dataloader(
    train=True, batch_size=128, num_workers=0
)
val_loader = validation.to_dataloader(
    train=False, batch_size=128, num_workers=0
)

# ----- Train TFT -----
checkpoint = ModelCheckpoint(
    dirpath=str(OUT_DIR),
    filename="tft-{epoch:02d}-{val_loss:.4f}",
    monitor="val_loss",
    mode="min",
    save_top_k=1,
)
early_stop = EarlyStopping(
    monitor="val_loss", patience=5, mode="min"
)

tft = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=3e-3,
    hidden_size=32,
    attention_head_size=4,
    dropout=0.1,
    hidden_continuous_size=16,
    loss=QuantileLoss(quantiles=QUANTILES),
    optimizer="adam",
    reduce_on_plateau_patience=3,
    log_interval=10,
)

trainer = pl.Trainer(
    max_epochs=30,
    accelerator="auto",
    devices=1,
    gradient_clip_val=0.1,
    callbacks=[early_stop, checkpoint],
    logger=False,
    enable_model_summary=True,
)

trainer.fit(
    tft,
    train_dataloaders=train_loader,
    val_dataloaders=val_loader,
)

best_path = checkpoint.best_model_path
if best_path:
    tft = TemporalFusionTransformer.load_from_checkpoint(best_path)

# ----- Forecast the next five steps -----
# Build a dataset containing the most recent encoder window per symbol.
latest = df.groupby("symbol", group_keys=False).tail(
    ENCODER_LENGTH
).copy()

# Append five future rows. Future covariates must be known or forecast
# separately. For this demo, carry forward known/static values and
# initialize unknown market inputs; the TFT predicts close.
future_rows = []
for symbol, part in latest.groupby("symbol"):
    last = part.sort_values("time_idx").iloc[-1]
    for step in range(1, PREDICTION_LENGTH + 1):
        future_rows.append({
            "time_idx": int(last.time_idx) + step,
            "symbol": symbol,
            "close": float(last.close),
            "open": float(last.close),
            "high": float(last.close),
            "low": float(last.close),
            "volume": float(last.volume),
            "sentiment_score": float(last.sentiment_score),
            "bid_volume": float(last.bid_volume),
            "ask_volume": float(last.ask_volume),
        })

forecast_frame = pd.concat(
    [latest, pd.DataFrame(future_rows)],
    ignore_index=True,
).sort_values(["symbol", "time_idx"])

# Predict=True selects the final forecast window for each series.
predict_ds = TimeSeriesDataSet.from_dataset(
    training,
    forecast_frame,
    predict=True,
    stop_randomization=True,
)
predict_loader = predict_ds.to_dataloader(
    train=False, batch_size=128, num_workers=0
)

predictions = tft.predict(
    predict_loader,
    mode="quantiles",
    return_x=True,
)

quantile_tensor = predictions.output
if isinstance(quantile_tensor, dict):
    quantile_tensor = quantile_tensor["prediction"]

quantile_array = quantile_tensor.detach().cpu().numpy()
# Expected shape: [series, 5 horizons, 3 quantiles]
x = predictions.x
decoder_times = x["decoder_time_idx"].detach().cpu().numpy()
groups = x["groups"].detach().cpu().numpy()

results = []
for i in range(quantile_array.shape[0]):
    for h in range(quantile_array.shape[1]):
        q10, q50, q90 = map(float, quantile_array[i, h, :])
        results.append({
            "symbol_group": int(groups[i, 0]),
            "time_idx": int(decoder_times[i, h]),
            "horizon": h + 1,
            "lower": min(q10, q90),
            "median": q50,
            "upper": max(q10, q90),
        })

with open(OUT_DIR / "forecast.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved {len(results)} forecast points to artifacts/forecast.json")
