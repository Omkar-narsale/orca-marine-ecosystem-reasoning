"""
Temporal Aggregator for INCOIS Numerical Forecast Series.
Preserves full time-series records while providing envelope metrics (min, max, peak, trend).
"""

from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord

class TemporalAggregator:
    def compute_temporal_envelope(
        self,
        records: List[NormalizedMarineRecord],
        parameter: str
    ) -> Dict[str, Any]:
        """
        Computes temporal envelope metrics for a parameter over the forecast window.
        """
        recs = [r for r in records if r.parameter == parameter and isinstance(r.value, (int, float))]
        if not recs:
            return {
                "parameter": parameter,
                "timesteps_count": 0,
                "mean": None,
                "min": None,
                "max": None,
                "peak_timestep": None,
                "trend": "unknown"
            }

        # Sort chronologically by timestamp
        recs.sort(key=lambda r: r.timestamp)
        values = [r.value for r in recs]

        # Calculate trend between first and last half
        trend = "steady"
        if len(values) >= 2:
            diff = values[-1] - values[0]
            if diff > 0.3:
                trend = "increasing"
            elif diff < -0.3:
                trend = "decreasing"

        peak_idx = values.index(max(values))
        peak_rec = recs[peak_idx]

        return {
            "parameter": parameter,
            "unit": recs[0].unit,
            "timesteps_count": len(values),
            "mean": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "peak_value": round(max(values), 2),
            "peak_valid_time": peak_rec.valid_time,
            "trend": trend,
            "series": [{"time": r.valid_time, "value": r.value} for r in recs]
        }

temporal_aggregator = TemporalAggregator()
