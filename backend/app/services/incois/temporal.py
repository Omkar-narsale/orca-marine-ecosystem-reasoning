"""
Temporal Resolver for INCOIS ERDDAP Query Subsetting.
Converts natural language temporal inquiries into ISO-8601 UTC timestamps and Indian Standard Time (IST) operational envelopes.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass

IST_OFFSET = timedelta(hours=5, minutes=30)

@dataclass
class ResolvedTimeWindow:
    start_utc: str
    end_utc: str
    start_ist: str
    end_ist: str
    display_label: str
    timezone: str = "Asia/Kolkata"
    source_expression: str = "tomorrow morning"
    duration_hours: float = 6.0

def resolve_time_window(expression: str, reference_time_utc: Optional[datetime] = None) -> ResolvedTimeWindow:
    """
    Parses natural language time expressions into valid ERDDAP UTC bounds and operational IST labels.
    """
    now_utc = reference_time_utc or datetime.now(timezone.utc)
    now_ist = now_utc + IST_OFFSET
    q = expression.lower().strip()

    # Target date calculation (Today vs Tomorrow vs Specific)
    is_tomorrow = "tomorrow" in q or "कल" in q or "उद्या" in q
    is_morning = any(w in q for w in ["morning", "dawn", "06:00", "सुबह", "सकाळी"])
    is_evening = any(w in q for w in ["evening", "dusk", "night", "शाम", "संध्याकाळी"])
    is_afternoon = any(w in q for w in ["afternoon", "noon", "दुपारी", "दोपहर"])
    is_next_hours = "next" in q or "hours" in q or "hour" in q

    target_date_ist = (now_ist + timedelta(days=1)).date() if is_tomorrow else now_ist.date()

    if is_morning:
        start_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=5, minute=0)
        end_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=13, minute=0)
        label = f"{'Tomorrow' if is_tomorrow else 'Today'} Morning (05:00 - 13:00 IST)"
    elif is_evening:
        start_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=15, minute=0)
        end_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=22, minute=0)
        label = f"{'Tomorrow' if is_tomorrow else 'Today'} Evening (15:00 - 22:00 IST)"
    elif is_afternoon:
        start_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=12, minute=0)
        end_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=17, minute=0)
        label = f"{'Tomorrow' if is_tomorrow else 'Today'} Afternoon (12:00 - 17:00 IST)"
    elif is_next_hours:
        # Extract number of hours if present
        import re
        match = re.search(r'(\d+)\s*hour', q)
        hours = int(match.group(1)) if match else 6
        start_ist_dt = now_ist
        end_ist_dt = now_ist + timedelta(hours=hours)
        label = f"Next {hours} Hours ({start_ist_dt.strftime('%H:%M')} - {end_ist_dt.strftime('%H:%M')} IST)"
    elif is_tomorrow:
        start_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=0, minute=0)
        end_ist_dt = datetime.combine(target_date_ist, datetime.min.time()).replace(hour=23, minute=59)
        label = f"Tomorrow Full Day ({target_date_ist.strftime('%d %b %Y')})"
    else:
        # Default: current 6-hour operational window
        start_ist_dt = now_ist
        end_ist_dt = now_ist + timedelta(hours=6)
        label = f"Operational Window ({start_ist_dt.strftime('%H:%M')} - {end_ist_dt.strftime('%H:%M')} IST)"

    # Convert IST to UTC ISO strings for ERDDAP
    start_utc_dt = start_ist_dt - IST_OFFSET
    end_utc_dt = end_ist_dt - IST_OFFSET

    duration = (end_ist_dt - start_ist_dt).total_seconds() / 3600.0

    return ResolvedTimeWindow(
        start_utc=start_utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_utc=end_utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        start_ist=start_ist_dt.strftime("%d %b %Y %H:%M IST"),
        end_ist=end_ist_dt.strftime("%d %b %Y %H:%M IST"),
        display_label=label,
        source_expression=expression,
        duration_hours=round(duration, 1)
    )
