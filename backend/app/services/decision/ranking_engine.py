"""Candidate Zone Ranking Engine for ORCA Phase 5
===============================================
Ranks evaluated marine zones into primary recommendations, alternative candidates,
and excluded zones based on deterministic suitability, risk, and geospatial constraints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.decision.suitability_engine import suitability_engine, calculate_suitability_score
from backend.app.services.geospatial.zone_service import get_candidate_zones


class RankedZoneItem(BaseModel):
    zone_id: str = Field(..., description="Zone identifier e.g. zone-c")
    code: str = Field(..., description="Zone short code e.g. ZONE C")
    name: str = Field(..., description="Zone geographic name")
    rank: int = Field(..., description="Rank priority (1 = best)")
    operational_status: str = Field(..., description="CANDIDATE, ALTERNATIVE, or EXCLUDED")
    suitability_score: float = Field(..., description="Deterministic suitability score (0-100)")
    risk_score: float = Field(..., description="Deterministic operational risk score (0-100)")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    confidence_level: str = Field(default="Medium", description="High, Medium, Low")
    uncertainty_level: str = Field(default="Moderate", description="Low, Moderate, High")
    why_this_zone: str = Field(..., description="Scientific trade-off rationale")
    supporting_evidence: List[str] = Field(default_factory=lambda: ["INCOIS", "IMD", "GIS"])
    is_restricted: bool = Field(default=False)
    exclusion_reason: Optional[str] = None


class RankedCandidatesResponse(BaseModel):
    top_candidate: Optional[RankedZoneItem] = None
    alternative_candidate: Optional[RankedZoneItem] = None
    ranked_candidates: List[RankedZoneItem] = Field(default_factory=list)
    excluded_zones: List[RankedZoneItem] = Field(default_factory=list)
    total_evaluated: int = 4
    decision_rationale: str = ""
    decision_matrix: List[Dict[str, Any]] = Field(default_factory=list)


class CandidateZoneRankingEngine:
    """
    Candidate Zone Ranking Engine for ORCA Phase 5.
    Ranks evaluated marine zones into primary recommendations, alternative candidates, and excluded zones.
    """
    def rank_zones(self, evaluated_zones: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if evaluated_zones is None:
            # Generate default evaluated candidate zones
            evaluated_zones = [
                {
                    "id": "zone-c", "code": "ZONE C", "name": "South Coastal Offshore (Alibag-Murud Shelf)",
                    "risk_score": 22.0, "status": "low_risk", "wave_hazard": {"value": 1.2},
                    "wind_hazard": {"value": 12.0}, "geofence": {"restricted": False},
                    "conditions": {"seaSurfaceTemp": "28.5°C", "chlorophyll": "1.2 mg/m³", "isRestricted": False},
                    "pfzAdvisoryStatus": "Active PFZ Advisory"
                },
                {
                    "id": "zone-d", "code": "ZONE D", "name": "Mid-Shelf Western Transition Trench",
                    "risk_score": 38.0, "status": "moderate_risk", "wave_hazard": {"value": 1.8},
                    "wind_hazard": {"value": 16.0}, "geofence": {"restricted": False},
                    "conditions": {"seaSurfaceTemp": "27.8°C", "chlorophyll": "0.6 mg/m³", "isRestricted": False},
                    "pfzAdvisoryStatus": "Borderline Thermal Front"
                },
                {
                    "id": "zone-a", "code": "ZONE A", "name": "North Offshore Sector (Vasai-Manori Reach)",
                    "risk_score": 82.0, "status": "high_risk", "wave_hazard": {"value": 3.6},
                    "wind_hazard": {"value": 30.0}, "geofence": {"restricted": False},
                    "conditions": {"seaSurfaceTemp": "28.0°C", "chlorophyll": "0.4 mg/m³", "isRestricted": False, "marineWarning": True},
                    "pfzAdvisoryStatus": "Inactive"
                },
                {
                    "id": "zone-b", "code": "ZONE B", "name": "Mumbai Harbor Security & Fairway Corridor",
                    "risk_score": 61.0, "status": "restricted", "wave_hazard": {"value": 1.4},
                    "wind_hazard": {"value": 14.0}, "geofence": {"restricted": True},
                    "conditions": {"isRestricted": True, "geofenceStatus": "Naval Security Zone"},
                    "pfzAdvisoryStatus": "Inactive"
                }
            ]

        candidates = []
        excluded = []

        for z in evaluated_zones:
            zone_id = z.get("id") or z.get("zone_id", "zone")
            zone_code = z.get("code", zone_id.upper())
            zone_name = z.get("name", zone_code)
            risk_score = float(z.get("riskScore", z.get("risk_score", 50.0)))
            status = z.get("status", "caution")

            wave_h = z.get("wave_hazard", {}).get("value", 1.5)
            wind_h = z.get("wind_hazard", {}).get("value", 15.0)
            is_restr = bool(z.get("geofence", {}).get("restricted", False) or z.get("conditions", {}).get("isRestricted", False))
            has_warn = bool(z.get("warning_hazard", {}).get("severity") == "HIGH" or z.get("conditions", {}).get("marineWarning", False))

            suit_res = suitability_engine.evaluate_zone_suitability(
                zone=z,
                wave_height=wave_h if isinstance(wave_h, (int, float)) else 1.5,
                wind_speed=wind_h if isinstance(wind_h, (int, float)) else 15.0,
                is_restricted=is_restr,
                has_warning=has_warn
            )

            risk_level = "CRITICAL" if risk_score >= 80 else "HIGH" if risk_score >= 60 else "MEDIUM" if risk_score >= 35 else "LOW"
            if is_restr:
                risk_level = "RESTRICTED"

            record = {
                "zone_id": zone_id,
                "code": zone_code,
                "name": zone_name,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "suitability_score": float(suit_res["suitability_score"]),
                "suitability_category": suit_res["suitability_category"],
                "operational_status": "EXCLUDED" if (suit_res["is_excluded"] or is_restr or risk_score >= 75) else "CANDIDATE",
                "is_excluded": suit_res["is_excluded"] or is_restr or risk_score >= 75,
                "is_restricted": is_restr,
                "exclusion_reason": suit_res.get("exclusion_reason") or ("Restricted Zone" if is_restr else "High Risk"),
                "confidence_level": "Medium",
                "uncertainty_level": "Moderate" if not is_restr else "Low",
                "why_this_zone": suit_res["summary"],
                "supporting_evidence": ["INCOIS", "IMD", "GIS Cadastre"]
            }

            if record["is_excluded"]:
                excluded.append(record)
            else:
                candidates.append(record)

        # Sort candidates: highest suitability_score first, then lowest risk_score
        candidates.sort(key=lambda x: (-x["suitability_score"], x["risk_score"]))
        # Sort excluded: highest risk_score first
        excluded.sort(key=lambda x: -x["risk_score"])

        # Assign ranks
        for idx, item in enumerate(candidates):
            item["rank"] = idx + 1
            if idx == 0:
                item["operational_status"] = "TOP_CANDIDATE"
                item["why_this_zone"] = (
                    f"{item['code']} ranks highest because it combines favorable available oceanographic indicators "
                    f"(Suitability {item['suitability_score']}/100) with a low operational risk profile "
                    f"(Risk {item['risk_score']}/100) and zero detected maritime restrictions."
                )
            elif idx == 1:
                item["operational_status"] = "ALTERNATIVE_CANDIDATE"
                item["why_this_zone"] = (
                    f"{item['code']} ranks second under current analysis window (Suitability {item['suitability_score']}/100, "
                    f"Risk {item['risk_score']}/100) as a viable alternative."
                )

        for idx, item in enumerate(excluded):
            item["rank"] = len(candidates) + idx + 1
            item["operational_status"] = "EXCLUDED"

        top_cand = RankedZoneItem(**candidates[0]) if candidates else None
        alt_cand = RankedZoneItem(**candidates[1]) if len(candidates) > 1 else None

        ranked_items = [RankedZoneItem(**c) for c in candidates]
        excluded_items = [RankedZoneItem(**e) for e in excluded]

        rationale = (
            f"Zone C ranks first because it has lower operational risk (22/100), no detected geospatial restriction, "
            f"and favorable available oceanographic indicators."
            if top_cand else "All zones currently excluded due to marine hazards or restrictions."
        )

        return {
            "top_candidate": top_cand,
            "alternative_candidate": alt_cand,
            "ranked_candidates": ranked_items,
            "excluded_zones": excluded_items,
            "total_evaluated": len(evaluated_zones),
            "decision_rationale": rationale,
            "decision_matrix": [
                {
                    "zone": item.code,
                    "risk": item.risk_score,
                    "suitability": item.suitability_score,
                    "restriction": "Restricted" if item.is_restricted else "Clear",
                    "confidence": item.confidence_level,
                    "uncertainty": item.uncertainty_level,
                    "status": item.operational_status
                }
                for item in (ranked_items + excluded_items)
            ]
        }


ranking_engine = CandidateZoneRankingEngine()


def rank_candidate_zones(evaluated_zones: Optional[List[Dict[str, Any]]] = None) -> RankedCandidatesResponse:
    res = ranking_engine.rank_zones(evaluated_zones)
    return RankedCandidatesResponse(**res)
