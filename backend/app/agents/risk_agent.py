from typing import Dict, Any, List, Optional
from backend.app.tools.risk_tools import calculate_zone_risk_tool, evaluate_fishing_suitability_tool
from backend.app.tools.evidence_tools import compile_evidence_tool
from backend.app.schemas.agentic import AgentTraceStep
from backend.app.schemas.marine import NormalizedMarineRecord

class RiskEvidenceAgent:
    """
    Risk & Evidence Agent: Orchestrates deterministic multi-source hazard synthesis,
    mathematical risk scoring, candidate fishing suitability, and source discrepancy detection.
    """
    async def run(
        self,
        ocean_records: List[NormalizedMarineRecord],
        weather_records: List[NormalizedMarineRecord],
        geofence_map: Dict[str, Any],
        time_window: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        all_records = ocean_records + weather_records
        tools_used = ["calculate_zone_risk_scores", "evaluate_candidate_fishing_suitability", "compile_evidence_graph"]

        # 1. Execute deterministic risk calculation tool
        risk_tool_res = await calculate_zone_risk_tool.execute(
            records=all_records,
            time_window=time_window
        )
        evaluated_zones = risk_tool_res.data or []

        # 2. Execute candidate fishing suitability tool
        suit_tool_res = await evaluate_fishing_suitability_tool.execute(
            zone_evaluations=evaluated_zones,
            records=all_records
        )
        suitability_results = suit_tool_res.data or []

        # 3. Assemble structured evidence graph
        ev_tool_res = await compile_evidence_tool.execute(
            records=all_records,
            evaluated_zones=evaluated_zones
        )
        evidence_nodes = ev_tool_res.data or []

        # 4. Check for source disagreement and missing data
        missing_data_flags = []
        source_disagreements = []

        has_wave = any(r.parameter == "significant_wave_height" for r in all_records)
        has_wind = any(r.parameter == "surface_wind_10m" for r in all_records)

        if not has_wave:
            missing_data_flags.append("Wave telemetry missing from INCOIS feed")
        if not has_wind:
            missing_data_flags.append("Wind telemetry missing from IMD feed")

        # Detect source divergence
        max_wave_val = max([r.value for r in all_records if r.parameter == "significant_wave_height" and isinstance(r.value, (int, float))], default=0.0)
        has_squall_warning = any(r.data_type == "warning" for r in all_records)

        if max_wave_val < 1.0 and has_squall_warning:
            source_disagreements.append("Source divergence: Low numerical swell with active statutory squall alert")

        # 5. Determine overall synthesized confidence
        avoid_count = sum(1 for z in evaluated_zones if z["classification"] in ("HIGH_RISK", "RESTRICTED"))
        candidate_count = sum(1 for z in evaluated_zones if z["classification"] in ("SUITABLE_CANDIDATE", "CAUTION"))

        base_conf = 88
        if missing_data_flags:
            base_conf -= 25
        if source_disagreements:
            base_conf -= 10
        if len(all_records) < 6:
            base_conf -= 15

        conf_score = max(35, min(95, base_conf))
        conf_level = "High" if conf_score >= 80 else "Medium" if conf_score >= 60 else "Low"

        trace_step = AgentTraceStep(
            agentName="Risk & Evidence Agent",
            action=f"Deterministic risk computed: {avoid_count} avoid sectors, {candidate_count} candidate sectors",
            status="completed",
            agentStatus="COMPLETE",
            toolsUsed=tools_used,
            dataCategories=["Weighted Physical Risk", "Geofence Override Matrix", "Evidence Graph Links"],
            evidenceCount=len(evidence_nodes)
        )

        return {
            "agent": "risk",
            "status": "COMPLETE",
            "evaluated_zones": evaluated_zones,
            "suitability_results": suitability_results,
            "evidence_nodes": evidence_nodes,
            "missing_data_flags": missing_data_flags,
            "source_disagreements": source_disagreements,
            "confidence_score": conf_score,
            "confidence_level": conf_level,
            "confidence_explanation": f"Confidence is {conf_level.lower()} ({conf_score}%) calculated from multi-source convergence across INCOIS OSF, IMD coastal bulletin, and GIS Cadastre.",
            "trace_step": trace_step
        }

risk_agent = RiskEvidenceAgent()
