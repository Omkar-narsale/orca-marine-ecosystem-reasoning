"""
Centralized Multi-Source Verified Dataset Registry.
Maintains strictly verified official dataset metadata for INCOIS, MOSDAC, and IMD.
Prevents hallucinated dataset IDs and invalid query dimensional configurations.
"""

from typing import Dict, List, Optional
from backend.app.schemas.query_plan import DatasetMetadata

VERIFIED_DATASET_REGISTRY: Dict[str, DatasetMetadata] = {
    # =========================================================================
    # INCOIS (Indian National Centre for Ocean Information Services)
    # =========================================================================
    "incois_ww3_regional": DatasetMetadata(
        dataset_id="incois_ww3_regional",
        source="INCOIS",
        name="INCOIS Wave Watch III Indian Ocean Regional Wave Forecast",
        parameters=["WAVE", "WAVE_CONDITIONS", "SEA_CONDITIONS", "FISHING_SUITABILITY", "MARINE_SAFETY"],
        variables=["swh", "mwp", "mwd"],
        dimensions=["time", "latitude", "longitude"],
        data_type="FORECAST",
        temporal_resolution="3-hourly (00Z, 03Z, 06Z, 09Z, 12Z, 15Z, 18Z, 21Z)",
        spatial_resolution="0.1° (~10 km regular grid)",
        coverage={"min_lat": -10.0, "max_lat": 30.0, "min_lon": 60.0, "max_lon": 100.0},
        query_interface="ERDDAP",
        verified=True,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_ww3_regional.html",
        description="Operational multi-grid WaveWatch-III hydrodynamic wave model driving significant wave height, swell height, peak period, and mean direction."
    ),
    "incois_roms_hydrodynamics": DatasetMetadata(
        dataset_id="incois_roms_hydrodynamics",
        source="INCOIS",
        name="INCOIS Regional Ocean Modeling System (ROMS) 3D Hydrodynamics",
        parameters=["CURRENT", "CURRENT_QUERY", "SEA_CONDITIONS", "FISHING_SUITABILITY"],
        variables=["u", "v", "temp", "salt"],
        dimensions=["time", "depth", "latitude", "longitude"],
        data_type="FORECAST",
        temporal_resolution="Daily 24-hr mean & 6-hourly instantaneous steps",
        spatial_resolution="0.083° (~9 km)",
        coverage={"min_lat": -10.0, "max_lat": 30.0, "min_lon": 60.0, "max_lon": 100.0},
        query_interface="ERDDAP",
        verified=True,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_roms_hydrodynamics.html",
        description="3D ROMS ocean circulation forecast providing surface and subsurface zonal (u) and meridional (v) current vectors."
    ),
    "incois_sst_composite": DatasetMetadata(
        dataset_id="incois_sst_composite",
        source="INCOIS",
        name="INCOIS Multi-Satellite Blended Sea Surface Temperature Composite",
        parameters=["SST", "SST_QUERY", "SEA_CONDITIONS", "FISHING_SUITABILITY"],
        variables=["sst", "sst_anomaly", "error"],
        dimensions=["time", "latitude", "longitude"],
        data_type="ANALYSIS",
        temporal_resolution="Daily optimal interpolation analysis",
        spatial_resolution="0.05° (~5 km high-resolution grid)",
        coverage={"min_lat": -10.0, "max_lat": 30.0, "min_lon": 60.0, "max_lon": 100.0},
        query_interface="ERDDAP",
        verified=True,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_sst_composite.html",
        description="High-resolution foundation SST analysis blending INSAT-3DR, AVHRR, MODIS, and in-situ Argo/Moored buoys."
    ),
    "incois_ocm_chlorophyll": DatasetMetadata(
        dataset_id="incois_ocm_chlorophyll",
        source="INCOIS",
        name="INCOIS Oceansat Ocean Color Monitor (OCM) Chlorophyll Composite",
        parameters=["CHLOROPHYLL", "FISHING_SUITABILITY"],
        variables=["chlorophyll", "kd_490"],
        dimensions=["time", "latitude", "longitude"],
        data_type="OBSERVATION",
        temporal_resolution="Daily cloud-masked swath mosaic",
        spatial_resolution="1 km",
        coverage={"min_lat": 0.0, "max_lat": 28.0, "min_lon": 65.0, "max_lon": 95.0},
        query_interface="ERDDAP",
        verified=True,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_ocm_chlorophyll.html",
        description="Ocean color bio-optical chlorophyll-a product derived from ISRO Oceansat-2/3 OCM sensors."
    ),
    "incois_pfz_advisory_table": DatasetMetadata(
        dataset_id="incois_pfz_advisory_table",
        source="INCOIS",
        name="INCOIS Potential Fishing Zone (PFZ) Integrated Multilingual Advisories",
        parameters=["PFZ", "FISHING_SUITABILITY", "ADVISORY"],
        variables=["sector", "bearing", "distance_km", "depth_m", "validity", "status"],
        dimensions=["time", "station_id"],
        data_type="ADVISORY",
        temporal_resolution="Multi-day advisory issuance (Monday, Wednesday, Friday)",
        spatial_resolution="Coastal fish landing centers / sector lines",
        coverage={"min_lat": 8.0, "max_lat": 23.0, "min_lon": 68.0, "max_lon": 90.0},
        query_interface="ERDDAP",
        verified=True,
        official_url="https://erddap.incois.gov.in/erddap/tabledap/incois_pfz_advisories.html",
        description="Authoritative PFZ advisories integrating ocean thermal front gradients and chlorophyll abundance."
    ),

    # =========================================================================
    # MOSDAC (ISRO Meteorological & Oceanographic Satellite Data Archival Centre)
    # =========================================================================
    "mosdac_oceansat3_ocm_chlorophyll": DatasetMetadata(
        dataset_id="O3_OCM_L3_DAILY_CHL",
        source="MOSDAC",
        name="ISRO Oceansat-3 Ocean Color Monitor Level-3 Daily Chlorophyll-a Swath",
        parameters=["CHLOROPHYLL", "FISHING_SUITABILITY"],
        variables=["chlorophyll_a", "diffuse_attenuation_coeff_490", "quality_flag"],
        dimensions=["time", "latitude", "longitude"],
        data_type="OBSERVATION",
        temporal_resolution="Daily daytime clear-sky orbital passes",
        spatial_resolution="360m / 1 km gridded product",
        coverage={"min_lat": -10.0, "max_lat": 35.0, "min_lon": 50.0, "max_lon": 105.0},
        query_interface="MOSDAC_DOWNLOAD_API",
        verified=True,
        official_url="https://mosdac.gov.in/downloadapi-manual",
        description="ISRO Level-3 processed bio-optical chlorophyll concentration used for pelagic fish habitat & phytoplankton bloom mapping."
    ),
    "mosdac_insat3dr_thermal_sst": DatasetMetadata(
        dataset_id="3R_IMG_L3C_SST_DAILY",
        source="MOSDAC",
        name="ISRO INSAT-3DR Geostationary Imager Level-3C Daily Sea Surface Temperature",
        parameters=["SST", "SST_QUERY", "SEA_CONDITIONS", "FISHING_SUITABILITY"],
        variables=["sea_surface_temperature", "brightness_temp_split_window"],
        dimensions=["time", "latitude", "longitude"],
        data_type="OBSERVATION",
        temporal_resolution="Half-hourly geostationary observations aggregated daily",
        spatial_resolution="4 km",
        coverage={"min_lat": -20.0, "max_lat": 40.0, "min_lon": 40.0, "max_lon": 120.0},
        query_interface="MOSDAC_DOWNLOAD_API",
        verified=True,
        official_url="https://mosdac.gov.in/downloadapi-manual",
        description="Geostationary thermal infrared SST retrievals capturing coastal upwelling fronts and thermal boundaries."
    ),
    "mosdac_scatsat_surface_winds": DatasetMetadata(
        dataset_id="SCAT_L3_WIND_DAILY",
        source="MOSDAC",
        name="ISRO SCATSAT-1 / Oceansat-3 Scatterometer Level-3 Daily Ocean Surface Wind Vectors",
        parameters=["WIND", "MARINE_SAFETY", "SEA_CONDITIONS"],
        variables=["wind_speed_10m", "wind_direction_10m", "wind_stress"],
        dimensions=["time", "latitude", "longitude"],
        data_type="OBSERVATION",
        temporal_resolution="Daily ascending/descending pass swath composite",
        spatial_resolution="25 km / 12.5 km swath grid",
        coverage={"min_lat": -50.0, "max_lat": 50.0, "min_lon": 30.0, "max_lon": 120.0},
        query_interface="MOSDAC_DOWNLOAD_API",
        verified=True,
        official_url="https://mosdac.gov.in/downloadapi-manual",
        description="Ku-band scatterometer equivalent neutral 10m ocean surface wind speed and vector direction."
    ),

    # =========================================================================
    # IMD (India Meteorological Department)
    # =========================================================================
    "imd_coastal_marine_bulletin": DatasetMetadata(
        dataset_id="imd_coastal_marine_bulletin",
        source="IMD",
        name="IMD Regional Coastal Weather & Marine Fishermen Warnings Bulletin",
        parameters=["WIND", "WARNINGS", "MARINE_SAFETY", "FISHING_SUITABILITY", "SEA_CONDITIONS"],
        variables=["wind_speed_knots", "wind_direction", "gusts_knots", "warning_severity", "cyclone_signal"],
        dimensions=["time", "coastal_station_id"],
        data_type="FORECAST",
        temporal_resolution="6-hourly bulletins (06:00, 12:00, 18:00, 24:00 IST)",
        spatial_resolution="Regional coastal zones (North/South Maharashtra, Gujarat, Goa, Karnataka, Kerala, Tamil Nadu, Andhra, Odisha, West Bengal)",
        coverage={"min_lat": 6.0, "max_lat": 24.0, "min_lon": 68.0, "max_lon": 94.0},
        query_interface="IMD_BULLETIN_API",
        verified=True,
        official_url="https://mausam.imd.gov.in/api_reference.html",
        description="Official statutory coastal marine warning bulletins advising fishermen regarding squally weather, rough seas, and port signals."
    ),
    "imd_station_marine_forecast": DatasetMetadata(
        dataset_id="imd_station_marine_forecast",
        source="IMD",
        name="IMD Coastal Meteorological Station 5-Day Marine Numerical Weather Forecast",
        parameters=["WIND", "WEATHER", "MARINE_SAFETY"],
        variables=["surface_wind_kt", "wind_dir", "air_temp_c", "visibility_km", "sea_state_code"],
        dimensions=["time", "station_id"],
        data_type="FORECAST",
        temporal_resolution="3-hourly numerical timesteps",
        spatial_resolution="Station point / 0.1° coastal mesh",
        coverage={"min_lat": 6.0, "max_lat": 24.0, "min_lon": 68.0, "max_lon": 94.0},
        query_interface="IMD_BULLETIN_API",
        verified=True,
        official_url="https://mausam.imd.gov.in/api_reference.html",
        description="Numerical weather prediction station forecasts providing 10m coastal wind, gust velocity, and precipitation probability."
    )
}

def get_verified_dataset(dataset_id: str) -> Optional[DatasetMetadata]:
    """Retrieves dataset metadata by exact ID."""
    return VERIFIED_DATASET_REGISTRY.get(dataset_id)

def list_all_verified_datasets(source: Optional[str] = None) -> List[DatasetMetadata]:
    """Lists all verified datasets, optionally filtered by source organization."""
    if source:
        return [ds for ds in VERIFIED_DATASET_REGISTRY.values() if ds.source.upper() == source.upper()]
    return list(VERIFIED_DATASET_REGISTRY.values())
