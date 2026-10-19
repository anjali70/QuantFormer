
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from pytorch_forecasting import TemporalFusionTransformer

from app.models.tft_setup import (
    DATA_DIR,
    load_data,
    build_datasets,
)

MODEL_FILE = DATA_DIR / "tft_model.ckpt"


def to_numpy(value):
    """Convert a tensor or array to a NumPy array."""
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().numpy()

    return np.asarray(value)


def summarize_weights(values, names, top_n=5):
    """Convert variable importance weights into a ranked list."""
    values = to_numpy(values)

    if values.size == 0:
        return []

    # Average all dimensions except the final feature dimension.
    if values.ndim > 1:
        values = values.mean(
            axis=tuple(range(values.ndim - 1))
        )

    values = values.reshape(-1)
    count = min(len(values), len(names))

    results = [
        {
            "feature": str(names[index]),
            "weight": round(float(values[index]), 6),
        }
        for index in range(count)
        if np.isfinite(values[index])
    ]

    results.sort(key=lambda item: item["weight"], reverse=True)
    return results[:top_n]


def generate_interpretation():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Trained TFT model not found. Run "
            "python -m app.models.tft_train first."
        )

    # Use the same dataset configuration as training.
    df = load_data()
    training, validation = build_datasets(df)

    loader = validation.to_dataloader(
        train=False,
        batch_size=1,
        num_workers=0,
    )

    model = TemporalFusionTransformer.load_from_checkpoint(
        str(MODEL_FILE),
        map_location="cpu",
    )
    model.eval()

    # Obtain raw TFT outputs and the corresponding input batch.
    with torch.no_grad():
        raw_output, x = model.predict(
            loader,
            mode="raw",
            return_x=True,
        )

    # Convert raw model output into TFT interpretation values.
    with torch.no_grad():
        interpretation = model.interpret_output(
            raw_output,
            reduction="sum",
        )

    attention = to_numpy(interpretation["attention"])

    # Average over batch/decoder dimensions, leaving encoder positions.
    if attention.ndim > 1:
        attention = attention.mean(
            axis=tuple(range(attention.ndim - 1))
        )

    attention = attention.reshape(-1)

    encoder_names = list(model.encoder_variables)
    decoder_names = list(model.decoder_variables)
    static_names = list(model.static_variables)

    encoder_importance = summarize_weights(
        interpretation["encoder_variables"],
        encoder_names,
    )

    decoder_importance = summarize_weights(
        interpretation["decoder_variables"],
        decoder_names,
    )

    static_importance = summarize_weights(
        interpretation["static_variables"],
        static_names,
    )

    # Match attention positions to the encoder input time indices.
    encoder_indices = to_numpy(x["encoder_time_idx"])
    encoder_indices = encoder_indices.reshape(-1)

    usable = min(len(attention), len(encoder_indices))
    attention = attention[-usable:]
    encoder_indices = encoder_indices[-usable:]

    timestamp_lookup = (
        df.drop_duplicates("time_idx")
        .set_index("time_idx")["timestamp"]
        .to_dict()
    )

    attention_steps = []

    for time_idx, weight in zip(encoder_indices, attention):
        timestamp = timestamp_lookup.get(int(time_idx))

        attention_steps.append({
            "time_idx": int(time_idx),
            "timestamp": (
                timestamp.isoformat()
                if timestamp is not None
                else None
            ),
            "weight": round(float(weight), 6),
        })

    attention_steps.sort(
        key=lambda item: item["weight"],
        reverse=True,
    )

    return {
        "model": "Temporal Fusion Transformer",
        "explanation_type": (
            "Attention and variable-selection importance"
        ),
        "attention_top_steps": attention_steps[:5],
        "encoder_variable_importance": encoder_importance,
        "decoder_variable_importance": decoder_importance,
        "static_variable_importance": static_importance,
        "note": (
            "These values describe model attention and variable "
            "selection, not causal effects. They do not identify "
            "a specific news headline as the cause of a prediction."
        ),
    }


if __name__ == "__main__":
    result = generate_interpretation()

    import json
    print(json.dumps(result, indent=2, default=str))
