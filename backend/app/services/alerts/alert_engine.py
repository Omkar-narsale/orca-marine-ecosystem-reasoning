import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.alerts.alert_rules import ALERT_RULES

class MarineAlertEngine:
    """
    Deterministic Safety Alert Engine.
    Evaluates real-time authoritative marine/weather data and geofence states against deterministic safety rules.
    Generates deduplicated alert objects with source provenance and severity tiers.
    """
    def evaluate_alerts(
        self,
        evaluated_zones: List[Dict[str, Any]],
        records: List[NormalizedMarineRecord]
    ) -> List[Dict[str, Any]]:
        alerts = []
        seen_fingerprints = set()

        for z in evaluated_zones:
            zone_id = z.get("id") or z.get("zone_id")
            zone_code = z.get("code", zone_id.upper().replace("-", " "))
            zone_name = z.get("name", zone_code)

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
                        value=f"{wave_val} m"
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
                        value=f"{wave_val} m"
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
                    value=f"{wind_val} kt"
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
                    value="Active Squall Bulletin"
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
                    value=restr_name
                )

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
        value: str
    ):
        raw_fp = f"{zone_id}_{rule_id}_{valid_time}_{severity}"
        fp = hashlib.md5(raw_fp.encode("utf-8")).hexdigest()[:12]
        if fp in seen:
            return
        seen.add(fp)

        alert_id = f"alert_{zone_id}_{rule_id.lower()}"
        alerts.append({
            "alert_id": alert_id,
            "fingerprint": fp,
            "severity": severity,
            "alert_type": alert_type,
            "title": title,
            "zone_id": zone_id,
            "zone_code": zone_code,
            "zone_name": zone_name,
            "message": message,
            "value": value,
            "source_id": source_id,
            "source_name": source_name,
            "source_url": source_url,
            "valid_time": valid_time,
            "created_at": datetime.now().strftime("%d %b %Y %H:%M IST"),
            "acknowledged": False
        })

alert_engine = MarineAlertEngine()
