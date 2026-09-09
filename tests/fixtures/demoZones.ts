/**
 * TEST FIXTURE ONLY
 * This file is for automated frontend and backend testing fixtures.
 * It must NOT be used in the production execution path.
 */
import { MarineZone } from '@/types/marine';

export const TEST_FIXTURE_ZONES: MarineZone[] = [
  {
    id: 'fixture-zone-a',
    code: 'FIXTURE A',
    name: 'Test Northern Sector',
    status: 'high_risk',
    statusLabel: 'HIGH RISK',
    riskScore: 87,
    confidence: 'Medium',
    coordinates: [
      [19.18, 72.38],
      [19.42, 72.38],
      [19.42, 72.68],
      [19.18, 72.68],
    ],
    center: [19.30, 72.53],
    depthMeters: '35 - 55 m',
    distanceCoastKm: 28,
    conditions: {
      waveHeight: '4.1 m',
      waveState: 'Rough',
      windSpeed: '30 kt',
      windDirection: 'WSW (245°)',
      seaSurfaceTemp: '28.8 °C',
      chlorophyll: '1.8 mg/m³',
      marineWarning: true,
      marineWarningText: 'Test Warning Active',
      geofenceStatus: 'No restriction detected',
      isRestricted: false,
    },
    reasons: ['Test wave hazard 4.1m'],
    recommendation: 'Test avoid recommendation',
    bestTimeToVisit: 'Test time',
    pfzAdvisoryStatus: 'Test gradient',
    dataSourceSummary: 'Test summary',
    primarySourceId: 'test-source',
    sourceUrl: 'https://incois.gov.in',
  }
];
