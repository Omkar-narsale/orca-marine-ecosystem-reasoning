"""
ORCA Request / Trace ID & Performance Measurement Module (Phase 6).

Generates traceable request IDs: ORCA-YYYYMMDD-XXXX
Propagates request context across Planner -> Agents -> Tools -> Risk Engine -> Synthesis.
"""

import uuid
import contextvars
from datetime import datetime
from typing import Optional, Dict, Any

# ContextVar for tracing the active request ID in async task flows
current_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_request_id", default=None
)

def generate_request_id(prefix: str = "ORCA") -> str:
    """Generates standard traceable request ID: ORCA-YYYYMMDD-XXXX."""
    date_part = datetime.now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_part}-{short_uuid}"

def set_current_request_id(request_id: Optional[str] = None) -> str:
    """Sets or creates the current active trace ID in the async context."""
    req_id = request_id or generate_request_id()
    current_request_id_var.set(req_id)
    return req_id

def get_current_request_id() -> str:
    """Retrieves the current trace ID or generates a default."""
    req_id = current_request_id_var.get()
    if not req_id:
        req_id = generate_request_id()
        current_request_id_var.set(req_id)
    return req_id
