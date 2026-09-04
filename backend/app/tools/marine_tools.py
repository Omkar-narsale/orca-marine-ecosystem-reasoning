from typing import List, Dict, Any, Optional
from backend.app.tools.base import BaseTool
from backend.app.services.incois.client import incois_connector
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.schemas.marine import NormalizedMarineRecord

class WaveForecastTool(BaseTool):
    name = "get_wave_forecast"
    description = "Retrieves authoritative numerical significant wave height (SWH) and swell forecasts from INCOIS Wave Watch III."

    async def _run(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None
    ) -> tuple[List[NormalizedMarineRecord], List[str]]:
        records = await incois_connector.get_data(min_lat, max_lat, min_lon, max_lon)
        wave_recs = [r for r in records if r.parameter in ("significant_wave_height", "wave_swell_height", "surface_current")]
        evidence_ids = [f"ev_incois_wave_{i+1}" for i, _ in enumerate(wave_recs)]
        return wave_recs, evidence_ids

class SeaSurfaceTempTool(BaseTool):
    name = "get_sst"
    description = "Retrieves sea surface temperature (SST) forecasts and satellite thermal observations from INCOIS and MOSDAC."

    async def _run(self, **kwargs) -> tuple[List[NormalizedMarineRecord], List[str]]:
        incois_recs = await incois_connector.get_data()
        mosdac_recs = await mosdac_connector.get_data()
        sst_recs = [r for r in (incois_recs + mosdac_recs) if r.parameter in ("sea_surface_temperature", "sea_surface_temp")]
        evidence_ids = [f"ev_sst_{i+1}" for i, _ in enumerate(sst_recs)]
        return sst_recs, evidence_ids

class PFZAdvisoryTool(BaseTool):
    name = "get_pfz_advisories"
    description = "Retrieves latest Potential Fishing Zone (PFZ) advisory sectors and oceanic thermal front composites from INCOIS."

    async def _run(self, **kwargs) -> tuple[List[NormalizedMarineRecord], List[str]]:
        records = await incois_connector.get_data()
        pfz_recs = [r for r in records if r.data_type == "advisory" or "fishing" in r.parameter]
        evidence_ids = [f"ev_incois_pfz_{i+1}" for i, _ in enumerate(pfz_recs)]
        return pfz_recs, evidence_ids

class ChlorophyllObservationTool(BaseTool):
    name = "get_chlorophyll_observations"
    description = "Retrieves latest Ocean Colour Monitor (OCM-3) chlorophyll-a concentration observations from MOSDAC / ISRO."

    async def _run(self, **kwargs) -> tuple[List[NormalizedMarineRecord], List[str]]:
        records = await mosdac_connector.get_data()
        chloro_recs = [r for r in records if "chlorophyll" in r.parameter]
        evidence_ids = [f"ev_mosdac_chloro_{i+1}" for i, _ in enumerate(chloro_recs)]
        return chloro_recs, evidence_ids

wave_forecast_tool = WaveForecastTool()
sst_tool = SeaSurfaceTempTool()
pfz_advisory_tool = PFZAdvisoryTool()
chlorophyll_tool = ChlorophyllObservationTool()
