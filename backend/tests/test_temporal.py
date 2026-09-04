import pytest
from datetime import datetime, timedelta
from backend.app.services.temporal.alignment import parse_temporal_window, is_forecast_valid_for_window
from backend.app.services.temporal.forecast_window import check_data_freshness

def test_parse_temporal_window_tomorrow_morning():
    window = parse_temporal_window("Which zones should be avoided tomorrow morning?")
    assert window["label"] == "tomorrow_morning"
    assert "05:00" in window["display_label"]
    assert "14:00" in window["display_label"]
    assert "IST" in window["display_label"]
    assert window["is_forecast"] is True

def test_parse_temporal_window_today():
    window = parse_temporal_window("Is zone c safe today?")
    assert window["label"] == "today"
    assert "IST" in window["display_label"]

def test_parse_temporal_window_default():
    window = parse_temporal_window("General marine conditions")
    assert window["label"] == "next_24h"

def test_data_freshness_check():
    now_iso = datetime.now().isoformat()
    old_iso = (datetime.now() - timedelta(hours=48)).isoformat()

    fresh_res = check_data_freshness(now_iso, max_age_hours=24)
    assert fresh_res["status"] == "fresh"
    assert fresh_res["is_stale"] is False

    stale_res = check_data_freshness(old_iso, max_age_hours=24)
    assert stale_res["status"] == "stale"
    assert stale_res["is_stale"] is True
