"""
Structured Application Logging for ORCA Marine Intelligence (Phase 6).

Features:
- Structured JSON and standard log formats
- Automatic request_id trace injection
- Log levels: DEBUG, INFO, WARNING, ERROR
- Credential & sensitive token redaction
- Tool & connector execution metric logging
"""

import logging
import sys
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from backend.app.core.tracing import get_current_request_id

# Sensitive keys to redact
SENSITIVE_KEYS = {"api_key", "password", "token", "secret", "authorization", "llm_api_key"}

def sanitize_data(data: Any) -> Any:
    """Recursively redacts sensitive credentials from logs."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in SENSITIVE_KEYS):
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or get_current_request_id()
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(sanitize_data(record.extra_data))
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Configure logger
logger = logging.getLogger("orca.marine")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_source_request(
    source_name: str,
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    record_count: Optional[int] = None,
    latency_ms: Optional[float] = None,
    error: Optional[str] = None,
    request_id: Optional[str] = None,
    operation: Optional[str] = None,
    cache_hit: bool = False,
    conversation_id: Optional[str] = None
):
    """
    Structured logger for marine & weather data source interactions.
    Outputs development-observable multi-line structured block:
    [ORCA][SOURCE]
    trace=...
    operation=...
    status=...
    latency=...ms
    records=...
    cache_hit=false
    """
    req_id = request_id or get_current_request_id()
    op_name = operation or method
    
    if cache_hit:
        msg = f"[ORCA][{source_name}]\ntrace={req_id}\noperation={op_name}\ncache_hit=true"
        logger.info(msg)
        return

    parts = [f"[ORCA][{source_name}]", f"trace={req_id}", f"operation={op_name}"]
    if conversation_id:
        parts.append(f"conversation={conversation_id}")
    if status_code is not None:
        parts.append(f"status={status_code}")
    if latency_ms is not None:
        parts.append(f"latency={int(latency_ms)}ms")
    if record_count is not None:
        parts.append(f"records={record_count}")
    parts.append("cache_hit=false")
    if error:
        parts.append(f"error={error}")
        
    logger.info("\n".join(parts))

def log_orca_request(
    conversation_id: str,
    intent: str,
    location_source: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    trace_id: Optional[str] = None
):
    """Logs incoming user request context."""
    req_id = trace_id or get_current_request_id()
    lat_str = f"{lat:.4f}" if lat is not None else "None"
    lon_str = f"{lon:.4f}" if lon is not None else "None"
    msg = (
        f"[ORCA REQUEST]\n"
        f"trace={req_id}\n"
        f"conversation={conversation_id}\n"
        f"intent={intent}\n"
        f"location_source={location_source}\n"
        f"lat={lat_str}\n"
        f"lon={lon_str}"
    )
    logger.info(msg)

def log_orca_result(
    intent: str,
    sources: list,
    status: str = "SUCCESS",
    trace_id: Optional[str] = None
):
    """Logs synthesis result summary."""
    req_id = trace_id or get_current_request_id()
    s_names = []
    if sources:
        for s in sources:
            if isinstance(s, dict):
                s_names.append(s.get("org") or s.get("source") or s.get("name") or "SOURCE")
            else:
                s_names.append(str(s))
    sources_str = ",".join(s_names) if s_names else "NONE"
    msg = (
        f"[ORCA RESULT]\n"
        f"trace={req_id}\n"
        f"intent={intent}\n"
        f"sources={sources_str}\n"
        f"status={status}"
    )
    logger.info(msg)

def log_orca_db(
    conversation_id: str,
    message_saved: bool = True,
    result_saved: bool = True,
    trace_id: Optional[str] = None
):
    """Logs conversation database persistence without sensitive information."""
    req_id = trace_id or get_current_request_id()
    msg = (
        f"[ORCA][DB]\n"
        f"trace={req_id}\n"
        f"conversation={conversation_id}\n"
        f"message_saved={str(message_saved).lower()}\n"
        f"result_saved={str(result_saved).lower()}"
    )
    logger.info(msg)

def log_agent_execution(
    agent_name: str,
    action: str,
    status: str,
    latency_ms: float,
    request_id: Optional[str] = None,
    tools_used: Optional[list] = None
):
    """Logs agent execution lifecycle with structured metrics."""
    req_id = request_id or get_current_request_id()
    tools_str = f" tools={','.join(tools_used)}" if tools_used else ""
    logger.info(f"[{req_id}] [AGENT:{agent_name}] status={status} latency={latency_ms:.1f}ms action='{action}'{tools_str}")

def log_tool_execution(
    tool_name: str,
    source: str,
    status: str,
    latency_ms: float,
    request_id: Optional[str] = None,
    error: Optional[str] = None
):
    """Logs tool execution lifecycle with latency and error categories."""
    req_id = request_id or get_current_request_id()
    err_str = f" error='{error}'" if error else ""
    if status == "success":
        logger.info(f"[{req_id}] [TOOL:{tool_name}] source={source} status={status} latency={latency_ms:.1f}ms")
    else:
        logger.warning(f"[{req_id}] [TOOL:{tool_name}] source={source} status={status} latency={latency_ms:.1f}ms{err_str}")

