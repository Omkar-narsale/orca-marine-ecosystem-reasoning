# ORCA Data Source Registry & Ingestion Contract

**System**: ORCA Marine Intelligence Platform  
**Phase**: Phase 6 — Authoritative Grounding & Freshness Contract

---

## 1. Authoritative Data Sources

ORCA integrates four official, scientific, and statutory data providers:

### 1.1 INCOIS (Indian National Centre for Ocean Information Services)
- **Authority**: Ministry of Earth Sciences (MoES), Government of India
- **Products**:
  - Significant Wave Height ($H_s$, meters)
  - Wave Period ($T_p$, seconds)
  - Sea Surface Temperature (SST, °C)
  - Potential Fishing Zone (PFZ) Advisories (Thermal Fronts)
- **Underlying Numerical Models**: Wave Watch III, ROMS Coastal Hydrodynamics
- **Nominal Update Cadence**: 12-hourly numerical forecast cycles
- **Official URL**: [https://incois.gov.in](https://incois.gov.in)
- **ERDDAP Server**: `https://erddap.incois.gov.in/erddap`

### 1.2 IMD (India Meteorological Department)
- **Authority**: Ministry of Earth Sciences (MoES), Government of India
- **Products**:
  - 10m Surface Wind Speed (knots) and Direction
  - Squall and Gale Warnings
  - Coastal Fishermen Bulletins
  - Cyclone Bulletins
- **Nominal Update Cadence**: 6-hourly bulletins, 3-hourly synoptic alerts
- **Official URL**: [https://api.imd.gov.in/public](https://api.imd.gov.in/public)

### 1.3 MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre)
- **Authority**: Space Applications Centre (SAC), ISRO
- **Products**:
  - Chlorophyll-a Concentration ($\text{mg/m}^3$)
  - Ocean Color Swath Data (Oceansat-3 OCM-3)
- **Nominal Cadence**: Daily clear-sky satellite pass observations
- **Official URL**: [https://www.mosdac.gov.in](https://www.mosdac.gov.in)

### 1.4 GIS Maritime Cadastre & Hydrographic Office
- **Authority**: National Hydrographic Office / Directorate General of Shipping
- **Products**:
  - Naval Anchorage Security Envelopes
  - Vessel Traffic Separation Scheme (TSS) Fairways
  - Marine Protected Sanctuaries (e.g. Malvan Reef)
- **Baseline**: Hydrographic Revision 2026.1
- **Official URL**: [https://hydro-india.nic.in](https://hydro-india.nic.in)

---

## 2. Centralized Freshness & Data Type Schema

Every marine telemetry record in ORCA is normalized with the following standardized fields:

```json
{
  "source": "INCOIS",
  "source_id": "INCOIS_OSF",
  "parameter": "significant_wave_height",
  "value": 4.1,
  "unit": "m",
  "latitude": 19.30,
  "longitude": 72.53,
  "timestamp": "2026-09-05T06:00:00Z",
  "observation_time": "2026-09-05T06:00:00Z",
  "valid_time": "Forecast · Valid Tomorrow 06:00 IST",
  "retrieved_at": "05 Sep 2026 06:00 IST",
  "data_type": "FORECAST",
  "quality": "available",
  "source_url": "https://incois.gov.in/oceanservices/osfforecast.jsp"
}
```

### Supported Data Types:
- `OBSERVATION`: Satellite sensor passes or in-situ buoy telemetry.
- `FORECAST`: Numerical model forecast field.
- `ADVISORY`: Statutory advisory (e.g. PFZ front).
- `WARNING`: Statutory storm/squall alert.
- `STATIC`: Regulatory cadastral geometry boundary.
- `CACHED`: Persisted record from past retrieval cycle.
- `UNKNOWN`: Unverified or missing telemetry.

---

## 3. Scientific Integrity & Data Policy

- **No Synthetic Hallucination**: If telemetry from a source is unreachable, ORCA returns `INSUFFICIENT_DATA` or `UNKNOWN`. It never fabricates wave heights or wind speeds.
- **Cache Transparency**: Cached fallback records are explicitly marked `CACHED` and never disguised as real-time observations.
- **Non-Guarantee Clause**: PFZ chlorophyll and thermal indicators represent biological probability fronts, not guarantees of harvestable fish presence.
