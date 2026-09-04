import pytest
from backend.app.services.alerts.alert_engine import alert_engine, MarineAlertEngine
from backend.app.services.alerts.alert_manager import alert_manager
from backend.app.services.alerts.alert_rules import ALERT_RULES

@pytest.mark.anyio
async def test_alert_rules_definition():
    assert len(ALERT_RULES) >= 4
    rule_ids = [r["id"] for r in ALERT_RULES]
    assert "HIGH_WAVE_SWELL" in rule_ids
    assert "GALE_FORCE_WIND" in rule_ids
    assert "GEOFENCE_RESTRICTION" in rule_ids

@pytest.mark.anyio
async def test_deterministic_alert_generation():
    test_zones = [
        {
            "id": "zone-a",
            "code": "ZONE A",
            "name": "North Offshore Sector",
            "wave_hazard": {"value": 4.1, "severity": "HIGH", "source_id": "INCOIS_OSF"},
            "wind_hazard": {"value": 30.0, "severity": "HIGH", "source_id": "IMD_MARINE"},
            "warning_hazard": {"severity": "HIGH"},
            "geofence": {"restricted": False}
        },
        {
            "id": "zone-b",
            "code": "ZONE B",
            "name": "Harbor Approach & Naval Security",
            "wave_hazard": {"value": 1.4, "severity": "LOW", "source_id": "INCOIS_OSF"},
            "wind_hazard": {"value": 12.0, "severity": "LOW", "source_id": "IMD_MARINE"},
            "warning_hazard": {"severity": "NONE"},
            "geofence": {"restricted": True, "intersections": [{"name": "Naval Security Buffer"}]}
        },
        {
            "id": "zone-c",
            "code": "ZONE C",
            "name": "South Shelf Fishing Grounds",
            "wave_hazard": {"value": 1.1, "severity": "LOW", "source_id": "INCOIS_OSF"},
            "wind_hazard": {"value": 14.0, "severity": "LOW", "source_id": "IMD_MARINE"},
            "warning_hazard": {"severity": "NONE"},
            "geofence": {"restricted": False}
        }
    ]

    alerts = alert_engine.evaluate_alerts(test_zones, [])
    assert len(alerts) >= 3

    # Zone A should have High Wave, Gale Wind, Squall
    zone_a_alerts = [a for a in alerts if a["zone_id"] == "zone-a"]
    assert len(zone_a_alerts) >= 2
    severities = [a["severity"] for a in zone_a_alerts]
    assert "HIGH" in severities or "WARNING" in severities or "CRITICAL" in severities

    # Zone B should have Geofence Alert
    zone_b_alerts = [a for a in alerts if a["zone_id"] == "zone-b"]
    assert len(zone_b_alerts) >= 1
    assert zone_b_alerts[0]["alert_type"] in ("REGULATORY_CONSTRAINT", "GEOFENCE_RESTRICTION")

    # Zone C should have 0 severe alerts
    zone_c_alerts = [a for a in alerts if a["zone_id"] == "zone-c" and a["severity"] in ("CRITICAL", "HIGH", "WARNING")]
    assert len(zone_c_alerts) == 0

@pytest.mark.anyio
async def test_alert_deduplication():
    test_zones = [
        {
            "id": "zone-a",
            "code": "ZONE A",
            "wave_hazard": {"value": 4.1, "severity": "HIGH", "source_id": "INCOIS_OSF"},
            "geofence": {"restricted": False}
        }
    ]
    alerts_1 = alert_engine.evaluate_alerts(test_zones, [])
    assert len(alerts_1) == 1
    fp1 = alerts_1[0]["fingerprint"]

    # Evaluating again with same parameters produces identical fingerprint
    alerts_2 = alert_engine.evaluate_alerts(test_zones, [])
    assert len(alerts_2) == 1
    assert alerts_2[0]["fingerprint"] == fp1

@pytest.mark.anyio
async def test_alert_manager_active_and_acknowledge():
    alerts = await alert_manager.refresh_alerts()
    assert len(alerts) > 0

    first_alert = alerts[0]
    alert_id = first_alert["alert_id"]

    # Check unread count
    initial_unread = alert_manager.get_unread_count()
    assert initial_unread > 0

    # Acknowledge first alert
    ack_res = alert_manager.acknowledge_alert(alert_id)
    assert ack_res is True

    # Check unread count decreased
    new_unread = alert_manager.get_unread_count()
    assert new_unread == initial_unread - 1
