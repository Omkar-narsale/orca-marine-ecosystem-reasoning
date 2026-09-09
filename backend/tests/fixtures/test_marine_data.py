"""
TEST FIXTURE ONLY - Not used in production code.
This file contains synthetic test data fixtures strictly for unit and integration tests
to verify deterministic risk calculations and ranking algorithms.
"""
from typing import List
from backend.app.schemas.marine import NormalizedMarineRecord

def get_test_marine_records() -> List[NormalizedMarineRecord]:
    """Generates standard test fixtures for pipeline verification tests."""
    return [
        # Zone A: Hazardous high waves & squalls
        NormalizedMarineRecord(
            source="INCOIS",
            source_id="INCOIS_OSF",
            parameter="significant_wave_height",
            value=3.85,
            unit="m",
            latitude=19.30,
            longitude=72.53,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://incois.gov.in/oceanservices/osfforecast.jsp"
        ),
        NormalizedMarineRecord(
            source="IMD",
            source_id="IMD_MARINE",
            parameter="surface_wind_10m",
            value=28.5,
            unit="kt",
            latitude=19.30,
            longitude=72.53,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://api.imd.gov.in/public/index.php"
        ),
        NormalizedMarineRecord(
            source="IMD",
            source_id="IMD_MARINE",
            parameter="marine_fishermen_warning",
            value="Fishermen are advised not to venture into North Maharashtra coast due to squally weather.",
            unit="bulletin_alert",
            latitude=19.30,
            longitude=72.53,
            timestamp="2026-09-10T06:00:00Z",
            data_type="warning",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://api.imd.gov.in/public/index.php"
        ),
        # Zone C: Favorable conditions + PFZ
        NormalizedMarineRecord(
            source="INCOIS",
            source_id="INCOIS_OSF",
            parameter="significant_wave_height",
            value=1.1,
            unit="m",
            latitude=18.58,
            longitude=72.70,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://incois.gov.in/oceanservices/osfforecast.jsp"
        ),
        NormalizedMarineRecord(
            source="INCOIS",
            source_id="INCOIS_PFZ",
            parameter="sea_surface_temperature",
            value=28.4,
            unit="°C",
            latitude=18.58,
            longitude=72.70,
            timestamp="2026-09-10T06:00:00Z",
            data_type="advisory",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://incois.gov.in/MarineFisheries/PfzAdvisory"
        ),
        NormalizedMarineRecord(
            source="IMD",
            source_id="IMD_MARINE",
            parameter="surface_wind_10m",
            value=12.0,
            unit="kt",
            latitude=18.58,
            longitude=72.70,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://api.imd.gov.in/public/index.php"
        ),
        # Zone D: Moderate
        NormalizedMarineRecord(
            source="INCOIS",
            source_id="INCOIS_OSF",
            parameter="significant_wave_height",
            value=1.9,
            unit="m",
            latitude=18.15,
            longitude=72.78,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://incois.gov.in/oceanservices/osfforecast.jsp"
        ),
        NormalizedMarineRecord(
            source="IMD",
            source_id="IMD_MARINE",
            parameter="surface_wind_10m",
            value=14.0,
            unit="kt",
            latitude=18.15,
            longitude=72.78,
            timestamp="2026-09-10T06:00:00Z",
            data_type="forecast",
            valid_time="10 Sep 2026 05:30 - 14:00 IST",
            retrieved_at="09 Sep 2026 14:00 IST",
            source_url="https://api.imd.gov.in/public/index.php"
        )
    ]
