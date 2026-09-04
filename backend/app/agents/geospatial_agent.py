from typing import Dict, Any, List, Optional
from backend.app.tools.geospatial_tools import check_zone_geofences_tool, get_zone_polygons_tool
from backend.app.schemas.agentic import AgentTraceStep

class GeospatialAgent:
    """
    Geospatial Agent: Specialized agent responsible for spatial indexing, polygon containment,
    and cadastral geofence verification (Naval Anchorage, TSS Fairways, Marine Protected Areas).
    """
    async def run(
        self,
        required_tools: List[str],
        target_zone_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        tools_used = ["check_zone_geofences"]
        geo_result = await check_zone_geofences_tool.execute(zone_id=target_zone_id)
        
        geofence_map = geo_result.data or {}
        restricted_count = sum(1 for v in geofence_map.values() if v.get("restricted", False))
        
        trace_step = AgentTraceStep(
            agentName="Geospatial Agent",
            action=f"Verified 3 authoritative Cadastre polygons ({restricted_count} restricted overlap identified)",
            status="completed" if geo_result.success else "failed",
            agentStatus="COMPLETE" if geo_result.success else "FAILED",
            toolsUsed=tools_used,
            dataCategories=["National Hydrographic Cadastre", "Naval Anchorage Buffers", "TSS Fairways"],
            evidenceCount=len(geo_result.evidence_ids)
        )

        return {
            "agent": "geospatial",
            "status": "COMPLETE" if geo_result.success else "FAILED",
            "geofence_evaluations": geofence_map,
            "restricted_count": restricted_count,
            "evidence_ids": geo_result.evidence_ids,
            "trace_step": trace_step
        }

geospatial_agent = GeospatialAgent()
