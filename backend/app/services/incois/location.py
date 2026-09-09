"""
Coastal Location & Marine Bounding Box Resolution Engine for INCOIS.
Resolves arbitrary Indian coastal points of interest into coordinates and builds dynamic marine bounding boxes.
"""

import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ResolvedLocation:
    name: str
    latitude: float
    longitude: float
    state: str
    coast: str  # "West Coast" (Arabian Sea) or "East Coast" (Bay of Bengal)
    confidence: float
    source: str = "ORCA_COASTAL_CADASTRE"
    marine_bearing: str = "W"  # Seaward orientation (W for West Coast, E for East Coast, S for South)

# Comprehensive coastal registry of Indian maritime landing centres, ports, and operational sectors
COASTAL_LOCATION_REGISTRY: Dict[str, ResolvedLocation] = {
    # Tamil Nadu / Bay of Bengal
    "nagapattinam": ResolvedLocation(
        name="Nagapattinam Coastal Shelf",
        latitude=10.765,
        longitude=79.843,
        state="Tamil Nadu",
        coast="East Coast",
        confidence=0.98,
        marine_bearing="E"
    ),
    "chennai": ResolvedLocation(
        name="Chennai Coastal Shelf",
        latitude=13.082,
        longitude=80.270,
        state="Tamil Nadu",
        coast="East Coast",
        confidence=0.98,
        marine_bearing="E"
    ),
    "cuddalore": ResolvedLocation(
        name="Cuddalore Coastal Sector",
        latitude=11.748,
        longitude=79.771,
        state="Tamil Nadu",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="E"
    ),
    "tuticorin": ResolvedLocation(
        name="Thoothukudi (Tuticorin) Gulf Sector",
        latitude=8.764,
        longitude=78.134,
        state="Tamil Nadu",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="SE"
    ),
    "kanyakumari": ResolvedLocation(
        name="Kanyakumari Ocean Confluence",
        latitude=8.088,
        longitude=77.538,
        state="Tamil Nadu",
        coast="South Confluence",
        confidence=0.98,
        marine_bearing="S"
    ),
    "puducherry": ResolvedLocation(
        name="Puducherry Coastal Shelf",
        latitude=11.941,
        longitude=79.808,
        state="Puducherry",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="E"
    ),
    "pondicherry": ResolvedLocation(
        name="Puducherry Coastal Shelf",
        latitude=11.941,
        longitude=79.808,
        state="Puducherry",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="E"
    ),

    # Maharashtra / Arabian Sea
    "mumbai": ResolvedLocation(
        name="Mumbai Coastal Continental Shelf",
        latitude=18.922,
        longitude=72.834,
        state="Maharashtra",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="W"
    ),
    "alibag": ResolvedLocation(
        name="Alibag-Murud Coastal Reach",
        latitude=18.641,
        longitude=72.872,
        state="Maharashtra",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),
    "vasai": ResolvedLocation(
        name="Vasai-Manori Reach (Zone A Sector)",
        latitude=19.331,
        longitude=72.775,
        state="Maharashtra",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),
    "ratnagiri": ResolvedLocation(
        name="Ratnagiri Coastal Shelf",
        latitude=16.990,
        longitude=73.300,
        state="Maharashtra",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),
    "dahanu": ResolvedLocation(
        name="Dahanu Coastal Sector",
        latitude=19.970,
        longitude=72.730,
        state="Maharashtra",
        coast="West Coast",
        confidence=0.92,
        marine_bearing="W"
    ),

    # Goa / Arabian Sea
    "goa": ResolvedLocation(
        name="Goa Coastal Marine Waters",
        latitude=15.299,
        longitude=73.980,
        state="Goa",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="W"
    ),
    "panaji": ResolvedLocation(
        name="Panaji-Mormugao Marine Shelf",
        latitude=15.498,
        longitude=73.827,
        state="Goa",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),

    # Kerala / Arabian Sea
    "kochi": ResolvedLocation(
        name="Kochi Coastal Waters",
        latitude=9.931,
        longitude=76.267,
        state="Kerala",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="W"
    ),
    "cochin": ResolvedLocation(
        name="Kochi Coastal Waters",
        latitude=9.931,
        longitude=76.267,
        state="Kerala",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="W"
    ),
    "kollam": ResolvedLocation(
        name="Kollam Coastal Shelf",
        latitude=8.893,
        longitude=76.614,
        state="Kerala",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),
    "kozhikode": ResolvedLocation(
        name="Kozhikode (Calicut) Coastal Sector",
        latitude=11.258,
        longitude=75.780,
        state="Kerala",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),

    # Karnataka / Arabian Sea
    "mangalore": ResolvedLocation(
        name="Mangalore Coastal Continental Shelf",
        latitude=12.914,
        longitude=74.856,
        state="Karnataka",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="W"
    ),
    "karwar": ResolvedLocation(
        name="Karwar Coastal Bay",
        latitude=14.818,
        longitude=74.130,
        state="Karnataka",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),

    # Gujarat / Arabian Sea
    "porbandar": ResolvedLocation(
        name="Porbandar Coastal Shelf",
        latitude=21.641,
        longitude=69.629,
        state="Gujarat",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="SW"
    ),
    "veraval": ResolvedLocation(
        name="Veraval Fishery Port Waters",
        latitude=20.900,
        longitude=70.368,
        state="Gujarat",
        coast="West Coast",
        confidence=0.98,
        marine_bearing="S"
    ),
    "okha": ResolvedLocation(
        name="Okha-Dwarka Coastal Reach",
        latitude=22.466,
        longitude=69.072,
        state="Gujarat",
        coast="West Coast",
        confidence=0.95,
        marine_bearing="W"
    ),

    # Andhra Pradesh / Bay of Bengal
    "visakhapatnam": ResolvedLocation(
        name="Visakhapatnam Deepwater Sector",
        latitude=17.686,
        longitude=83.218,
        state="Andhra Pradesh",
        coast="East Coast",
        confidence=0.98,
        marine_bearing="E"
    ),
    "vizag": ResolvedLocation(
        name="Visakhapatnam Deepwater Sector",
        latitude=17.686,
        longitude=83.218,
        state="Andhra Pradesh",
        coast="East Coast",
        confidence=0.98,
        marine_bearing="E"
    ),
    "kakinada": ResolvedLocation(
        name="Kakinada Coastal Bay",
        latitude=16.989,
        longitude=82.247,
        state="Andhra Pradesh",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="E"
    ),
    "machilipatnam": ResolvedLocation(
        name="Machilipatnam Coastal Shelf",
        latitude=16.180,
        longitude=81.130,
        state="Andhra Pradesh",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="E"
    ),

    # Odisha & West Bengal / Bay of Bengal
    "paradip": ResolvedLocation(
        name="Paradip Coastal Waters",
        latitude=20.316,
        longitude=86.611,
        state="Odisha",
        coast="East Coast",
        confidence=0.98,
        marine_bearing="SE"
    ),
    "puri": ResolvedLocation(
        name="Puri Coastal Shelf",
        latitude=19.813,
        longitude=85.831,
        state="Odisha",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="SE"
    ),
    "digha": ResolvedLocation(
        name="Digha-Shankarpur Coastal Waters",
        latitude=21.626,
        longitude=87.507,
        state="West Bengal",
        coast="East Coast",
        confidence=0.95,
        marine_bearing="S"
    )
}

