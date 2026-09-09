from typing import Dict, Any, List

ALERT_SEVERITIES = ["INFO", "ADVISORY", "WARNING", "CRITICAL"]

STRUCTURED_ALERT_TYPES = [
    "WIND_ALERT",
    "WAVE_ALERT",
    "SWELL_ALERT",
    "CYCLONE_ALERT",
    "WEATHER_ALERT",
    "FISHING_RESTRICTION",
    "MARITIME_RESTRICTION",
    "GEOFENCE_ALERT",
    "OCEAN_CONDITION_ALERT",
    "PFZ_ADVISORY"
]

ALERT_RULES = [
    {
        "id": "HIGH_WAVE_SWELL",
        "parameter": "significant_wave_height",
        "threshold": 3.5,
        "unit": "m",
        "severity": "CRITICAL",
        "type": "WAVE_ALERT",
        "title": "High Wave Swell Alert",
        "message_template": "Elevated significant wave height ({value}m) forecast by INCOIS exceeding craft safety limit of 3.5m.",
        "source": "INCOIS_OSF"
    },
    {
        "id": "MODERATE_WAVE_SWELL",
        "parameter": "significant_wave_height",
        "threshold": 2.0,
        "unit": "m",
        "severity": "ADVISORY",
        "type": "SWELL_ALERT",
        "title": "Moderate Wave Swell Advisory",
        "message_template": "Moderate wave swell ({value}m) forecast by INCOIS. Caution advised for artisanal craft < 12m.",
        "source": "INCOIS_OSF"
    },
    {
        "id": "GALE_FORCE_WIND",
        "parameter": "surface_wind_10m",
        "threshold": 28.0,
        "unit": "kt",
        "severity": "CRITICAL",
        "type": "WIND_ALERT",
        "title": "Gale Force Coastal Wind Warning",
        "message_template": "Strong sustained wind forecast ({value} kt) by IMD posing capsize hazard.",
        "source": "IMD_MARINE"
    },
    {
        "id": "SQUALL_ALERT",
        "parameter": "marine_fishermen_warning",
        "severity": "WARNING",
        "type": "WEATHER_ALERT",
        "title": "IMD Marine Squall Alert",
        "message_template": "Active statutory fishermen bulletin issued by IMD for northern Maharashtra shelf reach.",
        "source": "IMD_MARINE"
    },
    {
        "id": "GEOFENCE_RESTRICTION",
        "parameter": "geofence_restriction",
        "severity": "WARNING",
        "type": "GEOFENCE_ALERT",
        "title": "Naval / Commercial Fairway Restriction",
        "message_template": "Zone geometry intersects verified maritime Cadastre restriction boundary ({name}). Entry prohibited.",
        "source": "GIS_CADASTRE"
    },
    {
        "id": "FISHING_BAN_RESTRICTION",
        "parameter": "monsoon_fishing_ban",
        "severity": "CRITICAL",
        "type": "FISHING_RESTRICTION",
        "title": "Statutory Fisheries Restriction",
        "message_template": "Department of Fisheries statutory seasonal monsoon conservation ban active across territorial waters.",
        "source": "DEPT_FISHERIES"
    }
]

