from typing import List, Dict, Any, Optional

CANDIDATE_ZONES_DEFINITION = [
    {
        "id": "zone-a",
        "code": "ZONE A",
        "name": "North Offshore Sector (Vasai-Manori Reach)",
        "geometry_type": "Prototype / Demonstration Geometry",
        "coordinates": [
            [19.18, 72.38],
            [19.42, 72.38],
            [19.42, 72.68],
            [19.18, 72.68]
        ],
        "center": [19.30, 72.53],
        "depthMeters": "35 - 55 m",
        "distanceCoastKm": 28,
        "region": "North Maharashtra Offshore Reach"
    },
    {
        "id": "zone-b",
        "code": "ZONE B",
        "name": "Mumbai Harbor Security & Fairway Corridor",
        "geometry_type": "Prototype / Demonstration Geometry",
        "coordinates": [
            [18.86, 72.52],
            [19.08, 72.52],
            [19.08, 72.76],
            [18.86, 72.76]
        ],
        "center": [18.97, 72.64],
        "depthMeters": "18 - 32 m",
        "distanceCoastKm": 12,
        "region": "Central Mumbai Port Fairway"
    },
    {
        "id": "zone-c",
        "code": "ZONE C",
        "name": "South Coastal Offshore (Alibag-Murud Shelf)",
        "geometry_type": "Prototype / Demonstration Geometry",
        "coordinates": [
            [18.42, 72.55],
            [18.75, 72.55],
            [18.75, 72.86],
            [18.42, 72.86]
        ],
        "center": [18.58, 72.70],
        "depthMeters": "22 - 42 m",
        "distanceCoastKm": 18,
        "region": "South Maharashtra Coastal Shelf"
    },
    {
        "id": "zone-d",
        "code": "ZONE D",
        "name": "Mid-Shelf Western Transition Trench",
        "geometry_type": "Prototype / Demonstration Geometry",
        "coordinates": [
            [18.70, 72.15],
            [18.98, 72.15],
            [18.98, 72.48],
            [18.70, 72.48]
        ],
        "center": [18.84, 72.31],
        "depthMeters": "65 - 95 m",
        "distanceCoastKm": 46,
        "region": "Deep Offshore Transition Basin"
    }
]

def get_candidate_zones() -> List[Dict[str, Any]]:
    return CANDIDATE_ZONES_DEFINITION

def get_candidate_zone_by_id(zone_id: str) -> Optional[Dict[str, Any]]:
    for z in CANDIDATE_ZONES_DEFINITION:
        if z["id"].lower() == zone_id.lower():
            return z
    return None
