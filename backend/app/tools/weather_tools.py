from typing import List, Dict, Any, Optional
from backend.app.tools.base import BaseTool
from backend.app.services.imd.client import imd_connector
from backend.app.schemas.marine import NormalizedMarineRecord

class CoastalWindsTool(BaseTool):
    name = "get_coastal_winds"
    description = "Retrieves surface wind speed (10m) and gale gust forecasts for coastal Maharashtra sectors from IMD."

    async def _run(self, **kwargs) -> tuple[List[NormalizedMarineRecord], List[str]]:
        records = await imd_connector.get_data()
        wind_recs = [r for r in records if r.parameter in ("surface_wind_10m", "surface_wind_gusts")]
        evidence_ids = [f"ev_imd_wind_{i+1}" for i, _ in enumerate(wind_recs)]
        return wind_recs, evidence_ids

class MarineWarningsTool(BaseTool):
    name = "get_marine_warnings"
    description = "Retrieves active statutory fishermen warnings, squall line alerts, and cyclone advisories from IMD."

    async def _run(self, **kwargs) -> tuple[List[NormalizedMarineRecord], List[str]]:
        records = await imd_connector.get_data()
        warn_recs = [r for r in records if r.data_type == "warning" or "warning" in r.parameter]
        evidence_ids = [f"ev_imd_warning_{i+1}" for i, _ in enumerate(warn_recs)]
        return warn_recs, evidence_ids

coastal_winds_tool = CoastalWindsTool()
marine_warnings_tool = MarineWarningsTool()
