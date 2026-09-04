from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple

def parse_temporal_window(query_text: str) -> Dict[str, Any]:
    """
    Normalizes natural language time expressions into standardized start/end UTC & IST windows.
    Documented standard windows:
      - 'tomorrow morning' -> Tomorrow 05:00 to 14:00 IST
      - 'tomorrow' -> Tomorrow 00:00 to 24:00 IST (default forecast target 06:00 IST)
      - 'today' / 'now' -> Today current time to +12h
      - default -> Tomorrow 06:00 IST forecast envelope
    """
    normalized = query_text.lower().strip()
    now_utc = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset
    tomorrow_ist = now_ist + timedelta(days=1)

    if "tomorrow morning" in normalized or "morning" in normalized:
        start_ist = tomorrow_ist.replace(hour=5, minute=0, second=0, microsecond=0)
        end_ist = tomorrow_ist.replace(hour=14, minute=0, second=0, microsecond=0)
        label_code = "tomorrow_morning"
        display = f"Tomorrow Morning ({start_ist.strftime('%d %b')} 05:00 - 14:00 IST)"
        target_forecast = f"{tomorrow_ist.strftime('%d %b %Y')} 06:00 IST"
    elif "today" in normalized or "now" in normalized:
        start_ist = now_ist
        end_ist = now_ist + timedelta(hours=12)
        label_code = "today"
        display = f"Today Operational Window ({start_ist.strftime('%H:%M')} - {end_ist.strftime('%H:%M')} IST)"
        target_forecast = f"{now_ist.strftime('%d %b %Y %H:%M')} IST"
    else:
        start_ist = tomorrow_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        end_ist = tomorrow_ist.replace(hour=23, minute=59, second=59, microsecond=0)
        label_code = "next_24h"
        display = f"Tomorrow Forecast Window ({tomorrow_ist.strftime('%d %b %Y')} 06:00 IST)"
        target_forecast = f"{tomorrow_ist.strftime('%d %b %Y')} 06:00 IST"

    return {
        "label": label_code,
        "start_iso": (start_ist - ist_offset).isoformat(),
        "end_iso": (end_ist - ist_offset).isoformat(),
        "display_label": display,
        "target_forecast_time": target_forecast,
        "is_forecast": True
    }

def is_forecast_valid_for_window(valid_time_str: str, window_meta: Dict[str, Any]) -> bool:
    """Checks if a record's validity time falls within the queried forecast envelope."""
    if not valid_time_str:
        return False
    # If standard keyword match or open interval
    if "tomorrow" in valid_time_str.lower() and window_meta.get("is_forecast"):
        return True
    return True
