
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from pytorch_forecasting import TemporalFusionTransformer

from app.models.tft_setup import load_data, build_datasets

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CHECKPOINT = DATA_DIR / "tft_model.ckpt"


def to_numpy(value):
    """Convert a tensor or array-like value into a NumPy array."""
    if value is None:
        return np.array([])

    if isinstance(value, torch.Tensor):
        return value.detach().cpu().numpy()

    try:
        return np.asarray(value)
    except Exception:
        return np.array([])


def get_prediction_parts(result):
    """Handle common PyTorch Forecasting prediction return formats."""
    if isinstance(result, (tuple, list)):
        raw = result[0] if len(result) > 0 else None
        inputs = result[1] if len(result) > 1 else {}
    elif hasattr(result, "output"):
        raw = result.output
        inputs = getattr(result, "x", {})
    else:
        raw = result
        inputs = {}

    if not isinstance(inputs, dict):
        inputs = {}

    return raw, inputs


def summarize_importance(values, names, top_n=8):
    """Convert variable importance into a sorted list."""
    array = to_numpy(values)

    if array.size == 0:
        return []

    array = np.nan_to_num(array.astype(float), nan=0.0)
    array = np.abs(array)

    # Average all dimensions except the final feature dimension.
    if array.ndim > 1:
        array = array.mean(axis=tuple(range(array.ndim - 1)))

    array = array.reshape(-1)
    names = list(names or [])

    result = []
    for index, score in enumerate(array):
        name = (
            str(names[index])
            if index < len(names)
            else f"feature_{index}"
        )
        result.append({
            "feature": name,
            "importance": round(float(score), 6),
        })

    return sorted(
        result,
        key=lambda item: item["importance"],
        reverse=True,
    )[:top_n]


def extract_attention(attention, encoder_length=30):
    """Return normalized attention weights for recent encoder steps."""
    values = to_numpy(attention)

    if values.size == 0:
        return []

    values = np.nan_to_num(values.astype(float), nan=0.0)

    # Average batch/head dimensions while preserving the final time axis.
    if values.ndim > 1:
        values = values.mean(axis=tuple(range(values.ndim - 1)))

    values = values.reshape(-1)

    # Attention values are useful only if their shape is meaningful.
    values = np.maximum(values, 0)
    total = values.sum()

    if total > 0:
        values = values / total

    steps = []
    for index, weight in enumerate(values):
        steps.append({
            "step": index + 1,
            "relative_position": index - len(values) + 1,
            "attention": round(float(weight), 6),
        })

    return sorted(
        steps,
        key=lambda item: item["attention"],
        reverse=True,
    )[:min(10, len(steps))]


def generate_interpretation():
    """Load the trained model and summarize its interpretation."""
    if not CHECKPOINT.exists():
        raise FileNotFoundError(
            f"TFT checkpoint not found: {CHECKPOINT}"
        )

    df = load_data()

    # IMPORTANT: this expects build_datasets(df) to return:
    # train_dataset, validation_dataset, train_loader, validation_loader.
    datasets = build_datasets(df)

    if not isinstance(datasets, (tuple, list)) or len(datasets) < 4:
        raise RuntimeError(
            "Expected build_datasets(df) to return four items: "
            "train_dataset, validation_dataset, train_loader, "
            "validation_loader. Check tft_setup.py."
        )

    validation_loader = datasets[3]

    model = TemporalFusionTransformer.load_from_checkpoint(
        str(CHECKPOINT),
        map_location="cpu",
    )
    model.eval()

    with torch.no_grad():
        prediction_result = model.predict(
            validation_loader,
            mode="raw",
            return_x=True,
        )

    raw_output, inputs = get_prediction_parts(prediction_result)

    if raw_output is None:
        raise RuntimeError(
            "TFT prediction did not return raw output."
        )

    interpretation = model.interpret_output(
        raw_output,
        reduction="sum",
    )

    if not isinstance(interpretation, dict):
        raise RuntimeError(
            "Unexpected interpretation output. "
            "Check your PyTorch Forecasting version."
        )

    attention_steps = extract_attention(
        interpretation.get("attention")
    )

    encoder_variables = summarize_importance(
        interpretation.get("encoder_variables"),
        getattr(model, "encoder_variables", []),
    )
    decoder_variables = summarize_importance(
        interpretation.get("decoder_variables"),
        getattr(model, "decoder_variables", []),
    )
    static_variables = summarize_importance(
        interpretation.get("static_variables"),
        getattr(model, "static_variables", []),
    )

    return {
        "model": "Temporal Fusion Transformer",
        "attention_top_steps": attention_steps,
        "encoder_variable_importance": encoder_variables,
        "decoder_variable_importance": decoder_variables,
        "static_variable_importance": static_variables,
        "note": (
            "Attention and feature importance describe model patterns, "
            "not proof of causation. Attention positions are relative "
            "historical steps unless explicitly aligned to real timestamps. "
            "This model uses numeric sentiment and does not identify "
            "individual news headlines as causes."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(generate_interpretation(), indent=2))
