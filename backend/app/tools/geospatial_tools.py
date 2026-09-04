from typing import List, Dict, Any, Optional
from backend.app.tools.base import BaseTool
from backend.app.services.geospatial.geofence import geofence_engine, AUTHORITATIVE_GEOFENCES
from backend.app.services.geospatial.zone_service import get_candidate_zones, get_candidate_zone_by_id
from backend.app.services.geospatial.geometry import calculate_polygon_intersection

class CheckZoneGeofencesTool(BaseTool):
    name = "check_zone_geofences"
    description = "Checks candidate zone polygons against authoritative maritime Cadastre restricted areas (Naval Anchorage, TSS Fairway, Sanctuaries)."

    async def _run(self, zone_id: Optional[str] = None, **kwargs) -> tuple[Dict[str, Any], List[str]]:
        candidate_zones = get_candidate_zones()
        if zone_id:
            candidate_zones = [z for z in candidate_zones if z["id"] == zone_id]

        results = {}
        evidence_ids = []

        for z in candidate_zones:
            eval_res = geofence_engine.evaluate_zone_geofence(z["id"], z["coordinates"])
            results[z["id"]] = eval_res
            if eval_res["restricted"]:
                evidence_ids.append(f"ev_geofence_restricted_{z['id']}")
            else:
                evidence_ids.append(f"ev_geofence_clear_{z['id']}")

        return results, evidence_ids

class GetZonePolygonsTool(BaseTool):
    name = "get_zone_polygons"
    description = "Retrieves spatial boundaries, centroids, and depth profiles for ORCA candidate coastal sectors."

    async def _run(self, **kwargs) -> tuple[List[Dict[str, Any]], List[str]]:
        zones = get_candidate_zones()
        evidence_ids = [f"ev_zone_geometry_{z['id']}" for z in zones]
        return zones, evidence_ids

class CheckCustomPolygonTool(BaseTool):
    name = "check_custom_polygon_restriction"
    description = "Performs exact Shapely intersection for arbitrary user-defined maritime polygon coordinates against official restrictions."

    async def _run(self, coordinates: List[List[float]], **kwargs) -> tuple[Dict[str, Any], List[str]]:
        res = geofence_engine.evaluate_zone_geofence("custom_poly", coordinates)
        evidence_ids = ["ev_custom_geofence_check"]
        return res, evidence_ids

check_zone_geofences_tool = CheckZoneGeofencesTool()
get_zone_polygons_tool = GetZonePolygonsTool()
check_custom_polygon_tool = CheckCustomPolygonTool()
