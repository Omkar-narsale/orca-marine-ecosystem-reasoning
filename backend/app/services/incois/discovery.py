"""
Dataset Discovery & Semantic Parameter Mapping for INCOIS ERDDAP.
Maps natural language and operational intents to required marine parameters and matching verified datasets.
"""

from typing import List, Dict, Any, Optional
from backend.app.services.incois.datasets import (
    INCOISDatasetMetadata,
    VERIFIED_INCOIS_DATASETS
)

INTENT_DATA_REQUIREMENTS: Dict[str, List[str]] = {
    # 1. General Sea Conditions: Wave, Current, SST
    "SEA_CONDITIONS": ["WAVE", "CURRENT", "SST"],
    "sea_conditions": ["WAVE", "CURRENT", "SST"],
    "marine_forecast": ["WAVE", "SST", "CURRENT"],

    # 2. Detailed Wave Conditions
    "WAVE_CONDITIONS": ["SIGNIFICANT_WAVE_HEIGHT", "SWELL_HEIGHT", "WAVE_PERIOD", "WAVE_DIRECTION"],
    "wave_conditions": ["SIGNIFICANT_WAVE_HEIGHT", "SWELL_HEIGHT", "WAVE_PERIOD", "WAVE_DIRECTION"],

    # 3. Comprehensive Fishing Suitability: Wave, Wind, Current, SST, Chlorophyll, PFZ
    "FISHING_SUITABILITY": ["WAVE", "WIND", "CURRENT", "SST", "CHLOROPHYLL", "PFZ", "WARNINGS", "RESTRICTIONS"],
    "fishing_suitability": ["WAVE", "WIND", "CURRENT", "SST", "CHLOROPHYLL", "PFZ", "WARNINGS", "RESTRICTIONS"],

    # 4. Marine Safety & Hazard Avoidance: Wave, Wind, Warnings, Current, Restrictions
    "MARINE_SAFETY": ["WAVE", "WIND", "WARNINGS", "CURRENT", "RESTRICTIONS"],
    "marine_safety": ["WAVE", "WIND", "WARNINGS", "CURRENT", "RESTRICTIONS"],
    "marine_hazard": ["WAVE", "WIND", "WARNINGS", "CURRENT"],
    "zone_analysis": ["WAVE", "WIND", "WARNINGS", "CURRENT", "RESTRICTIONS"],
    "risk_comparison": ["WAVE", "WIND", "WARNINGS", "RESTRICTIONS", "SST"],

    # 5. Specific Parameter Inquiries
    "SST_QUERY": ["SST"],
    "CURRENT_QUERY": ["CURRENT"],
    "CHLOROPHYLL_QUERY": ["CHLOROPHYLL"],
    "GEOFENCE_CHECK": ["RESTRICTIONS"],
    "geofence_check": ["RESTRICTIONS"]
}

# Mapping of semantic parameters to verified INCOIS ERDDAP datasets and variable subsets
PARAMETER_DATASET_MAP: Dict[str, Dict[str, Any]] = {
    "WAVE": {
        "dataset_id": "incois_ww3_regional",
        "variables": ["swh", "mwp", "mwd", "swell_height"]
    },
    "SIGNIFICANT_WAVE_HEIGHT": {
        "dataset_id": "incois_ww3_regional",
        "variables": ["swh"]
    },
    "SWELL_HEIGHT": {
        "dataset_id": "incois_ww3_regional",
        "variables": ["swell_height", "mwp"]
    },
    "WAVE_PERIOD": {
        "dataset_id": "incois_ww3_regional",
        "variables": ["mwp"]
    },
    "WAVE_DIRECTION": {
        "dataset_id": "incois_ww3_regional",
        "variables": ["mwd"]
    },
    "SST": {
        "dataset_id": "incois_sst_composite",
        "variables": ["sst", "sst_anomaly"]
    },
    "CURRENT": {
        "dataset_id": "incois_roms_hydrodynamics",
        "variables": ["u", "v", "temp"]
    },
    "CHLOROPHYLL": {
        "dataset_id": "incois_ocm_chlorophyll",
        "variables": ["chlorophyll", "kd_490"]
    },
    "PFZ": {
        "dataset_id": "incois_pfz_advisory_table",
        "variables": ["sector", "latitude", "longitude", "bearing", "distance_km", "depth_m"]
    }
}

class INCOISDiscoveryEngine:
    """
    Discovers relevant INCOIS ERDDAP datasets matching requested oceanographic parameters.
    """
    def __init__(self):
        self._dataset_registry = VERIFIED_INCOIS_DATASETS

    def get_data_requirements_for_intent(self, intent: str) -> List[str]:
        """Returns minimal required marine parameters for an intent."""
        return INTENT_DATA_REQUIREMENTS.get(intent, ["WAVE", "CURRENT", "SST"])

    def discover_datasets_for_parameters(
        self,
        parameters: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Discovers datasets and bundles compatible variables to minimize HTTP requests.
        """
        dataset_requests: Dict[str, List[str]] = {}

        for param in parameters:
            param_key = param.upper()
            if param_key in PARAMETER_DATASET_MAP:
                mapping = PARAMETER_DATASET_MAP[param_key]
                ds_id = mapping["dataset_id"]
                vars_needed = mapping["variables"]

                if ds_id not in dataset_requests:
                    dataset_requests[ds_id] = []
                for v in vars_needed:
                    if v not in dataset_requests[ds_id]:
                        dataset_requests[ds_id].append(v)

        discovered = []
        for ds_id, var_list in dataset_requests.items():
            if ds_id in self._dataset_registry:
                ds_meta = self._dataset_registry[ds_id]
                discovered.append({
                    "dataset_id": ds_id,
                    "metadata": ds_meta,
                    "variables": var_list,
                    "endpoint_type": ds_meta.endpoint_type,
                    "data_type": ds_meta.data_type,
                    "category": ds_meta.category
                })

        return discovered

    def get_dataset_metadata(self, dataset_id: str) -> Optional[INCOISDatasetMetadata]:
        return self._dataset_registry.get(dataset_id)

discovery_engine = INCOISDiscoveryEngine()
