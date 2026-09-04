from typing import Dict, Any, List, Optional

class DecisionTradeoffEngine:
    """
    Trade-off Analysis Engine for ORCA Phase 5.
    Compares two or more candidate zones and explains operational trade-offs
    between physical safety, environmental indicators, transit distance, and regulatory constraints.
    """
    def compare_zones(
        self,
        zone_a: Dict[str, Any],
        zone_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        risk_a = zone_a.get("risk_score", zone_a.get("riskScore", 50))
        risk_b = zone_b.get("risk_score", zone_b.get("riskScore", 50))
        suit_a = zone_a.get("suitability_score", 50)
        suit_b = zone_b.get("suitability_score", 50)

        code_a = zone_a.get("code", zone_a.get("id", "ZONE A"))
        code_b = zone_b.get("code", zone_b.get("id", "ZONE B"))

        delta_risk = risk_b - risk_a # positive if B is riskier
        delta_suit = suit_a - suit_b # positive if A is more suitable

        reasons = []
        if risk_a < risk_b:
            reasons.append(f"{code_a} presents lower operational risk ({risk_a} vs {risk_b}).")
        elif risk_b < risk_a:
            reasons.append(f"{code_b} presents lower operational risk ({risk_b} vs {risk_a}).")

        if suit_a > suit_b:
            reasons.append(f"{code_a} demonstrates stronger supportive oceanographic indicators ({suit_a} vs {suit_b}).")
        elif suit_b > suit_a:
            reasons.append(f"{code_b} demonstrates stronger supportive oceanographic indicators ({suit_b} vs {suit_a}).")

        if zone_a.get("is_excluded"):
            recommendation = f"{code_b} is strongly preferred because {code_a} is currently EXCLUDED ({zone_a.get('exclusion_reason', 'Safety / Geofence')})."
        elif zone_b.get("is_excluded"):
            recommendation = f"{code_a} is strongly preferred because {code_b} is currently EXCLUDED ({zone_b.get('exclusion_reason', 'Safety / Geofence')})."
        elif suit_a >= suit_b and risk_a <= risk_b:
            recommendation = f"{code_a} is the superior operational candidate across both safety and environmental parameters."
        elif suit_b >= suit_a and risk_b <= risk_a:
            recommendation = f"{code_b} is the superior operational candidate across both safety and environmental parameters."
        else:
            recommendation = (
                f"Trade-off Detected: {code_a} offers lower risk ({risk_a}), while {code_b} shows alternative environmental indicators. "
                f"For artisanal/small craft safety, {code_a if risk_a < risk_b else code_b} is recommended."
            )

        return {
            "zone_1": {
                "code": code_a,
                "name": zone_a.get("name", code_a),
                "risk_score": risk_a,
                "suitability_score": suit_a,
                "status": zone_a.get("status_label", zone_a.get("statusLabel", "Candidate"))
            },
            "zone_2": {
                "code": code_b,
                "name": zone_b.get("name", code_b),
                "risk_score": risk_b,
                "suitability_score": suit_b,
                "status": zone_b.get("status_label", zone_b.get("statusLabel", "Candidate"))
            },
            "comparison_summary": " · ".join(reasons),
            "recommendation": recommendation,
            "delta_risk": delta_risk,
            "delta_suitability": delta_suit
        }

tradeoff_engine = DecisionTradeoffEngine()


def compare_zones_tradeoff(zone_a_id: str = "zone-c", zone_b_id: str = "zone-d") -> Dict[str, Any]:
    """Compares two zones by ID and generates grounded trade-off analysis."""
    default_zone_map = {
        "zone-c": {"id": "zone-c", "code": "ZONE C", "name": "South Coastal Offshore", "risk_score": 22.0, "suitability_score": 72.0, "status_label": "Candidate", "is_excluded": False},
        "zone-d": {"id": "zone-d", "code": "ZONE D", "name": "Mid-Shelf Western Transition", "risk_score": 38.0, "suitability_score": 61.0, "status_label": "Candidate", "is_excluded": False},
        "zone-a": {"id": "zone-a", "code": "ZONE A", "name": "North Offshore Sector", "risk_score": 82.0, "suitability_score": 15.0, "status_label": "High Risk", "is_excluded": True, "exclusion_reason": "High Wave/Wind Hazard"},
        "zone-b": {"id": "zone-b", "code": "ZONE B", "name": "Mumbai Harbor Fairway", "risk_score": 61.0, "suitability_score": 0.0, "status_label": "Restricted", "is_excluded": True, "exclusion_reason": "Naval Security Restriction"}
    }
    
    za = default_zone_map.get(zone_a_id.lower().replace("_", "-"), {"id": zone_a_id, "code": zone_a_id.upper(), "risk_score": 50.0, "suitability_score": 50.0})
    zb = default_zone_map.get(zone_b_id.lower().replace("_", "-"), {"id": zone_b_id, "code": zone_b_id.upper(), "risk_score": 50.0, "suitability_score": 50.0})
    
    return tradeoff_engine.compare_zones(za, zb)

