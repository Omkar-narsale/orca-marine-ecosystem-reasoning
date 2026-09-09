from typing import List, Dict, Any, Optional
from backend.app.services.alerts.alert_engine import alert_engine
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector
from backend.app.services.geospatial.zone_service import get_candidate_zones
from backend.app.services.geospatial.spatial_query import align_records_to_zone
from backend.app.services.risk.risk_engine import risk_engine

class AlertManager:
    """
    Stateful manager for active proactive safety alerts, acknowledgement state, and map focus routing.
    """
    def __init__(self):
        self._cached_alerts: List[Dict[str, Any]] = []
        self._acknowledged_ids: set[str] = set()

    async def get_active_alerts(
        self,
        force_refresh: bool = False,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        location_timestamp: Optional[str] = None,
        location_accuracy: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        # If user coordinates given, always evaluate spatially for current location
        if user_lat is not None and user_lon is not None:
            return await self.refresh_alerts(
                user_lat=user_lat,
                user_lon=user_lon,
                location_timestamp=location_timestamp,
                location_accuracy=location_accuracy
            )

        if not self._cached_alerts or force_refresh:
            await self.refresh_alerts()
        
        # Apply acknowledgement state
        for alert in self._cached_alerts:
            alert["acknowledged"] = (alert.get("id") in self._acknowledged_ids) or (alert.get("alert_id") in self._acknowledged_ids)

        return self._cached_alerts

    async def refresh_alerts(
        self,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        location_timestamp: Optional[str] = None,
        location_accuracy: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        incois_recs = await incois_connector.get_data()
        imd_recs = await imd_connector.get_data()
        all_recs = incois_recs + imd_recs

        candidate_zones = get_candidate_zones()
        evaluated = []
        for z in candidate_zones:
            aligned = align_records_to_zone(z["coordinates"], all_recs)
            res = risk_engine.evaluate_zone(
                zone_id=z["id"],
                zone_name=z["name"],
                zone_coords=z["coordinates"],
                records=aligned
            )
            res["coordinates"] = z.get("coordinates")
            res["center"] = z.get("center")
            evaluated.append(res)

        new_alerts = alert_engine.evaluate_alerts(
            evaluated_zones=evaluated,
            records=all_recs,
            user_lat=user_lat,
            user_lon=user_lon,
            location_timestamp=location_timestamp,
            location_accuracy=location_accuracy
        )
        
        for alert in new_alerts:
            alert["acknowledged"] = (alert.get("id") in self._acknowledged_ids) or (alert.get("alert_id") in self._acknowledged_ids)

        if user_lat is None or user_lon is None:
            self._cached_alerts = new_alerts

        return new_alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        self._acknowledged_ids.add(alert_id)
        for a in self._cached_alerts:
            if a["alert_id"] == alert_id:
                a["acknowledged"] = True
                return True
        return False

    def get_unread_count(self) -> int:
        return sum(1 for a in self._cached_alerts if a["alert_id"] not in self._acknowledged_ids)

alert_manager = AlertManager()
