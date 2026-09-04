from typing import Dict, Any, List

ALERT_SEVERITIES = ["INFO", "ADVISORY", "WARNING", "CRITICAL"]

ALERT_RULES = [
    {
        "id": "HIGH_WAVE_SWELL",
        "parameter": "significant_wave_height",
        "threshold": 3.5,
        "unit": "m",
        "severity": "CRITICAL",
        "type": "MARINE_HAZARD",
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
        "type": "MARINE_HAZARD",
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
        "type": "METEOROLOGICAL_HAZARD",
        "title": "Gale Force Coastal Wind Warning",
        "message_template": "Strong sustained wind forecast ({value} kt) by IMD posing capsize hazard.",
        "source": "IMD_MARINE"
    },
    {
        "id": "SQUALL_ALERT",
        "parameter": "marine_fishermen_warning",
        "severity": "WARNING",
        "type": "STATUTORY_WARNING",
        "title": "IMD Marine Squall Alert",
        "message_template": "Active statutory fishermen bulletin issued by IMD for northern Maharashtra shelf reach.",
        "source": "IMD_MARINE"
    },
    {
        "id": "GEOFENCE_RESTRICTION",
        "parameter": "geofence_restriction",
        "severity": "WARNING",
        "type": "REGULATORY_CONSTRAINT",
        "title": "Naval / Commercial Fairway Restriction",
        "message_template": "Zone geometry intersects verified maritime Cadastre restriction boundary ({name}). Entry prohibited.",
        "source": "GIS_CADASTRE"
    }
]
