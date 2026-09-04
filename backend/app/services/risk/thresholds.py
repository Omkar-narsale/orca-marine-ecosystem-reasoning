from typing import Dict, Any

# Documented & Configurable Marine Safety Thresholds
# Note: Labeled as 'Prototype Risk Thresholds' pending formal joint calibration with INCOIS/IMD standards.
MARINE_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "significant_wave_height": {
        "unit": "m",
        "description": "Significant wave height (H_s) threshold for motorized/artisanal fishing craft",
        "thresholds": {
            "low": 1.2,      # <= 1.2m: Low hazard (Calm sea state)
            "moderate": 2.0, # 1.2 - 2.0m: Moderate hazard (Caution for small craft < 12m)
            "high": 3.2,     # 2.0 - 3.2m: High hazard (Dangerous swell)
            "critical": 4.0  # > 4.0m: Critical hazard (Severe rough sea / capsize risk)
        },
        "rationale": "Indian coastal craft safety limits (Directorate General of Shipping / INCOIS criteria)",
        "configuration_status": "Configured Prototype Criteria"
    },
    "surface_wind_10m": {
        "unit": "kt",
        "description": "10-meter surface wind speed",
        "thresholds": {
            "low": 12.0,     # <= 12 kts: Gentle breeze
            "moderate": 18.0,# 12 - 18 kts: Moderate breeze
            "high": 25.0,    # 18 - 25 kts: Fresh to strong breeze
            "critical": 32.0 # > 32 kts: Gale force wind / Squall gusts
        },
        "rationale": "Beaufort Wind Scale adapted for Western Arabian Sea coastal fishing vessels",
        "configuration_status": "Configured Prototype Criteria"
    },
    "surface_current": {
        "unit": "m/s",
        "description": "Surface ocean current velocity",
        "thresholds": {
            "low": 0.4,
            "moderate": 0.8,
            "high": 1.4,
            "critical": 2.0
        },
        "rationale": "Rip current and tidal stream risk in Mumbai harbor narrows",
        "configuration_status": "Configured Prototype Criteria"
    }
}

# Configurable Risk Weights for Deterministic Scoring Formula
RISK_WEIGHTS: Dict[str, float] = {
    "wave": 0.35,     # 35% weight: Primary physical hazard for small vessels
    "wind": 0.30,     # 30% weight: Surface chop and sail/steering risk
    "warning": 0.25,  # 25% weight: Official IMD/INCOIS statutory alert
    "current": 0.10   # 10% weight: Ocean current velocity
}
