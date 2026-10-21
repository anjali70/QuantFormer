
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
    """Convert tensors and arrays to NumPy arrays."""
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().numpy()

    return np.asarray(value)


def get_result_parts(result):
    """Extract prediction output and input data from predict()."""
    if isinstance(result, (tuple, list)):
        if len(result) < 2:
            raise RuntimeError(
                "model.predict() did not return both predictions and inputs."
            )

        return result[0], result[1]

    raise RuntimeError(
        "Unexpected model.predict() result type: "
        f"{type(result).__name__}. "
        "Expected a tuple or list with predictions and inputs."
    )


def summarize_importance(values, names, top_n=6):
    """Summarize variable-selection importance."""
    if values is None:
        return []

    array = to_numpy(values)

    if array.size == 0:
        return []

    # Average batch and time dimensions, keeping the feature dimension.
    if array.ndim > 1:
        array = array.mean(
            axis=tuple(range(array.ndim - 1))
        )

    array = array.reshape(-1)
    count = min(len(array), len(names))
    results = []

    for index in range(count):
        score = float(array[index])

        if np.isfinite(score):
            results.append({
                "feature": str(names[index]),
                "importance": round(score, 6),
            })

    results.sort(
        key=lambda item: item["importance"],
        reverse=True,
    )

    return results[:top_n]


def extract_attention_steps(
    interpretation,
    inputs,
    df,
):
    """
    Extract attention scores and timestamps.

    Timestamp matching is attempted only when the returned
    encoder indices have a compatible length.
    """
    attention_steps = []
    attention_value = interpretation.get("attention")

    if attention_value is None:
        return attention_steps

    attention = to_numpy(attention_value)

    # Interpret attention along the last dimension as the sequence.
    if attention.ndim > 1:
        attention = attention.mean(
            axis=tuple(range(attention.ndim - 1))
        )

    attention = attention.reshape(-1)

    if attention.size == 0:
        return attention_steps

    encoder_indices = inputs.get("encoder_time_idx")

    # Some library versions omit encoder_time_idx.
    if encoder_indices is not None:
        encoder_indices = to_numpy(
            encoder_indices
        ).reshape(-1)

        usable = min(
            len(attention),
            len(encoder_indices),
        )

        if usable > 0:
            timestamp_lookup = (
                df.drop_duplicates("time_idx")
                .set_index("time_idx")["timestamp"]
                .to_dict()
            )

            selected_attention = attention[-usable:]
            selected_indices = encoder_indices[-usable:]

            for time_idx, weight in zip(
                selected_indices,
                selected_attention,
            ):
                timestamp = timestamp_lookup.get(
                    int(time_idx)
                )

                attention_steps.append({
                    "time_idx": int(time_idx),
                    "timestamp": (
                        timestamp.isoformat()
                        if timestamp is not None
                        else None
                    ),
                    "weight": round(float(weight), 6),
                })

    else:
        # Fallback: provide recent timestamps, clearly marked
        # as approximate rather than verified attention alignment.
        recent = df.tail(len(attention)).reset_index(drop=True)
        usable = min(len(attention), len(recent))

        for index in range(usable):
            attention_steps.append({
                "time_idx": None,
                "timestamp": recent.iloc[index][
                    "timestamp"
                ].isoformat(),
                "weight": round(
                    float(attention[-usable + index]),
                    6,
                ),
                "timestamp_alignment": "approximate",
            })

    attention_steps = [
        item for item in attention_steps
        if np.isfinite(item["weight"])
    ]

    attention_steps.sort(
        key=lambda item: item["weight"],
        reverse=True,
    )

    return attention_steps[:5]


def generate_interpretation():
    """Generate TFT attention and variable-importance results."""
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_FILE}. "
            "Run python -m app.models.tft_train first."
        )

    df = load_data()
    training, validation = build_datasets(df)

    loader = validation.to_dataloader(
        train=False,
        batch_size=1,
        num_workers=0,
    )

    if len(loader) == 0:
        raise ValueError(
            "The validation dataset has no batches. "
            "Check the dataset size and validation split."
        )

    model = TemporalFusionTransformer.load_from_checkpoint(
        str(MODEL_FILE),
        map_location="cpu",
    )
    model.eval()

    with torch.no_grad():
        result = model.predict(
            loader,
            mode="raw",
            return_x=True,
        )

    raw_output, inputs = get_result_parts(result)

    with torch.no_grad():
        interpretation = model.interpret_output(
            raw_output,
            reduction="sum",
        )

    encoder_importance = summarize_importance(
        interpretation.get("encoder_variables"),
        list(model.encoder_variables),
    )

    decoder_importance = summarize_importance(
        interpretation.get("decoder_variables"),
        list(model.decoder_variables),
    )

    static_importance = summarize_importance(
        interpretation.get("static_variables"),
        list(model.static_variables),
    )

    attention_steps = extract_attention_steps(
        interpretation,
        inputs,
        df,
    )

    return {
        "model": "Temporal Fusion Transformer",
        "attention_top_steps": attention_steps,
        "encoder_variable_importance": encoder_importance,
        "decoder_variable_importance": decoder_importance,
        "static_variable_importance": static_importance,
        "note": (
            "Attention weights and variable-selection importance "
            "describe model patterns, not causal effects. Timestamp "
            "alignment may be approximate when encoder indices are "
            "unavailable. Sentiment is a numeric feature; individual "
            "news headlines are not identified by this model."
        ),
    }


if __name__ == "__main__":
    import json

    try:
        result = generate_interpretation()
        print(json.dumps(result, indent=2, default=str))

    except Exception as exc:
        print(f"Interpretability failed: {exc}")
        raise
