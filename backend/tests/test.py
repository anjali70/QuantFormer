
import numpy as np
import pandas as pd
import pytest

from app.models.tft_interpret import (
    get_result_parts,
    summarize_importance,
    extract_attention_steps,
)


def test_prediction_result_unpacking():
    """Check that predictions and inputs are extracted correctly."""
    predictions = {"output": "sample"}
    inputs = {"encoder_lengths": [5]}

    raw_output, x = get_result_parts(
        (predictions, inputs)
    )

    assert raw_output == predictions
    assert x == inputs


def test_prediction_result_rejects_invalid_data():
    """Check that unexpected prediction results raise an error."""
    with pytest.raises(RuntimeError):
        get_result_parts({"output": "sample"})


def test_feature_importance_returns_sorted_results():
    """Check that features are ranked by importance."""
    values = np.array([[0.2, 0.8, 0.4]])
    names = ["spread", "imbalance", "sentiment_score"]

    results = summarize_importance(values, names)

    assert len(results) == 3
    assert results[0]["feature"] == "imbalance"
    assert results[1]["feature"] == "sentiment_score"
    assert results[2]["feature"] == "spread"


def test_feature_importance_handles_missing_values():
    """Check that invalid importance scores are excluded."""
    values = np.array([0.5, np.nan, 0.2])
    names = ["bid_volume", "ask_volume", "spread"]

    results = summarize_importance(values, names)

    assert len(results) == 2
    assert all(
        np.isfinite(item["importance"])
        for item in results
    )


def test_empty_importance_returns_empty_list():
    assert summarize_importance(None, ["spread"]) == []


def test_attention_timestamp_mapping():
    """Check attention mapping when encoder indices are available."""
    df = pd.DataFrame({
        "time_idx": [0, 1, 2],
        "timestamp": pd.to_datetime([
            "2026-10-20T10:00:00Z",
            "2026-10-20T10:01:00Z",
            "2026-10-20T10:02:00Z",
        ], utc=True),
    })

    interpretation = {
        "attention": np.array([[0.1, 0.7, 0.2]])
    }

    inputs = {
        "encoder_time_idx": np.array([[0, 1, 2]])
    }

    results = extract_attention_steps(
        interpretation,
        inputs,
        df,
    )

    assert len(results) == 3
    assert results[0]["time_idx"] == 1
    assert results[0]["weight"] == pytest.approx(0.7)
    assert results[0]["timestamp"] is not None


def test_attention_without_encoder_indices():
    """Check the fallback for versions missing encoder_time_idx."""
    df = pd.DataFrame({
        "time_idx": [0, 1, 2],
        "timestamp": pd.to_datetime([
            "2026-10-20T10:00:00Z",
            "2026-10-20T10:01:00Z",
            "2026-10-20T10:02:00Z",
        ], utc=True),
    })

    interpretation = {
        "attention": np.array([[0.1, 0.8, 0.3]])
    }

    results = extract_attention_steps(
        interpretation,
        {},
        df,
    )

    assert len(results) == 3
    assert results[0]["weight"] == pytest.approx(0.8)
    assert results[0]["timestamp_alignment"] == "approximate"


def test_missing_attention_returns_empty_list():
    df = pd.DataFrame({
        "time_idx": [0],
        "timestamp": pd.to_datetime(
            ["2026-10-20T10:00:00Z"],
            utc=True,
        ),
    })

    results = extract_attention_steps(
        {},
        {},
        df,
    )

    assert results == []
