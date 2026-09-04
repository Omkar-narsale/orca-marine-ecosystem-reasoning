from typing import Dict, Any, List

def calculate_synthesis_confidence(
    wave_hazard: Dict[str, Any],
    wind_hazard: Dict[str, Any],
    warning_hazard: Dict[str, Any],
    geofence_eval: Dict[str, Any],
    has_observation: bool = True
) -> Dict[str, Any]:
    """
    Transparent confidence calculation engine based on:
      1. Data completeness (40 points)
      2. Data freshness (25 points)
      3. Cross-source agreement (25 points)
      4. Geospatial verification (10 points)
    """
    score = 0.0
    factors = []
    is_stale = wave_hazard.get("is_stale", False) or wind_hazard.get("is_stale", False)

    # 1. Data Completeness (up to 40)
    completeness_pts = 0.0
    if wave_hazard.get("status") == "AVAILABLE":
        completeness_pts += 15.0
    else:
        factors.append("Wave forecast data missing (-15 pts)")

    if wind_hazard.get("status") == "AVAILABLE":
        completeness_pts += 15.0
    else:
        factors.append("Wind forecast data missing (-15 pts)")

    if warning_hazard.get("status") == "AVAILABLE":
        completeness_pts += 10.0

    score += completeness_pts

    # 2. Data Freshness (up to 25)
    if is_stale:
        freshness_pts = 10.0
        factors.append("Telemetry latency exceeds 24h baseline (-15 pts)")
    else:
        freshness_pts = 25.0
        factors.append("Telemetry retrieved within active 24h forecast cycle (+25 pts)")
    score += freshness_pts

    # 3. Cross-Source Consistency & Agreement (up to 25)
    wave_sev = wave_hazard.get("severity", "UNKNOWN")
    wind_sev = wind_hazard.get("severity", "UNKNOWN")

    if wave_sev in ("HIGH", "CRITICAL") and wind_sev in ("HIGH", "CRITICAL"):
        agreement_pts = 25.0
        factors.append("High source convergence between INCOIS wave model and IMD squall vectors (+25 pts)")
    elif wave_sev in ("LOW", "NONE") and wind_sev in ("LOW", "NONE"):
        agreement_pts = 25.0
        factors.append("High source convergence on calm maritime window (+25 pts)")
    elif wave_sev == "UNKNOWN" or wind_sev == "UNKNOWN":
        agreement_pts = 10.0
        factors.append("Partial source availability (-15 pts)")
    else:
        agreement_pts = 18.0
        factors.append("Moderate parameter variation across ocean and atmospheric models")

    score += agreement_pts

    # 4. Geospatial Verification (up to 10)
    if geofence_eval.get("status") != "UNKNOWN":
        score += 10.0
        factors.append("Geospatial cadastral boundary verified (+10 pts)")
    else:
        factors.append("Geofence cadastre baseline unverified (-10 pts)")

    final_score = round(min(100.0, max(10.0, score)), 0)

    if final_score >= 85.0:
        level = "High"
    elif final_score >= 65.0:
        level = "Medium"
    else:
        level = "Low"

    return {
        "confidence_score": int(final_score),
        "confidence_level": level,
        "confidence_percentage": f"{int(final_score)}%",
        "is_stale": is_stale,
        "explanation": f"Confidence is {level.lower()} ({int(final_score)}%) based on numerical forecast freshness, cross-source agreement, and cadastral baseline verification.",
        "factors": factors
    }
