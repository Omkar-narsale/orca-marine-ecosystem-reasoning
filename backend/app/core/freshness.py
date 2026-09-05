"""
Centralized Marine Data Freshness & Data Type Contract for ORCA (Phase 6).

Preserves scientific metadata:
- source
- parameter
- value
- unit
- latitude
- longitude
- observation_time
- valid_time
- retrieved_at
- data_type (OBSERVATION, FORECAST, ADVISORY, WARNING, STATIC, CACHED, UNKNOWN)
- quality
- source_url
"""

from datetime import datetime, timezone
from typing import Optional, Literal, Dict, Any

DataType = Literal[
    "OBSERVATION",
    "FORECAST",
    "ADVISORY",
    "WARNING",
    "STATIC",
    "CACHED",
    "UNKNOWN",
    # Support lowercase for backward compatibility
    "observation",
    "forecast",
    "advisory",
    "warning",
    "static",
    "cached",
    "unknown"
]

FreshnessStatus = Literal[
    "LIVE",
    "RECENT",
    "FORECAST",
    "ADVISORY",
    "WARNING",
    "CACHED",
    "STALE",
    "UNKNOWN"
]

# Freshness thresholds in seconds
MAX_OBSERVATION_AGE_SECONDS = 86400 * 2  # 48 hours for satellite/in-situ observations
MAX_FORECAST_AGE_SECONDS = 86400 * 3     # 72 hours for forecast horizons
MAX_CACHE_AGE_SECONDS = 3600 * 6         # 6 hours before cache is considered stale

def normalize_data_type(dt: str) -> str:
    """Standardizes data type string to uppercase standard."""
    dt_upper = dt.upper() if dt else "UNKNOWN"
    valid = {"OBSERVATION", "FORECAST", "ADVISORY", "WARNING", "STATIC", "CACHED", "UNKNOWN"}
    return dt_upper if dt_upper in valid else "UNKNOWN"

def parse_iso_or_custom_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
    """Parses various timestamp formats safely into a UTC datetime object."""
    if not ts_str:
        return None
    
    # Try ISO format
    try:
        clean_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception:
        pass
    
    # Try common Indian Standard Time formats e.g. '05 Sep 2026 06:00 IST'
    for fmt in ("%d %b %Y %H:%M IST", "%d %b %Y %H:%M:%S IST", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts_str.replace(" IST", ""), fmt.replace(" IST", "")).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    
    return None

def get_retrieval_age_seconds(retrieved_at_str: Optional[str]) -> Optional[float]:
    """Calculates age in seconds since data was retrieved by ORCA."""
    dt = parse_iso_or_custom_timestamp(retrieved_at_str)
    if not dt:
        return None
    now_utc = datetime.now(timezone.utc)
    return max(0.0, (now_utc - dt).total_seconds())

def get_observation_age_seconds(observation_time_str: Optional[str]) -> Optional[float]:
    """Calculates age in seconds since satellite/sensor observation was recorded."""
    dt = parse_iso_or_custom_timestamp(observation_time_str)
    if not dt:
        return None
    now_utc = datetime.now(timezone.utc)
    return max(0.0, (now_utc - dt).total_seconds())

def is_stale(
    data_type: str,
    retrieved_at: Optional[str] = None,
    observation_time: Optional[str] = None,
    max_age_seconds: Optional[float] = None
) -> bool:
    """
    Evaluates whether a marine record is stale based on its data type and timestamps.
    """
    norm_type = normalize_data_type(data_type)
    
    if norm_type == "STATIC":
        return False
        
    threshold = max_age_seconds or (
        MAX_CACHE_AGE_SECONDS if norm_type == "CACHED" else MAX_OBSERVATION_AGE_SECONDS
    )
    
    age = get_retrieval_age_seconds(retrieved_at)
    if age is not None and age > threshold:
        return True
        
    if observation_time:
        obs_age = get_observation_age_seconds(observation_time)
        if obs_age is not None and obs_age > (max_age_seconds or MAX_OBSERVATION_AGE_SECONDS):
            return True
            
    return False

def calculate_freshness_status(
    data_type: str,
    retrieved_at: Optional[str] = None,
    observation_time: Optional[str] = None,
    valid_time: Optional[str] = None
) -> FreshnessStatus:
    """
    Determines UI-facing freshness badge.
    Returns: LIVE, RECENT, FORECAST, ADVISORY, WARNING, CACHED, STALE, or UNKNOWN.
    """
    norm_type = normalize_data_type(data_type)
    
    if norm_type == "WARNING":
        return "WARNING"
    if norm_type == "ADVISORY":
        return "ADVISORY"
    if norm_type == "STATIC":
        return "LIVE"
    
    if is_stale(norm_type, retrieved_at, observation_time):
        return "STALE"
        
    if norm_type == "CACHED":
        return "CACHED"
    if norm_type == "FORECAST":
        return "FORECAST"
    if norm_type == "OBSERVATION":
        age = get_observation_age_seconds(observation_time)
        if age is not None and age <= 3600 * 12:
            return "LIVE"
        return "RECENT"
        
    return "RECENT"

def format_freshness_metadata(
    source: str,
    parameter: str,
    value: Any,
    unit: str,
    data_type: str,
    retrieved_at: str,
    valid_time: str,
    source_url: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    observation_time: Optional[str] = None,
    quality: str = "available"
) -> Dict[str, Any]:
    """Constructs a fully transparent, standard scientific metadata payload."""
    norm_type = normalize_data_type(data_type)
    freshness = calculate_freshness_status(norm_type, retrieved_at, observation_time, valid_time)
    
    return {
        "source": source,
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "latitude": latitude,
        "longitude": longitude,
        "observation_time": observation_time or retrieved_at,
        "valid_time": valid_time,
        "retrieved_at": retrieved_at,
        "data_type": norm_type,
        "freshness_status": freshness,
        "is_stale": freshness == "STALE",
        "quality": quality,
        "source_url": source_url
    }
