"""
IMD Coastal Station, District, and Marine Region Registry.
Maps geographic queries to official IMD station IDs, district codes, and sea bulletin operational areas.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class IMDLocationMapping(BaseModel):
    name: str
    state: str
    station_id: str
    district_id: str
    marine_region: str
    latitude: float
    longitude: float
    coastal_zone: str

IMD_COASTAL_REGISTRY: Dict[str, IMDLocationMapping] = {
    "nagapattinam": IMDLocationMapping(
        name="Nagapattinam",
        state="Tamil Nadu",
        station_id="43347",
        district_id="TN_NAGAPATTINAM",
        marine_region="South Tamil Nadu Coast & Palk Bay",
        latitude=10.767,
        longitude=79.843,
        coastal_zone="Tamil Nadu Coastal Waters"
    ),
    "mumbai": IMDLocationMapping(
        name="Mumbai",
        state="Maharashtra",
        station_id="43003",
        district_id="MH_MUMBAI",
        marine_region="North Maharashtra Coast",
        latitude=18.970,
        longitude=72.820,
        coastal_zone="North Maharashtra Coastal Waters"
    ),
    "vasai": IMDLocationMapping(
        name="Vasai-Manori Reach",
        state="Maharashtra",
        station_id="43003",
        district_id="MH_PALGHAR",
        marine_region="North Maharashtra Coast",
        latitude=19.300,
        longitude=72.530,
        coastal_zone="North Maharashtra Coastal Waters"
    ),
    "alibag": IMDLocationMapping(
        name="Alibag-Murud",
        state="Maharashtra",
        station_id="43057",
        district_id="MH_RAIGAD",
        marine_region="South Maharashtra Coast",
        latitude=18.580,
        longitude=72.700,
        coastal_zone="South Maharashtra Coastal Waters"
    ),
    "goa": IMDLocationMapping(
        name="Panaji / Goa",
        state="Goa",
        station_id="43192",
        district_id="GA_NORTH_GOA",
        marine_region="Goa-South Maharashtra Coast",
        latitude=15.498,
        longitude=73.827,
        coastal_zone="Goa Coastal Waters"
    ),
    "kochi": IMDLocationMapping(
        name="Kochi / Cochin",
        state="Kerala",
        station_id="43351",
        district_id="KL_ERNAKULAM",
        marine_region="Kerala Coast & Lakshadweep Sea",
        latitude=9.931,
        longitude=76.267,
        coastal_zone="Kerala Coastal Waters"
    ),
    "chennai": IMDLocationMapping(
        name="Chennai",
        state="Tamil Nadu",
        station_id="43279",
        district_id="TN_CHENNAI",
        marine_region="North Tamil Nadu Coast",
        latitude=13.082,
        longitude=80.270,
        coastal_zone="North Tamil Nadu Coastal Waters"
    ),
    "visakhapatnam": IMDLocationMapping(
        name="Visakhapatnam",
        state="Andhra Pradesh",
        station_id="43149",
        district_id="AP_VISAKHAPATNAM",
        marine_region="North Andhra Pradesh Coast",
        latitude=17.686,
        longitude=83.218,
        coastal_zone="Andhra Pradesh Coastal Waters"
    ),
    "kanyakumari": IMDLocationMapping(
        name="Kanyakumari",
        state="Tamil Nadu",
        station_id="43371",
        district_id="TN_KANYAKUMARI",
        marine_region="Comorin Area & Gulf of Mannar",
        latitude=8.088,
        longitude=77.538,
        coastal_zone="South Tamil Nadu Coastal Waters"
    ),
    "mangalore": IMDLocationMapping(
        name="Mangalore",
        state="Karnataka",
        station_id="43285",
        district_id="KA_DAKSHINA_KANNADA",
        marine_region="Karnataka Coast",
        latitude=12.914,
        longitude=74.856,
        coastal_zone="Karnataka Coastal Waters"
    ),
    "paradip": IMDLocationMapping(
        name="Paradip",
        state="Odisha",
        station_id="42976",
        district_id="OR_JAGATSINGHPUR",
        marine_region="Odisha Coast & North Bay of Bengal",
        latitude=20.316,
        longitude=86.611,
        coastal_zone="Odisha Coastal Waters"
    )
}

def resolve_imd_location(location_name: str) -> Dict[str, Any]:
    """
    Deterministically resolves location string to official IMD station, district, and marine region.
    """
    norm = location_name.lower().strip()
    
    # 1. Exact or Substring Matching
    for key, mapping in IMD_COASTAL_REGISTRY.items():
        if key in norm or norm in key:
            return {
                "location_name": mapping.name,
                "state": mapping.state,
                "latitude": mapping.latitude,
                "longitude": mapping.longitude,
                "station_id": mapping.station_id,
                "district_id": mapping.district_id,
                "marine_region": mapping.marine_region,
                "coastal_zone": mapping.coastal_zone,
                "resolution_method": "IMD_COASTAL_REGISTRY_MATCH",
                "confidence": 1.0
            }

    # 2. Regional Default / Fallback
    return {
        "location_name": location_name,
        "state": "Maharashtra",
        "latitude": 18.970,
        "longitude": 72.820,
        "station_id": "43003",
        "district_id": "MH_MUMBAI",
        "marine_region": "North Maharashtra Coast",
        "coastal_zone": "North Maharashtra Coastal Waters",
        "resolution_method": "REGIONAL_COASTAL_FALLBACK",
        "confidence": 0.65
    }
