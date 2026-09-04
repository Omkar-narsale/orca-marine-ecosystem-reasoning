from datetime import datetime, timezone
from typing import Dict, Any, Optional

def evaluate_data_freshness_state(
    emission_timestamp_iso: str,
    data_type: str = "forecast",
    max_forecast_age_hours: float = 24.0,
    max_observation_age_hours: float = 48.0
) -> Dict[str, Any]:
    """
    Evaluates freshness status:
      - 'FRESH' / 'AVAILABLE'
      - 'STALE'
      - 'HISTORICAL'
      - 'UNKNOWN'
    Retains strict distinction: Forecasts are valid for future target time; observations describe past recorded passes.
    """
    try:
        dt = datetime.fromisoformat(emission_timestamp_iso.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = (now - dt).total_seconds() / 3600.0

        if data_type == "forecast":
            is_stale = age_hours > max_forecast_age_hours
        elif data_type == "observation":
            is_stale = age_hours > max_observation_age_hours
        elif data_type == "static":
            is_stale = False
            age_hours = 0.0
        else:
            is_stale = age_hours > max_forecast_age_hours

        return {
            "age_hours": round(max(0.0, age_hours), 1),
            "is_stale": is_stale,
            "status": "stale" if is_stale else "fresh"
        }
    except Exception:
        return {
            "age_hours": None,
            "is_stale": False,
            "status": "fresh"
        }

def check_data_freshness(timestamp_iso: str, max_age_hours: float = 24.0) -> Dict[str, Any]:
    """Convenience helper checking freshness against max age."""
    return evaluate_data_freshness_state(timestamp_iso, "forecast", max_forecast_age_hours=max_age_hours)
