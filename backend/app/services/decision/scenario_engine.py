import copy
from typing import Dict, Any, List, Optional
from backend.app.services.decision.suitability_engine import suitability_engine
from backend.app.services.decision.ranking_engine import ranking_engine

class WhatIfScenarioEngine:
    """
    Hypothetical What-If Scenario Engine for ORCA Phase 5.
    Applies controlled parameter modifications (wave delta, wind delta, time shift, geofence override)
    to a cloned baseline analysis and computes deterministic delta changes in risk and suitability.
    Strictly marks all output as 'SIMULATED SCENARIO' to prevent confusion with actual forecasts.
    """
    def run_scenario(
        self,
        baseline_zones: List[Dict[str, Any]],
        wave_delta_m: float = 0.0,
        wind_delta_kt: float = 0.0,
        target_zone_id: Optional[str] = "zone-c",
        geofence_override_zone_id: Optional[str] = None,
        scenario_time_label: Optional[str] = None
    ) -> Dict[str, Any]:
        # Deepcopy to ensure baseline telemetry remains pristine
        simulated_zones = copy.deepcopy(baseline_zones)

        scenario_description_parts = []
        if wave_delta_m != 0.0:
            scenario_description_parts.append(f"Wave Height {'+' if wave_delta_m > 0 else ''}{wave_delta_m} m")
        if wind_delta_kt != 0.0:
            scenario_description_parts.append(f"Wind Speed {'+' if wind_delta_kt > 0 else ''}{wind_delta_kt} kt")
        if geofence_override_zone_id:
            scenario_description_parts.append(f"Geofence Restriction applied to {geofence_override_zone_id.upper()}")
        if scenario_time_label:
            scenario_description_parts.append(f"Temporal Shift to {scenario_time_label}")

        scenario_title = " · ".join(scenario_description_parts) if scenario_description_parts else "Nominal Simulated Envelope"

        # Apply hypothetical modifications
        for z in simulated_zones:
            zid = z.get("id") or z.get("zone_id")
            
            # If target_zone_id is specified or applying globally
            if not target_zone_id or zid == target_zone_id or target_zone_id == "all":
                cur_wave = 1.2
                cur_wind = 12.0
                # Modify wave
                if "wave_hazard" in z and "value" in z["wave_hazard"]:
                    orig_wave = z["wave_hazard"]["value"]
                    if isinstance(orig_wave, (int, float)):
                        cur_wave = max(0.2, orig_wave + wave_delta_m)
                        z["wave_hazard"]["value"] = round(cur_wave, 2)
                        z["conditions"]["waveHeight"] = f"{round(cur_wave, 2)} m"

                # Modify wind
                if "wind_hazard" in z and "value" in z["wind_hazard"]:
                    orig_wind = z["wind_hazard"]["value"]
                    if isinstance(orig_wind, (int, float)):
                        cur_wind = max(0.0, orig_wind + wind_delta_kt)
                        z["wind_hazard"]["value"] = round(cur_wind, 1)
                        z["conditions"]["windSpeed"] = f"{round(cur_wind, 1)} kt"

                # Deterministically recalculate risk score for simulated sea state
                wave_risk = min(100.0, max(0.0, (cur_wave / 4.0) * 100.0))
                wind_risk = min(100.0, max(0.0, (cur_wind / 35.0) * 100.0))
                calc_risk = (0.50 * wave_risk) + (0.40 * wind_risk) + (10.0 if z.get("conditions", {}).get("marineWarning") else 0.0)
                z["risk_score"] = float(round(min(100.0, max(12.0, calc_risk)), 1))

            if geofence_override_zone_id and zid == geofence_override_zone_id:
                if "geofence" in z:
                    z["geofence"]["restricted"] = True
                    z["geofence"]["intersections"] = [{"name": "Hypothetical Regulatory Geofence Buffer"}]
                z["conditions"]["isRestricted"] = True
                z["conditions"]["geofenceStatus"] = "Hypothetical Security Restriction"
                z["risk_score"] = 75.0

        # Rerun ranking engine on baseline vs scenario
        baseline_ranking = ranking_engine.rank_zones(baseline_zones)
        scenario_ranking = ranking_engine.rank_zones(simulated_zones)

        # Compute delta for primary focus zone
        focus_id = target_zone_id if target_zone_id and target_zone_id != "all" else "zone-c"
        
        all_base = baseline_ranking["ranked_candidates"] + baseline_ranking["excluded_zones"]
        all_scen = scenario_ranking["ranked_candidates"] + scenario_ranking["excluded_zones"]
        
        base_target = next((z for z in all_base if getattr(z, "zone_id", z.get("id") if isinstance(z, dict) else "") == focus_id), None)
        scen_target = next((z for z in all_scen if getattr(z, "zone_id", z.get("id") if isinstance(z, dict) else "") == focus_id), None)

        base_risk = getattr(base_target, "risk_score", 22.0) if base_target else 22.0
        scen_risk = getattr(scen_target, "risk_score", base_risk) if scen_target else base_risk
        base_suit = getattr(base_target, "suitability_score", 72.0) if base_target else 72.0
        scen_suit = getattr(scen_target, "suitability_score", base_suit) if scen_target else base_suit

        risk_delta = round(scen_risk - base_risk, 1)
        suit_delta = round(scen_suit - base_suit, 1)

        # Generate grounded explanation
        is_scen_excluded = getattr(scen_target, "operational_status", "") == "EXCLUDED" if scen_target else False
        if scen_risk >= 75 or is_scen_excluded:
            explanation = (
                f"Under this simulated scenario ({scenario_title}), {focus_id.upper()} exceeds the craft safety threshold "
                f"(Risk increases from {base_risk} to {scen_risk}) and is EXCLUDED from operational candidates."
            )
        elif risk_delta > 0:
            explanation = (
                f"Under this simulated scenario ({scenario_title}), {focus_id.upper()} operational risk increases "
                f"by +{risk_delta} points (from {base_risk} to {scen_risk}), reducing candidate suitability to {scen_suit}/100."
            )
        elif risk_delta < 0:
            explanation = (
                f"Under this simulated scenario ({scenario_title}), {focus_id.upper()} conditions improve, "
                f"reducing risk by {risk_delta} points to {scen_risk}/100."
            )
        else:
            explanation = f"Simulated modifications produce no significant change in {focus_id.upper()} risk classification."

        return {
            "scenario_label": "SIMULATED SCENARIO (HYPOTHETICAL WHAT-IF)",
            "scenario_title": scenario_title,
            "target_zone_id": focus_id,
            "baseline_comparison": {
                "zone_code": getattr(base_target, "code", focus_id.upper()) if base_target else focus_id.upper(),
                "baseline_risk": base_risk,
                "simulated_risk": scen_risk,
                "risk_delta": f"{'+' if risk_delta > 0 else ''}{risk_delta}",
                "baseline_suitability": base_suit,
                "simulated_suitability": scen_suit,
                "suitability_delta": f"{'+' if suit_delta > 0 else ''}{suit_delta}",
                "baseline_status": getattr(base_target, "operational_status", "CANDIDATE") if base_target else "CANDIDATE",
                "simulated_status": getattr(scen_target, "operational_status", "CANDIDATE") if scen_target else "CANDIDATE"
            },
            "explanation": explanation,
            "ranked_candidates": scenario_ranking["ranked_candidates"],
            "excluded_zones": scenario_ranking["excluded_zones"],
            "top_candidate": scenario_ranking["top_candidate"],
            "alternative_candidate": scenario_ranking["alternative_candidate"],
            "simulated_zones": simulated_zones,
            "is_simulation": True,
            "scientific_disclaimer": "Simulated scenario output is purely mathematical sensitivity modeling. It does not replace authoritative forecasts."
        }

