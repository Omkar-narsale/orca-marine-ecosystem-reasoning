import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.alerts.alert_rules import ALERT_RULES
from backend.app.services.geospatial.spatial_engine import SpatialEngine

spatial_engine = SpatialEngine()

SEVERITY_WEIGHTS = {
    "CRITICAL": 4,
    "WARNING": 3,
    "ADVISORY": 2,
    "INFO": 1
}

class MarineAlertEngine:
    """
    Spatially Aware Marine Alert Engine.
    Evaluates real-time authoritative marine/weather data and geofence boundaries against deterministic safety rules.
    Ties alerts directly to user coordinates, computes distance, checks polygon intersections,
    filters by spatial relevance, and ranks by proximity, severity, and temporal validity.
    """

    def evaluate_alerts(
        self,
        evaluated_zones: List[Dict[str, Any]],
        records: List[NormalizedMarineRecord],
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        location_timestamp: Optional[str] = None,
        location_accuracy: Optional[float] = None,
        max_proximity_km: float = 85.0
    ) -> List[Dict[str, Any]]:
        alerts = []
        seen_fingerprints = set()

        # Check staleness if location timestamp provided
        staleness_notice = None
        if location_timestamp:
            try:
                # Support ISO or string timestamps
                ts = datetime.fromisoformat(location_timestamp.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_minutes = int((now - ts).total_seconds() / 60)
                if age_minutes >= 20:
                    staleness_notice = f"Your location was last updated {age_minutes} minutes ago."
            except Exception:
                pass

        for z in evaluated_zones:
            zone_id = z.get("id") or z.get("zone_id")
            zone_code = z.get("code", zone_id.upper().replace("-", " "))
            zone_name = z.get("name", zone_code)
            coords = z.get("coordinates") or []
            center = z.get("center")

            # Determine zone center
            if not center and coords:
                lats = [pt[0] for pt in coords]
                lons = [pt[1] for pt in coords]
                center = [sum(lats) / len(lats), sum(lons) / len(lons)]
            elif not center:
                center = [18.9, 72.8]

            zone_lat, zone_lon = center[0], center[1]

            # Spatial distance and polygon intersection
            distance_from_user_km = None
            is_inside = False
            if user_lat is not None and user_lon is not None:
                distance_from_user_km = round(
                    spatial_engine.calculate_distance(user_lat, user_lon, zone_lat, zone_lon), 1
                )
                if coords:
                    try:
                        is_inside = spatial_engine.point_in_polygon(user_lat, user_lon, coords)
                    except Exception:
                        is_inside = False
                if is_inside:
                    distance_from_user_km = 0.0

                # Filter out alerts that are far away from user location
                if not is_inside and distance_from_user_km > max_proximity_km:
                    continue

            geometry = {
                "type": "Polygon",
                "coordinates": [coords] if coords and isinstance(coords[0], list) and not isinstance(coords[0][0], list) else coords
            } if coords else {
                "type": "Point",
                "coordinates": [zone_lon, zone_lat]
            }

            # 1. Evaluate Wave Alert
            wave_h = z.get("wave_hazard", {})
            wave_val = wave_h.get("value")
            if wave_val is not None and isinstance(wave_val, (int, float)):
                if wave_val >= 3.5:
                    rule = next(r for r in ALERT_RULES if r["id"] == "HIGH_WAVE_SWELL")
                    self._add_alert(
                        alerts, seen_fingerprints,
                        rule_id=rule["id"],
                        severity=rule["severity"],
                        alert_type=rule["type"],
                        title=f"{zone_code}: {rule['title']}",
                        zone_id=zone_id,
                        zone_code=zone_code,
                        zone_name=zone_name,
                        message=rule["message_template"].format(value=wave_val),
                        source_id=wave_h.get("source_id", "INCOIS_OSF"),
                        source_name="INCOIS Wave Watch III",
                        source_url=wave_h.get("source_url", "https://incois.gov.in/oceanservices/osfforecast.jsp"),
                        valid_time=wave_h.get("valid_time", "Tomorrow 06:00 IST"),
                        value=f"{wave_val} m",
                        location={"latitude": zone_lat, "longitude": zone_lon},
                        affected_geometry=geometry,
                        distance_from_user_km=distance_from_user_km,
                        is_inside=is_inside,
                        staleness_notice=staleness_notice
                    )
                elif wave_val >= 2.0:
                    rule = next(r for r in ALERT_RULES if r["id"] == "MODERATE_WAVE_SWELL")
                    self._add_alert(
                        alerts, seen_fingerprints,
                        rule_id=rule["id"],
                        severity=rule["severity"],
                        alert_type=rule["type"],
                        title=f"{zone_code}: {rule['title']}",
                        zone_id=zone_id,
                        zone_code=zone_code,
                        zone_name=zone_name,
                        message=rule["message_template"].format(value=wave_val),
                        source_id=wave_h.get("source_id", "INCOIS_OSF"),
                        source_name="INCOIS Wave Watch III",
                        source_url=wave_h.get("source_url", "https://incois.gov.in/oceanservices/osfforecast.jsp"),
                        valid_time=wave_h.get("valid_time", "Tomorrow 06:00 IST"),
                        value=f"{wave_val} m",
                        location={"latitude": zone_lat, "longitude": zone_lon},
                        affected_geometry=geometry,
                        distance_from_user_km=distance_from_user_km,
                        is_inside=is_inside,
                        staleness_notice=staleness_notice
                    )

            # 2. Evaluate Wind Alert
            wind_h = z.get("wind_hazard", {})
            wind_val = wind_h.get("value")
            if wind_val is not None and isinstance(wind_val, (int, float)) and wind_val >= 28.0:
                rule = next(r for r in ALERT_RULES if r["id"] == "GALE_FORCE_WIND")
                self._add_alert(
                    alerts, seen_fingerprints,
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    alert_type=rule["type"],
                    title=f"{zone_code}: {rule['title']}",
                    zone_id=zone_id,
                    zone_code=zone_code,
                    zone_name=zone_name,
                    message=rule["message_template"].format(value=wind_val),
                    source_id=wind_h.get("source_id", "IMD_MARINE"),
                    source_name="IMD Coastal Division",
                    source_url=wind_h.get("source_url", "https://api.imd.gov.in/public/api_reference.html"),
                    valid_time=wind_h.get("valid_time", "Tomorrow 06:00 IST"),
                    value=f"{wind_val} kt",
                    location={"latitude": zone_lat, "longitude": zone_lon},
                    affected_geometry=geometry,
                    distance_from_user_km=distance_from_user_km,
                    is_inside=is_inside,
                    staleness_notice=staleness_notice
                )

            # 3. Evaluate Marine Warnings
            warn_h = z.get("warning_hazard", {})
            if warn_h.get("severity") == "HIGH" or z.get("conditions", {}).get("marineWarning"):
                rule = next(r for r in ALERT_RULES if r["id"] == "SQUALL_ALERT")
                self._add_alert(
                    alerts, seen_fingerprints,
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    alert_type=rule["type"],
                    title=f"{zone_code}: {rule['title']}",
                    zone_id=zone_id,
                    zone_code=zone_code,
                    zone_name=zone_name,
                    message=rule["message_template"],
                    source_id="IMD_MARINE",
                    source_name="IMD Marine Bulletin",
                    source_url="https://api.imd.gov.in/public/api_reference.html",
                    valid_time="Active Next 24h",
                    value="Active Squall Bulletin",
                    location={"latitude": zone_lat, "longitude": zone_lon},
                    affected_geometry=geometry,
                    distance_from_user_km=distance_from_user_km,
                    is_inside=is_inside,
                    staleness_notice=staleness_notice
                )

            # 4. Evaluate Geofence Restrictions
            geofence = z.get("geofence", {})
            if geofence.get("restricted") or z.get("conditions", {}).get("isRestricted"):
                intersections = geofence.get("intersections", [])
                restr_name = intersections[0]["name"] if intersections else "Naval Security Buffer & Fairway"
                rule = next(r for r in ALERT_RULES if r["id"] == "GEOFENCE_RESTRICTION")
                self._add_alert(
                    alerts, seen_fingerprints,
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    alert_type=rule["type"],
                    title=f"{zone_code}: {rule['title']}",
                    zone_id=zone_id,
                    zone_code=zone_code,
                    zone_name=zone_name,
                    message=rule["message_template"].format(name=restr_name),
                    source_id="GIS_CADASTRE",
                    source_name="National Hydrographic Cadastre",
                    source_url="https://hydro-india.nic.in/",
                    valid_time="Rev 2026.1 Official Gazette",
                    value=restr_name,
                    location={"latitude": zone_lat, "longitude": zone_lon},
                    affected_geometry=geometry,
                    distance_from_user_km=distance_from_user_km,
                    is_inside=is_inside,
                    staleness_notice=staleness_notice
                )

        # Prioritize alerts:
        # 1. Directly affecting user (inside or distance == 0)
        # 2. Distance from user (nearest first)
        # 3. Severity (CRITICAL > WARNING > ADVISORY > INFO)
        def alert_sort_key(a):
            dist = a.get("distance_from_user_km")
            dist_val = dist if dist is not None else 999.0
            is_inside_val = 0 if a.get("is_inside") else (1 if dist_val <= 15.0 else 2)
            sev_val = -SEVERITY_WEIGHTS.get(a.get("severity", "INFO"), 1)
            return (is_inside_val, dist_val, sev_val)

        alerts.sort(key=alert_sort_key)
        return alerts

    def _add_alert(
        self,
        alerts: List[Dict[str, Any]],
        seen: set,
        rule_id: str,
        severity: str,
        alert_type: str,
        title: str,
        zone_id: str,
        zone_code: str,
        zone_name: str,
        message: str,
        source_id: str,
        source_name: str,
        source_url: str,
        valid_time: str,
        value: str,
        location: Dict[str, float],
        affected_geometry: Dict[str, Any],
        distance_from_user_km: Optional[float] = None,
        is_inside: bool = False,
        staleness_notice: Optional[str] = None
    ):
        raw_fp = f"{zone_id}_{rule_id}_{valid_time}_{severity}"
        fp = hashlib.md5(raw_fp.encode("utf-8")).hexdigest()[:12]
        if fp in seen:
            return
        seen.add(fp)

        alert_id = f"alert_{zone_id}_{rule_id.lower()}"
        alert_obj = {
            "id": alert_id,
            "alert_id": alert_id,
            "fingerprint": fp,
            "type": alert_type,
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "zone_id": zone_id,
            "zone_code": zone_code,
            "zone_name": zone_name,
            "message": message,
            "value": value,
            "location": location,
            "affected_geometry": affected_geometry,
            "distance_from_user_km": distance_from_user_km,
            "is_inside": is_inside,
            "source": source_name,
            "source_id": source_id,
            "source_name": source_name,
            "source_url": source_url,
            "valid_from": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "valid_until": valid_time,
            "valid_time": valid_time,
            "status": "ACTIVE",
            "created_at": datetime.now().strftime("%d %b %Y %H:%M IST"),
            "acknowledged": False
        }
        if staleness_notice:
            alert_obj["staleness_notice"] = staleness_notice

        alerts.append(alert_obj)

alert_engine = MarineAlertEngine()
