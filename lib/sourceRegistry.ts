import { EvidenceSource } from '@/types/marine';

export interface AuthoritativeSourceEntry {
  id: string;
  shortName: string;
  organization: string;
  title: string;
  description: string;
  dataType: 'forecast' | 'observation' | 'advisory' | 'warning' | 'static';
  parameter: string;
  sourceUrl: string;
  validFor: string;
  retrievedAt: string;
}

export const OFFICIAL_SOURCE_REGISTRY: Record<string, AuthoritativeSourceEntry> = {
  INCOIS_OSF: {
    id: 'incois-osf',
    shortName: 'INCOIS OSF',
    organization: 'Indian National Centre for Ocean Information Services',
    title: 'High-Resolution Ocean State & Wave Forecast',
    description: 'Operational 3-day high-resolution numerical wave and swell model (Wave Watch III / ROMS) for coastal Maharashtra.',
    dataType: 'forecast',
    parameter: 'High-Resolution Wave & Swell Forecast, SST, Ocean Currents',
    sourceUrl: 'https://incois.gov.in/oceanservices/osfforecast.jsp',
    validFor: 'Forecast · Valid Tomorrow 06:00 IST',
    retrievedAt: 'Latest Cycle: 12h Numerical Run',
  },
  INCOIS_PFZ: {
    id: 'incois-pfz',
    shortName: 'INCOIS PFZ',
    organization: 'Indian National Centre for Ocean Information Services',
    title: 'Potential Fishing Zone (PFZ) Advisory System',
    description: 'Multi-satellite ocean color and thermal gradient overlay for pelagic fish congregation zones.',
    dataType: 'advisory',
    parameter: 'PFZ Thermal Front Lines & Fish Aggregation Advisories',
    sourceUrl: 'https://incois.gov.in/MarineFisheries/PfzAdvisory',
    validFor: 'Advisory · Latest Available Sector Map',
    retrievedAt: 'Daily Composite Pass',
  },
  INCOIS_ERDDAP: {
    id: 'incois-erddap',
    shortName: 'INCOIS ERDDAP',
    organization: 'Indian National Centre for Ocean Information Services',
    title: 'Operational In-Situ Ocean Buoy & ERDDAP Server',
    description: 'Standardized scientific data server providing in-situ mooring wave riders, coastal radar, and gridded sea surface metrics.',
    dataType: 'observation',
    parameter: 'In-situ Coastal Buoy & Automated Tide Telemetry',
    sourceUrl: 'https://erddap.incois.gov.in/erddap/',
    validFor: 'Observation · Real-time Mooring Feed',
    retrievedAt: 'Hourly Observation Stream',
  },
  IMD_MARINE: {
    id: 'imd-marine',
    shortName: 'IMD Marine',
    organization: 'India Meteorological Department',
    title: 'Marine Coastal Weather & Squall Warning Bulletins',
    description: 'Official coastal meteorological warnings, 10m surface wind vectors, squall lines, and fishermen storm advisories.',
    dataType: 'warning',
    parameter: 'Marine Weather Bulletins, Squall Alerts & 10m Surface Winds',
    sourceUrl: 'https://api.imd.gov.in/public/api_reference.html',
    validFor: 'Forecast · Valid Tomorrow 06:00 IST',
    retrievedAt: '6-hourly Coastal Bulletin Sync',
  },
  MOSDAC_OCEAN: {
    id: 'mosdac-ocean',
    shortName: 'MOSDAC / ISRO',
    organization: 'ISRO Meteorological and Oceanographic Satellite Data Archival Centre',
    title: 'Satellite Ocean Color & Sea Surface Temperature Products',
    description: 'Earth observation imagery from Oceansat-3 (OCM-3) and INSAT-3DR for chlorophyll-a concentration and sea surface thermal fronts.',
    dataType: 'observation',
    parameter: 'Satellite Ocean Color (Chlorophyll-a), Thermal Fronts & SST',
    sourceUrl: 'https://www.mosdac.gov.in/',
    validFor: 'Observation · Yesterday 14:30 IST Pass (Latest Product)',
    retrievedAt: 'Daily Clear-Sky Satellite Swath',
  },
  GIS_CADASTRE: {
    id: 'gis-cadastre',
    shortName: 'GIS Maritime Cadastre',
    organization: 'National Hydrographic Office / Maritime Domain Cadastre',
    title: 'National Maritime Geospatial Boundaries & Security Buffers',
    description: 'Official nautical charts, Naval anchorage boundaries, commercial traffic separation schemes (TSS), and port limits.',
    dataType: 'static',
    parameter: 'Naval Fairways, Anchorage Zones, EEZ & Marine Sanctuaries',
    sourceUrl: 'https://hydro-india.nic.in/',
    validFor: 'Verified Cadastral Baseline (Rev 2026.1)',
    retrievedAt: 'Static Cadastral Geofence Grid',
  },
};

export function getSourceById(sourceId: string): AuthoritativeSourceEntry | undefined {
  return Object.values(OFFICIAL_SOURCE_REGISTRY).find((s) => s.id === sourceId);
}
