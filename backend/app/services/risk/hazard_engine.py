from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.risk.thresholds import MARINE_THRESHOLDS

class MarineHazardEngine:
    """
    Deterministic Marine Hazard Detection Engine (Phase 6).
    Inspects available wave, wind, warning, and current records and computes parameter hazard levels.
    Enforces fail-safe safety: Missing data or failed warning checks trigger explicit INSUFFICIENT_DATA / UNKNOWN.
    """
    def evaluate_wave_hazard(self, wave_records: List[NormalizedMarineRecord]) -> Dict[str, Any]:
        if not wave_records:
            return {
                "parameter": "significant_wave_height",
                "severity": "UNKNOWN",
                "score_contribution": 0.0,
                "value": None,
                "unit": "m",
                "status": "MISSING_DATA",
                "description": "Wave forecast data unavailable for sector. Safe passage cannot be determined."
            }

        valid_wave_recs = [r for r in wave_records if isinstance(r.value, (int, float))]
        if not valid_wave_recs:
            return {
                "parameter": "significant_wave_height",
                "severity": "UNKNOWN",
                "score_contribution": 0.0,
                "value": None,
                "unit": "m",
                "status": "MISSING_DATA",
                "description": "No valid numerical wave height values found."
            }

        max_wave_rec = max(valid_wave_recs, key=lambda r: float(r.value))
        h_val = float(max_wave_rec.value)
        th = MARINE_THRESHOLDS["significant_wave_height"]["thresholds"]

        if h_val >= th["critical"]:
            severity = "CRITICAL"
            sub_score = 100.0
            desc = f"Critical rough sea state: Significant wave height {h_val}m exceeds 4.0m danger threshold."
        elif h_val >= th["high"]:
            severity = "HIGH"
            sub_score = 70.0 + (h_val - th["moderate"]) / (th["critical"] - th["moderate"]) * 25.0
            desc = f"Elevated wave hazard: Swell reaches {h_val}m exceeding 2.0m craft limit."
        elif h_val >= th["moderate"]:
            severity = "MODERATE"
            sub_score = 40.0 + (h_val - th["low"]) / (th["high"] - th["low"]) * 30.0
            desc = f"Moderate wave swell ({h_val}m): Requires caution for crafts under 12m."
        else:
            severity = "LOW"
            sub_score = max(5.0, (h_val / th["low"]) * 35.0)
            desc = f"Calm to slight sea state ({h_val}m): Within safe operational envelope."

        return {
            "parameter": "significant_wave_height",
            "severity": severity,
            "score_contribution": round(sub_score, 1),
            "value": h_val,
            "unit": "m",
            "status": "AVAILABLE",
            "description": desc,
            "source": max_wave_rec.source,
            "source_url": max_wave_rec.source_url,
            "valid_time": max_wave_rec.valid_time,
            "data_type": max_wave_rec.data_type
        }

    def evaluate_wind_hazard(self, wind_records: List[NormalizedMarineRecord]) -> Dict[str, Any]:
        if not wind_records:
            return {
                "parameter": "surface_wind_10m",
                "severity": "UNKNOWN",
                "score_contribution": 0.0,
                "value": None,
                "unit": "kt",
                "status": "MISSING_DATA",
                "description": "Wind forecast data unavailable for sector."
            }

        valid_wind_recs = [r for r in wind_records if isinstance(r.value, (int, float))]
        if not valid_wind_recs:
            return {
                "parameter": "surface_wind_10m",
                "severity": "UNKNOWN",
                "score_contribution": 0.0,
                "value": None,
                "unit": "kt",
                "status": "MISSING_DATA",
                "description": "No valid numerical wind telemetry found."
            }

        max_wind_rec = max(valid_wind_recs, key=lambda r: float(r.value))
        w_val = float(max_wind_rec.value)
        th = MARINE_THRESHOLDS["surface_wind_10m"]["thresholds"]

        if w_val >= th["critical"]:
            severity = "CRITICAL"
            sub_score = 100.0
            desc = f"Gale/squall winds ({w_val} kt): Severe capsize hazard for coastal boats."
        elif w_val >= th["high"]:
            severity = "HIGH"
            sub_score = 70.0 + (w_val - th["moderate"]) / (th["critical"] - th["moderate"]) * 25.0
            desc = f"Strong wind hazard ({w_val} kt): Surface chop and steerage difficulty."
        elif w_val >= th["moderate"]:
            severity = "MODERATE"
            sub_score = 40.0 + (w_val - th["low"]) / (th["high"] - th["low"]) * 30.0
            desc = f"Moderate breeze ({w_val} kt): Manageable operational conditions."
        else:
            severity = "LOW"
            sub_score = max(5.0, (w_val / th["low"]) * 35.0)
            desc = f"Gentle breeze ({w_val} kt): Favorable surface navigation conditions."

        return {
            "parameter": "surface_wind_10m",
            "severity": severity,
            "score_contribution": round(sub_score, 1),
            "value": w_val,
            "unit": "kt",
            "status": "AVAILABLE",
            "description": desc,
            "source": max_wind_rec.source,
            "source_url": max_wind_rec.source_url,
            "valid_time": max_wind_rec.valid_time,
            "data_type": max_wind_rec.data_type
        }

    def evaluate_warning_hazard(
        self,
        warning_records: List[NormalizedMarineRecord],
        is_warning_service_available: bool = True
    ) -> Dict[str, Any]:
        if not is_warning_service_available:
            return {
                "parameter": "marine_warning",
                "severity": "UNKNOWN",
                "score_contribution": 50.0,
                "value": "Warning Data Unavailable",
                "status": "INSUFFICIENT_DATA",
                "description": "Marine warning feed unavailable. Cannot certify zone is warning-free."
            }

        if not warning_records:
            return {
                "parameter": "marine_warning",
                "severity": "NONE",
                "score_contribution": 0.0,
                "value": "No Active Warning",
                "status": "AVAILABLE",
                "description": "No active IMD coastal storm or squall warnings in effect."
            }

        w_rec = warning_records[0]
        return {
            "parameter": "marine_warning",
            "severity": "HIGH",
            "score_contribution": 90.0,
            "value": str(w_rec.value),
            "status": "AVAILABLE",
            "description": f"Official Marine Warning: {w_rec.value}",
            "source": w_rec.source,
            "source_url": w_rec.source_url,
            "valid_time": w_rec.valid_time,
            "data_type": w_rec.data_type
        }

hazard_engine = MarineHazardEngine()
