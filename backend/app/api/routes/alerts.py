from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List
from backend.app.services.alerts.alert_manager import alert_manager

router = APIRouter(prefix="/alerts", tags=["Proactive Marine Safety Alerts"])

@router.get("", summary="Get all active proactive marine safety alerts")
async def get_active_alerts():
    """Returns active deduplicated alerts from INCOIS wave swell, IMD winds/squalls, and GIS Cadastre."""
    alerts = await alert_manager.get_active_alerts()
    unread_count = alert_manager.get_unread_count()
    return {
        "active_alerts_count": len(alerts),
        "unread_count": unread_count,
        "alerts": alerts
    }

@router.post("/evaluate", summary="Force re-evaluation of safety alerts")
async def evaluate_safety_alerts():
    """Forces fresh telemetry pull and re-evaluates deterministic alert rules."""
    alerts = await alert_manager.refresh_alerts()
    return {
        "status": "success",
        "evaluated_alerts": len(alerts),
        "alerts": alerts
    }

@router.post("/{alert_id}/acknowledge", summary="Mark a safety alert as acknowledged / read")
async def acknowledge_alert(alert_id: str = Path(..., description="Alert ID to acknowledge")):
    """Acknowledges an alert by ID."""
    success = alert_manager.acknowledge_alert(alert_id)
    if not success:
        return {"status": "not_found", "message": f"Alert {alert_id} not currently in active cache, but marked as acknowledged."}
    return {"status": "success", "alert_id": alert_id, "acknowledged": True}
