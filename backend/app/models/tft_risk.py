
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_FILE = DATA_DIR / "market_history.csv"


def get_latest_market_price():
    """Return the latest observed market mid-price."""

    if not HISTORY_FILE.exists():
        raise FileNotFoundError(
            "Market history not found. Start the backend and producers."
        )

    df = pd.read_csv(HISTORY_FILE)

    if df.empty or "mid_price" not in df.columns:
        raise ValueError("Market history has no usable price data.")

    df["mid_price"] = pd.to_numeric(
        df["mid_price"], errors="coerce"
    )

    prices = df["mid_price"].dropna()

    if prices.empty:
        raise ValueError("No valid market prices were found.")

    return float(prices.iloc[-1])


def calculate_forecast_risk(current_price, forecast_result):
    """
    Calculate a simple heuristic risk score from TFT forecasts.

    This is a demonstration score, not a calibrated crash probability.
    """

    if current_price <= 0:
        raise ValueError("Current market price must be positive.")

    forecasts = forecast_result.get("forecasts", [])

    if not forecasts:
        raise ValueError("No TFT forecasts were returned.")

    medians = [float(item["median"]) for item in forecasts]
    lowers = [float(item["lower"]) for item in forecasts]
    uppers = [float(item["upper"]) for item in forecasts]

    if not all(
        pd.notna(value)
        for value in medians + lowers + uppers
    ):
        raise ValueError("Forecast contains invalid numeric values.")

    # Largest forecasted median decline from the current price.
    worst_decline_pct = max(
        0.0,
        (current_price - min(medians)) / current_price * 100,
    )

    # Average forecast interval width as a percentage of current price.
    average_interval_pct = (
        sum(upper - lower for lower, upper in zip(lowers, uppers))
        / len(forecasts)
        / current_price
        * 100
    )

    if average_interval_pct < 0:
        raise ValueError("Forecast interval bounds are invalid.")

    # Heuristic score: downside contributes up to 60 points;
    # forecast interval width contributes up to 40 points.
    downside_component = min(worst_decline_pct / 2.0 * 60, 60)
    uncertainty_component = min(average_interval_pct / 4.0 * 40, 40)

    risk_score = round(
        downside_component + uncertainty_component, 2
    )

    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "current_price": round(current_price, 6),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "forecast_steps": len(forecasts),
        "worst_forecast_decline_pct": round(worst_decline_pct, 4),
        "average_forecast_interval_pct": round(
            average_interval_pct, 4
        ),
        "interpretation": (
            "Heuristic risk score based on forecast downside and "
            "quantile interval width. It is not a crash probability "
            "or a validated financial risk measure."
        ),
    }
