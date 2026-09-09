"""
Dataset Discovery Service.
Discovers and ranks verified datasets matching structured DataRequirements across INCOIS, MOSDAC, and IMD.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.app.schemas.query_plan import DataRequirement, DatasetMetadata, LocationContext, TimeContext
from backend.app.services.discovery.registry import VERIFIED_DATASET_REGISTRY, list_all_verified_datasets

class DatasetDiscoveryService:
    """
    Evaluates DataRequirements against authoritative metadata catalogs.
    Ranks candidate datasets by source preference, parameter fidelity, spatial coverage, and query interface.
    """

    def find_datasets(
        self,
        requirement: DataRequirement,
        location: Optional[LocationContext] = None,
        time_window: Optional[TimeContext] = None
    ) -> List[Tuple[DatasetMetadata, float]]:
        """
        Finds and scores all verified datasets compatible with the given DataRequirement.
        Returns list of (DatasetMetadata, compatibility_score) sorted descending by score.
        """
        req_param = requirement.parameter.upper()
        candidates: List[Tuple[DatasetMetadata, float]] = []

        for ds_key, ds in VERIFIED_DATASET_REGISTRY.items():
            score = 0.0

            # 1. Parameter Match
            ds_params = [p.upper() for p in ds.parameters]
            if req_param in ds_params:
                score += 0.50
            elif any(req_param in p or p in req_param for p in ds_params):
                score += 0.35
            else:
                # No parameter match
                continue

            # 2. Source Preference Alignment
            if requirement.source_preference:
                pref_upper = [s.upper() for s in requirement.source_preference]
                if ds.source.upper() in pref_upper:
                    rank_idx = pref_upper.index(ds.source.upper())
                    # Highest preference gets +0.30, next +0.20, etc.
                    score += max(0.10, 0.30 - (rank_idx * 0.10))
                else:
                    score += 0.05
            else:
                # Default source weighting based on parameter specialization
                if req_param in ("CHLOROPHYLL", "OCEAN_COLOR") and ds.source == "MOSDAC":
                    score += 0.25
                elif req_param in ("WAVE", "CURRENT", "SST") and ds.source == "INCOIS":
                    score += 0.25
                elif req_param in ("WIND", "WARNINGS") and ds.source == "IMD":
                    score += 0.25
                else:
                    score += 0.15

            # 3. Spatial Coverage Verification
            if location and ds.coverage:
                cov = ds.coverage
                lat, lon = location.latitude, location.longitude
                min_lat = cov.get("min_lat", -90.0)
                max_lat = cov.get("max_lat", 90.0)
                min_lon = cov.get("min_lon", -180.0)
                max_lon = cov.get("max_lon", 180.0)

                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    score += 0.15
                else:
                    # Outside spatial bounds reduces compatibility
                    score -= 0.30

            # 4. Data Type / Purpose Match
            if requirement.purpose == "FISHING_SUITABILITY":
                if ds.data_type in ("ANALYSIS", "OBSERVATION", "ADVISORY"):
                    score += 0.05
            elif requirement.purpose in ("MARINE_SAFETY", "SEA_CONDITIONS"):
                if ds.data_type in ("FORECAST", "WARNING"):
                    score += 0.05

            # Bounded compatibility
            final_score = min(1.0, max(0.0, round(score, 3)))
            if final_score > 0.3:
                candidates.append((ds, final_score))

        # Sort descending by compatibility score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def find_best_dataset(
        self,
        requirement: DataRequirement,
        location: Optional[LocationContext] = None,
        time_window: Optional[TimeContext] = None
    ) -> Optional[DatasetMetadata]:
        """Returns the single top-ranked verified dataset for the requirement."""
        results = self.find_datasets(requirement, location, time_window)
        if results:
            return results[0][0]
        return None

discovery_service = DatasetDiscoveryService()