def resolve_location(query: str, fallback_lat: float = 18.92, fallback_lon: float = 72.83) -> ResolvedLocation:
    """
    Resolves natural language location inquiries into a verified coastal point of interest.
    """
    q_norm = query.lower()

    for key, loc in COASTAL_LOCATION_REGISTRY.items():
        if key in q_norm:
            return loc

    # Check for state-level inquiries
    if "tamil nadu" in q_norm or "tamilnadu" in q_norm:
        return COASTAL_LOCATION_REGISTRY["nagapattinam"]
    elif "kerala" in q_norm:
        return COASTAL_LOCATION_REGISTRY["kochi"]
    elif "andhra" in q_norm:
        return COASTAL_LOCATION_REGISTRY["visakhapatnam"]
    elif "gujarat" in q_norm:
        return COASTAL_LOCATION_REGISTRY["veraval"]
    elif "odisha" in q_norm or "orissa" in q_norm:
        return COASTAL_LOCATION_REGISTRY["paradip"]
    elif "west bengal" in q_norm or "bengal" in q_norm:
        return COASTAL_LOCATION_REGISTRY["digha"]
    elif "karnataka" in q_norm:
        return COASTAL_LOCATION_REGISTRY["mangalore"]

    # Controlled Maharashtra baseline
    return COASTAL_LOCATION_REGISTRY["mumbai"]

def build_marine_bbox(
    latitude: float,
    longitude: float,
    radius_km: float = 35.0,
    marine_bearing: str = "W"
) -> Dict[str, float]:
    """
    Constructs a seaward-oriented marine bounding box for INCOIS ERDDAP subsetting.
    1 deg latitude ≈ 111.0 km
    1 deg longitude ≈ 111.0 km * cos(lat)
    """
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * max(0.2, math.cos(math.radians(latitude))))

    # Adjust bounding box seaward based on coastal orientation
    min_lat = latitude - lat_delta
    max_lat = latitude + lat_delta
    min_lon = longitude - lon_delta
    max_lon = longitude + lon_delta

    if marine_bearing == "W":
        # West Coast: extend longitude westward into Arabian Sea
        min_lon = longitude - (lon_delta * 1.5)
        max_lon = longitude + (lon_delta * 0.3)
    elif marine_bearing == "E":
        # East Coast: extend longitude eastward into Bay of Bengal
        min_lon = longitude - (lon_delta * 0.3)
        max_lon = longitude + (lon_delta * 1.5)
    elif marine_bearing == "S":
        # South Confluence: extend southward into Indian Ocean
        min_lat = latitude - (lat_delta * 1.5)
        max_lat = latitude + (lat_delta * 0.3)

    return {
        "min_lat": round(min_lat, 3),
        "max_lat": round(max_lat, 3),
        "min_lon": round(min_lon, 3),
        "max_lon": round(max_lon, 3),
        "center_lat": round(latitude, 3),
        "center_lon": round(longitude, 3),
        "radius_km": radius_km
    }

def get_radius_for_intent(intent: str) -> float:
    """Returns optimal spatial subset radius (in km) according to operational intent."""
    intent_norm = intent.lower()
    if any(w in intent_norm for w in ["fishing", "suitability", "candidate", "rank"]):
        return 50.0  # Broader regional candidate search envelope
    elif any(w in intent_norm for w in ["regional", "overview", "forecast"]):
        return 45.0
    elif any(w in intent_norm for w in ["hazard", "warning", "avoid"]):
        return 35.0
    else:
        return 25.0  # High-resolution local conditions
