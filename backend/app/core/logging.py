import logging
import sys
import time
from typing import Optional

# Configure standard logger
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
    error: Optional[str] = None
):
    """
    Structured logger for marine & weather data source interactions as required:
    [SOURCE] METHOD endpoint status count latency error
    """
    parts = [f"[{source_name}]", f"{method} {endpoint}"]
    if status_code is not None:
        parts.append(f"status={status_code}")
    if record_count is not None:
        parts.append(f"records={record_count}")
    if latency_ms is not None:
        parts.append(f"{latency_ms:.1f}ms")
    if error:
        parts.append(f"ERROR: {error}")
        logger.error(" ".join(parts))
    else:
        logger.info(" ".join(parts))
