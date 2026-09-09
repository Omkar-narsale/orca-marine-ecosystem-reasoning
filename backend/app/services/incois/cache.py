"""
Deterministic Query Cache for INCOIS ERDDAP Subsets.
Caches retrieved subsets by (dataset_id, variables, bbox, time_window) and flags cached records transparently.
"""

import time
import hashlib
from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord

class INCOISQueryCache:
    def __init__(self, default_ttl_seconds: int = 1800):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = default_ttl_seconds
        self.hits = 0
        self.misses = 0

    def _generate_key(
        self,
        dataset_id: str,
        variables: List[str],
        bbox: Dict[str, float],
        start_time: str,
        end_time: str
    ) -> str:
        var_sorted = ",".join(sorted(variables))
        raw = f"{dataset_id}:{var_sorted}:{bbox.get('min_lat')}:{bbox.get('max_lat')}:{bbox.get('min_lon')}:{bbox.get('max_lon')}:{start_time}:{end_time}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(
        self,
        dataset_id: str,
        variables: List[str],
        bbox: Dict[str, float],
        start_time: str,
        end_time: str
    ) -> Optional[List[NormalizedMarineRecord]]:
        key = self._generate_key(dataset_id, variables, bbox, start_time, end_time)
        item = self._store.get(key)
        if not item:
            self.misses += 1
            return None

        now = time.time()
        if now > item["expires_at"]:
            del self._store[key]
            self.misses += 1
            return None

        self.hits += 1
        cached_records: List[NormalizedMarineRecord] = item["records"]

        # Tag cached records transparently per Section 16
        marked_records = []
        for r in cached_records:
            rec_copy = r.model_copy(deep=True)
            rec_copy.data_type = "cached"
            rec_copy.metadata["cache_retrieved_at"] = item["stored_at"]
            marked_records.append(rec_copy)

        return marked_records

    def set(
        self,
        dataset_id: str,
        variables: List[str],
        bbox: Dict[str, float],
        start_time: str,
        end_time: str,
        records: List[NormalizedMarineRecord],
        ttl_seconds: Optional[int] = None
    ):
        key = self._generate_key(dataset_id, variables, bbox, start_time, end_time)
        ttl = ttl_seconds or self._ttl_seconds
        now = time.time()
        self._store[key] = {
            "records": records,
            "stored_at": time.strftime("%d %b %Y %H:%M IST"),
            "expires_at": now + ttl
        }

    def clear(self):
        self._store.clear()
        self.hits = 0
        self.misses = 0

incois_cache = INCOISQueryCache()
