import pytest
from datetime import datetime
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.risk.hazard_engine import hazard_engine
from backend.app.services.risk.risk_engine import risk_engine
from backend.app.services.risk.suitability import suitability_engine
from backend.app.services.risk.explanation import explanation_engine
from backend.app.services.risk.confidence import calculate_synthesis_confidence

def make_record(source, source_id, param, value, unit="", lat=19.3, lon=72.5, data_type="forecast", valid="Tomorrow 06:00 IST"):
    return NormalizedMarineRecord(
        source=source,
        source_id=source_id,
        parameter=param,
        value=value,
        unit=unit,
        latitude=lat,
        longitude=lon,
        timestamp=datetime.now().isoformat(),
        data_type=data_type,
        valid_time=valid,
        retrieved_at=datetime.now().isoformat(),
        quality="available",
        source_url="https://incois.gov.in"
    )

def test_case_1_high_risk_wave_wind_warning():
    """
    TEST CASE 1:
    Wave: High (4.1m)
    Wind: High (30kt)
    Warning: Active
    Geofence: Clear
    Expected: HIGH_RISK
    """
    records = [
        make_record("INCOIS", "INCOIS_OSF", "significant_wave_height", 4.1, "m"),
        make_record("IMD", "IMD_MARINE", "surface_wind_10m", 30.0, "kt"),
        make_record("IMD", "IMD_MARINE", "marine_fishermen_warning", "Squall alert active", data_type="warning")
    ]
    
    # Zone A coordinates (unrestricted area)
    zone_a_coords = [[19.18, 72.38], [19.42, 72.38], [19.42, 72.68], [19.18, 72.68]]
    result = risk_engine.evaluate_zone("zone-a", "North Offshore Sector", zone_a_coords, records)

    assert result["classification"] == "HIGH_RISK"
    assert result["risk_score"] >= 75
    assert result["wave_hazard"]["severity"] in ("HIGH", "CRITICAL")
    assert result["wind_hazard"]["severity"] == "HIGH"
    assert result["warning_hazard"]["severity"] == "HIGH"

def test_case_2_restricted_zone_override_not_safe():
    """
    TEST CASE 2:
    Wave: Low (0.8m)
    Wind: Low (8kt)
    Warning: None
    Geofence: Restricted
    Expected: RESTRICTED, NOT SAFE
    """
    records = [
        make_record("INCOIS", "INCOIS_OSF", "significant_wave_height", 0.8, "m"),
        make_record("IMD", "IMD_MARINE", "surface_wind_10m", 8.0, "kt")
    ]
    # Zone B coordinates intersect Mumbai Naval Anchorage
    zone_b_coords = [[18.86, 72.52], [19.08, 72.52], [19.08, 72.76], [18.86, 72.76]]
    result = risk_engine.evaluate_zone("zone-b", "Mumbai Harbor", zone_b_coords, records)

    assert result["classification"] == "RESTRICTED"
    assert result["is_restricted"] is True
    assert result["classification"] != "SUITABLE_CANDIDATE"
    assert result["classification"] != "SAFE"

def test_case_3_missing_data_reduced_confidence():
    """
    TEST CASE 3:
    Wave: Missing
    Wind: Available
    Warning: Unknown
    Expected: INSUFFICIENT_DATA or reduced confidence (NOT safe)
    """
    records = [
        make_record("IMD", "IMD_MARINE", "surface_wind_10m", 12.0, "kt")
    ]
    zone_a_coords = [[19.18, 72.38], [19.42, 72.38], [19.42, 72.68], [19.18, 72.68]]
    result = risk_engine.evaluate_zone("zone-test", "Test Sector", zone_a_coords, records)

    assert result["wave_hazard"]["status"] == "MISSING_DATA"
    assert result["wave_hazard"]["severity"] == "UNKNOWN"
    # Never classify as safe when wave data is missing
    assert result["classification"] != "SUITABLE_CANDIDATE"
    assert result["confidence"]["confidence_score"] < 75

def test_case_4_candidate_suitability_no_false_guarantee():
    """
    TEST CASE 4:
    Recent PFZ: Available
    Forecast weather: Favorable (0.9m wave, 10kt wind)
    Geofence: Clear
    Expected: SUITABLE_CANDIDATE, NOT 'Fish guaranteed'
    """
    records = [
        make_record("INCOIS", "INCOIS_OSF", "significant_wave_height", 0.9, "m"),
        make_record("IMD", "IMD_MARINE", "surface_wind_10m", 10.0, "kt"),
        make_record("INCOIS", "INCOIS_PFZ", "potential_fishing_zone", "PFZ line 18.5N 72.7E", data_type="advisory"),
        make_record("MOSDAC", "MOSDAC_OCM", "chlorophyll_a", 3.4, "mg/m³", data_type="observation")
    ]
    zone_c_coords = [[18.42, 72.55], [18.75, 72.55], [18.75, 72.86], [18.42, 72.86]]
    risk_result = risk_engine.evaluate_zone("zone-c", "South Coastal Offshore", zone_c_coords, records)
    suit_result = suitability_engine.evaluate_suitability(risk_result, records)

    assert risk_result["classification"] == "SUITABLE_CANDIDATE"
    assert "guaranteed" not in suit_result["summary"].lower()
    assert "not a guaranteed" in suit_result["scientific_disclaimer"].lower()
    assert "advisory" in suit_result["scientific_disclaimer"].lower()

def test_explanation_generation():
    records = [
        make_record("INCOIS", "INCOIS_OSF", "significant_wave_height", 4.1, "m"),
        make_record("IMD", "IMD_MARINE", "surface_wind_10m", 30.0, "kt")
    ]
    zone_a_coords = [[19.18, 72.38], [19.42, 72.38], [19.42, 72.68], [19.18, 72.68]]
    result = risk_engine.evaluate_zone("zone-a", "North Offshore Sector", zone_a_coords, records)
    reasons = explanation_engine.generate_zone_explanation(result)
    
    assert len(reasons) >= 2
    assert any("wave" in r.lower() for r in reasons)
    assert any("wind" in r.lower() for r in reasons)

def test_confidence_calculation_factors():
    wave_h = {"status": "AVAILABLE", "is_stale": False}
    wind_h = {"status": "AVAILABLE", "is_stale": False}
    warn_h = {"status": "AVAILABLE", "is_stale": False}
    geo_e = {"restricted": False}

    conf = calculate_synthesis_confidence(wave_h, wind_h, warn_h, geo_e)
    assert conf["confidence_score"] >= 80
    assert conf["confidence_level"] == "High"
    assert conf["is_stale"] is False