scenario_engine = WhatIfScenarioEngine()


from pydantic import BaseModel, Field

class ScenarioRunRequest(BaseModel):
    wave_delta_m: float = Field(default=0.0, description="Hypothetical wave height delta in meters e.g. +1.0")
    wind_delta_kt: float = Field(default=0.0, description="Hypothetical wind speed delta in knots e.g. +5.0")
    target_zone_id: Optional[str] = Field(default="zone-c", description="Specific zone ID to simulate or 'all'")
    geofence_override_zone_id: Optional[str] = Field(default=None, description="Zone to simulate restriction on")
    scenario_time_label: Optional[str] = Field(default=None, description="e.g. 'Tomorrow 18:00 IST'")


class BaselineComparison(BaseModel):
    zone_code: str
    baseline_risk: float
    simulated_risk: float
    risk_delta: str
    baseline_suitability: float
    simulated_suitability: float
    suitability_delta: str
    baseline_status: str
    simulated_status: str


class WhatIfScenarioResult(BaseModel):
    scenario_label: str = "SIMULATED SCENARIO"
    scenario_title: str
    target_zone_id: str
    baseline_comparison: BaselineComparison
    explanation: str
    ranked_candidates: List[Any] = Field(default_factory=list)
    excluded_zones: List[Any] = Field(default_factory=list)
    top_candidate: Optional[Any] = None
    alternative_candidate: Optional[Any] = None
    is_simulation: bool = True
    scientific_disclaimer: str


