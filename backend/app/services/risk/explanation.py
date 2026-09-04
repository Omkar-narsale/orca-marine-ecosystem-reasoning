from typing import Dict, Any, List

class DeterministicExplanationEngine:
    """
    Produces transparent, deterministic explanations for ORCA decisions based on calculated risk and constraints.
    """
    def generate_zone_explanation(self, zone_eval: Dict[str, Any]) -> List[str]:
        reasons = []
        classification = zone_eval.get("classification", "")
        wave_h = zone_eval.get("wave_hazard", {})
        wind_h = zone_eval.get("wind_hazard", {})
        warn_h = zone_eval.get("warning_hazard", {})
        geofence = zone_eval.get("geofence", {"restricted": False, "intersections": []})

        if geofence.get("restricted"):
            for inter in geofence.get("intersections", []):
                reasons.append(
                    f"Geofence restriction: Intersects {inter['name']} ({inter['authority']}) — {inter['restriction_level']}."
                )

        if wave_h.get("severity") in ("HIGH", "CRITICAL"):
            reasons.append(
                f"Elevated wave swell ({wave_h['value']}m forecast from {wave_h.get('source', 'INCOIS')}) breaches 3.5m craft safety threshold."
            )
        elif wave_h.get("severity") == "MODERATE":
            reasons.append(
                f"Moderate wave swell ({wave_h['value']}m from {wave_h.get('source', 'INCOIS')}) requires caution for crafts < 12m."
            )
        elif wave_h.get("severity") == "LOW":
            reasons.append(
                f"Calm sea state ({wave_h['value']}m swell forecast from {wave_h.get('source', 'INCOIS')}) within favorable operating envelope."
            )

        if wind_h.get("severity") in ("HIGH", "CRITICAL"):
            reasons.append(
                f"Strong wind forecast ({wind_h['value']} kt from {wind_h.get('source', 'IMD')}) indicates elevated surface chop and capsize risk."
            )
        elif wind_h.get("severity") == "LOW":
            reasons.append(
                f"Gentle surface breeze ({wind_h['value']} kt from {wind_h.get('source', 'IMD')}) supports smooth navigation."
            )

        if warn_h.get("severity") == "HIGH":
            reasons.append(
                f"Active statutory alert from {warn_h.get('source', 'IMD')}: {warn_h.get('value', 'Active warning')}"
            )

        if not reasons:
            reasons.append("No critical physical hazards or regulatory geofence restrictions detected in available data.")

        return reasons

    def generate_executive_decision_summary(
        self,
        avoid_zones: List[Dict[str, Any]],
        candidate_zones: List[Dict[str, Any]],
        time_label: str
    ) -> str:
        avoid_names = ", ".join([f"{z['code']} ({z.get('status_label', z.get('statusLabel', 'Avoid'))})" for z in avoid_zones]) if avoid_zones else "None"
        candidate_names = ", ".join([f"{z['code']} ({z.get('status_label', z.get('statusLabel', 'Candidate'))})" for z in candidate_zones]) if candidate_zones else "None"

        if avoid_zones and candidate_zones:
            return (
                f"ORCA deterministic multi-source analysis for {time_label} recommends avoiding {avoid_names}. "
                f"Favorable conditions with no critical hazards detected in {candidate_names}."
            )
        elif avoid_zones:
            return f"ORCA recommends bypassing all operational sectors in {avoid_names} due to hazardous coastal conditions."
        else:
            return f"All evaluated coastal sectors ({candidate_names}) demonstrate favorable operating conditions under available forecast data."

explanation_engine = DeterministicExplanationEngine()
