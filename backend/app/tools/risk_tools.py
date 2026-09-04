from typing import List, Dict, Any, Optional
from backend.app.tools.base import BaseTool
from backend.app.services.risk.risk_engine import risk_engine
from backend.app.services.risk.suitability import suitability_engine
from backend.app.services.geospatial.zone_service import get_candidate_zones
from backend.app.services.geospatial.spatial_query import align_records_to_zone
from backend.app.schemas.marine import NormalizedMarineRecord

class CalculateZoneRiskTool(BaseTool):
    name = "calculate_zone_risk_scores"
    description = "Executes the deterministic weighted risk scoring formula across candidate sectors using spatially aligned wave, wind, and warning inputs."

    async def _run(
        self,
        records: List[NormalizedMarineRecord],
        time_window: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        candidate_zones = get_candidate_zones()
        evaluated_zones = []
        evidence_ids = []

        for z in candidate_zones:
            aligned = align_records_to_zone(z["coordinates"], records)
            eval_result = risk_engine.evaluate_zone(
                zone_id=z["id"],
                zone_name=z["name"],
                zone_coords=z["coordinates"],
                records=aligned,
                time_window=time_window
            )
            evaluated_zones.append(eval_result)
            evidence_ids.append(f"ev_risk_calc_{z['id']}")

        return evaluated_zones, evidence_ids

class EvaluateFishingSuitabilityTool(BaseTool):
    name = "evaluate_candidate_fishing_suitability"
    description = "Evaluates candidate fishing suitability by combining PFZ advisory alignments, chlorophyll fronts, and physical sea safety thresholds."

    async def _run(
        self,
        zone_evaluations: List[Dict[str, Any]],
        records: List[NormalizedMarineRecord],
        **kwargs
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        suitability_results = []
        evidence_ids = []

        for z_eval in zone_evaluations:
            zone_id = z_eval["zone_id"]
            # Filter records aligned to this zone
            # Candidate zones helper
            candidate_zones = get_candidate_zones()
            target_zone = next((z for z in candidate_zones if z["id"] == zone_id), None)
            zone_coords = target_zone["coordinates"] if target_zone else []
            aligned = align_records_to_zone(zone_coords, records) if zone_coords else records

            suit_eval = suitability_engine.evaluate_suitability(z_eval, aligned)
            suitability_results.append({
                "zone_id": zone_id,
                "suitability": suit_eval
            })
            evidence_ids.append(f"ev_suitability_{zone_id}")

        return suitability_results, evidence_ids

calculate_zone_risk_tool = CalculateZoneRiskTool()
evaluate_fishing_suitability_tool = EvaluateFishingSuitabilityTool()