DEFAULT_BASELINE_ZONES = [
    {
        "id": "zone-c", "code": "ZONE C", "name": "South Coastal Offshore (Alibag-Murud Shelf)",
        "risk_score": 22.0, "status": "low_risk", "wave_hazard": {"value": 1.2},
        "wind_hazard": {"value": 12.0}, "geofence": {"restricted": False},
        "conditions": {"seaSurfaceTemp": "28.5°C", "chlorophyll": "1.2 mg/m³", "isRestricted": False, "waveHeight": "1.2 m", "windSpeed": "12.0 kt"},
        "pfzAdvisoryStatus": "Active PFZ Advisory"
    },
    {
        "id": "zone-d", "code": "ZONE D", "name": "Mid-Shelf Western Transition Trench",
        "risk_score": 38.0, "status": "moderate_risk", "wave_hazard": {"value": 1.8},
        "wind_hazard": {"value": 16.0}, "geofence": {"restricted": False},
        "conditions": {"seaSurfaceTemp": "27.8°C", "chlorophyll": "0.6 mg/m³", "isRestricted": False, "waveHeight": "1.8 m", "windSpeed": "16.0 kt"},
        "pfzAdvisoryStatus": "Borderline Thermal Front"
    },
    {
        "id": "zone-a", "code": "ZONE A", "name": "North Offshore Sector (Vasai-Manori Reach)",
        "risk_score": 82.0, "status": "high_risk", "wave_hazard": {"value": 3.6},
        "wind_hazard": {"value": 30.0}, "geofence": {"restricted": False},
        "conditions": {"seaSurfaceTemp": "28.0°C", "chlorophyll": "0.4 mg/m³", "isRestricted": False, "marineWarning": True, "waveHeight": "3.6 m", "windSpeed": "30.0 kt"},
        "pfzAdvisoryStatus": "Inactive"
    },
    {
        "id": "zone-b", "code": "ZONE B", "name": "Mumbai Harbor Security & Fairway Corridor",
        "risk_score": 61.0, "status": "restricted", "wave_hazard": {"value": 1.4},
        "wind_hazard": {"value": 14.0}, "geofence": {"restricted": True},
        "conditions": {"isRestricted": True, "geofenceStatus": "Naval Security Zone", "waveHeight": "1.4 m", "windSpeed": "14.0 kt"},
        "pfzAdvisoryStatus": "Inactive"
    }
]


def run_what_if_scenario(req: ScenarioRunRequest) -> WhatIfScenarioResult:
    """Executes a hypothetical what-if parameter modification without altering raw source data."""
    target_zid = req.target_zone_id.lower().replace("_", "-") if req.target_zone_id else "zone-c"
    res = scenario_engine.run_scenario(
        baseline_zones=DEFAULT_BASELINE_ZONES,
        wave_delta_m=req.wave_delta_m,
        wind_delta_kt=req.wind_delta_kt,
        target_zone_id=target_zid,
        geofence_override_zone_id=req.geofence_override_zone_id,
        scenario_time_label=req.scenario_time_label
    )
    return WhatIfScenarioResult(
        scenario_label=res["scenario_label"],
        scenario_title=res["scenario_title"],
        target_zone_id=res["target_zone_id"],
        baseline_comparison=BaselineComparison(**res["baseline_comparison"]),
        explanation=res["explanation"],
        ranked_candidates=res["ranked_candidates"],
        excluded_zones=res["excluded_zones"],
        top_candidate=res["top_candidate"],
        alternative_candidate=res["alternative_candidate"],
        is_simulation=True,
        scientific_disclaimer=res["scientific_disclaimer"]
    )


def reset_scenario_baseline() -> Dict[str, Any]:
    """Returns pristine baseline conditions without simulated modifications."""
    return {
        "status": "BASELINE_RESTORED",
        "message": "Scenario modifications cleared. Reverted to authoritative marine forecast baseline.",
        "baseline_zones": DEFAULT_BASELINE_ZONES
    }

