"""
Official INCOIS ERDDAP Dataset Registry & Metadata Catalogue.
Contains verified metadata for INCOIS ERDDAP gridded and tabular oceanographic datasets.
Documentation: https://erddap.incois.gov.in/erddap/griddap/documentation.html
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class DatasetVariable:
    name: str
    standard_name: str
    units: str
    data_type: str = "float"
    description: str = ""

@dataclass
class INCOISDatasetMetadata:
    dataset_id: str
    title: str
    source: str = "INCOIS"
    endpoint_type: str = "griddap"  # "griddap" or "tabledap"
    category: str = "WAVE"          # WAVE, SST, CURRENT, CHLOROPHYLL, WIND, BATHYMETRY
    data_type: str = "FORECAST"      # FORECAST, OBSERVATION, ANALYSIS, ADVISORY
    variables: Dict[str, DatasetVariable] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=lambda: ["time", "latitude", "longitude"])
    min_lat: float = 0.0
    max_lat: float = 30.0
    min_lon: float = 60.0
    max_lon: float = 100.0
    temporal_resolution: str = "3-hourly"
    spatial_resolution_deg: float = 0.1
    official_url: str = "https://erddap.incois.gov.in/erddap/"
    description: str = ""

# Verified INCOIS ERDDAP Dataset Catalogue
VERIFIED_INCOIS_DATASETS: Dict[str, INCOISDatasetMetadata] = {
    # 1. High-Resolution Numerical Wave Forecast (Wave Watch III / OSF)
    "incois_ww3_regional": INCOISDatasetMetadata(
        dataset_id="incois_ww3_regional",
        title="INCOIS Wave Watch III Regional Coastal Wave Forecast",
        source="INCOIS",
        endpoint_type="griddap",
        category="WAVE",
        data_type="FORECAST",
        variables={
            "swh": DatasetVariable(
                name="swh",
                standard_name="sea_surface_wave_significant_height",
                units="m",
                description="Significant wave height of combined wind waves and swell"
            ),
            "mwp": DatasetVariable(
                name="mwp",
                standard_name="sea_surface_wave_mean_period",
                units="s",
                description="Mean wave period"
            ),
            "mwd": DatasetVariable(
                name="mwd",
                standard_name="sea_surface_wave_from_direction",
                units="degrees",
                description="Mean wave direction from true north"
            ),
            "shww": DatasetVariable(
                name="shww",
                standard_name="sea_surface_wind_wave_significant_height",
                units="m",
                description="Significant height of wind waves"
            ),
            "swell_height": DatasetVariable(
                name="swell_height",
                standard_name="sea_surface_swell_wave_significant_height",
                units="m",
                description="Significant height of swell waves"
            )
        },
        dimensions=["time", "latitude", "longitude"],
        min_lat=0.0,
        max_lat=30.0,
        min_lon=60.0,
        max_lon=100.0,
        temporal_resolution="3-hourly",
        spatial_resolution_deg=0.05,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_ww3_regional.html",
        description="High-resolution coastal WaveWatch III hydrodynamic numerical wave simulation model."
    ),

    # 2. Regional Ocean Modeling System (ROMS) Hydrodynamic Forecast
    "incois_roms_hydrodynamics": INCOISDatasetMetadata(
        dataset_id="incois_roms_hydrodynamics",
        title="INCOIS Regional Ocean Modeling System (ROMS) 3D Hydrodynamics",
        source="INCOIS",
        endpoint_type="griddap",
        category="CURRENT",
        data_type="FORECAST",
        variables={
            "u": DatasetVariable(
                name="u",
                standard_name="eastward_sea_water_velocity",
                units="m s-1",
                description="Zonal eastward surface current velocity"
            ),
            "v": DatasetVariable(
                name="v",
                standard_name="northward_sea_water_velocity",
                units="m s-1",
                description="Meridional northward surface current velocity"
            ),
            "temp": DatasetVariable(
                name="temp",
                standard_name="sea_water_potential_temperature",
                units="degree_C",
                description="Potential sea surface temperature from 3D ocean model"
            ),
            "salinity": DatasetVariable(
                name="salinity",
                standard_name="sea_water_salinity",
                units="PSU",
                description="Sea water practical salinity"
            )
        },
        dimensions=["time", "latitude", "longitude"],
        min_lat=0.0,
        max_lat=30.0,
        min_lon=60.0,
        max_lon=100.0,
        temporal_resolution="6-hourly",
        spatial_resolution_deg=0.08,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_roms_hydrodynamics.html",
        description="3D hydrodynamic state of coastal waters for currents, SST, and salinity."
    ),

    # 3. High-Resolution Multi-Satellite Blended Sea Surface Temperature (SST)
    "incois_sst_composite": INCOISDatasetMetadata(
        dataset_id="incois_sst_composite",
        title="INCOIS Multi-Satellite Daily High-Resolution Sea Surface Temperature",
        source="INCOIS",
        endpoint_type="griddap",
        category="SST",
        data_type="ANALYSIS",
        variables={
            "sst": DatasetVariable(
                name="sst",
                standard_name="sea_surface_temperature",
                units="degree_C",
                description="Daily optimal interpolation blended satellite sea surface temperature"
            ),
            "sst_anomaly": DatasetVariable(
                name="sst_anomaly",
                standard_name="sea_surface_temperature_anomaly",
                units="degree_C",
                description="Daily SST departure from climatological baseline"
            )
        },
        dimensions=["time", "latitude", "longitude"],
        min_lat=-10.0,
        max_lat=35.0,
        min_lon=40.0,
        max_lon=110.0,
        temporal_resolution="daily",
        spatial_resolution_deg=0.05,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_sst_composite.html",
        description="Merged satellite IR/Microwave and in-situ thermal front composite product."
    ),

    # 4. Ocean Colour & Chlorophyll-a Satellite Observation Product
    "incois_ocm_chlorophyll": INCOISDatasetMetadata(
        dataset_id="incois_ocm_chlorophyll",
        title="INCOIS Ocean Colour Monitor Daily Chlorophyll-a Concentration",
        source="INCOIS",
        endpoint_type="griddap",
        category="CHLOROPHYLL",
        data_type="OBSERVATION",
        variables={
            "chlorophyll": DatasetVariable(
                name="chlorophyll",
                standard_name="mass_concentration_of_chlorophyll_a_in_sea_water",
                units="mg m-3",
                description="Surface chlorophyll-a pigment concentration for pelagic productivity"
            ),
            "kd_490": DatasetVariable(
                name="kd_490",
                standard_name="diffuse_attenuation_coefficient_of_downwelling_radiative_flux",
                units="m-1",
                description="Water optical clarity / turbidity metric"
            )
        },
        dimensions=["time", "latitude", "longitude"],
        min_lat=0.0,
        max_lat=30.0,
        min_lon=60.0,
        max_lon=100.0,
        temporal_resolution="daily",
        spatial_resolution_deg=0.04,
        official_url="https://erddap.incois.gov.in/erddap/griddap/incois_ocm_chlorophyll.html",
        description="Satellite optical radiometry observation for marine biological productivity."
    ),

    # 5. Potential Fishing Zone (PFZ) Thermal Front Advisory Products
    "incois_pfz_advisory_table": INCOISDatasetMetadata(
        dataset_id="incois_pfz_advisory_table",
        title="INCOIS Potential Fishing Zone (PFZ) Multilingual Advisory Bulletins",
        source="INCOIS",
        endpoint_type="tabledap",
        category="ADVISORY",
        data_type="ADVISORY",
        variables={
            "sector": DatasetVariable(name="sector", standard_name="sector_name", units="text"),
            "latitude": DatasetVariable(name="latitude", standard_name="latitude", units="degrees_north"),
            "longitude": DatasetVariable(name="longitude", standard_name="longitude", units="degrees_east"),
            "bearing": DatasetVariable(name="bearing", standard_name="bearing_compass", units="degrees"),
            "distance_km": DatasetVariable(name="distance_km", standard_name="distance_from_landing_centre", units="km"),
            "depth_m": DatasetVariable(name="depth_m", standard_name="bathymetry_depth", units="m"),
            "valid_date": DatasetVariable(name="valid_date", standard_name="advisory_validity_date", units="text")
        },
        dimensions=["time", "latitude", "longitude"],
        min_lat=0.0,
        max_lat=30.0,
        min_lon=60.0,
        max_lon=100.0,
        temporal_resolution="daily",
        spatial_resolution_deg=0.0,
        official_url="https://erddap.incois.gov.in/erddap/tabledap/incois_pfz_advisory_table.html",
        description="Daily operational PFZ advisory lines derived from integrated thermal fronts and chlorophyll gradients."
    )
}
