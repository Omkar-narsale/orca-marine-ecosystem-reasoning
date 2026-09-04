export type ZoneStatus = 'high_risk' | 'caution' | 'suitable' | 'suitable_candidate' | 'restricted' | 'insufficient_data';

export interface ZoneFactor {
  parameter: string;
  label: string;
  value: string;
  severity: string;
  description: string;
  source: string;
  source_url: string;
  valid_time: string;
  data_type: string;
}

export interface MarineZone {
  id: string;
  code: string;
  name: string;
  status: ZoneStatus;
  statusLabel: string;
  riskScore: number; // 0 to 100
  confidence: 'High' | 'Medium' | 'Low';
  coordinates: [number, number][]; // [lat, lng] array forming a polygon
  center: [number, number]; // [lat, lng]
  depthMeters: string;
  distanceCoastKm: number;
  geometry_type?: string;
  conditions: {
    waveHeight: string;
    waveState: 'Low' | 'Moderate' | 'High' | 'Rough' | string;
    windSpeed: string;
    windDirection: string;
    seaSurfaceTemp: string;
    chlorophyll: string;
    marineWarning: boolean;
    marineWarningText?: string;
    geofenceStatus: string;
    isRestricted: boolean;
  };
  reasons: string[];
  recommendation: string;
  bestTimeToVisit?: string;
  pfzAdvisoryStatus: 'Active PFZ Line' | 'Borderline Gradient' | 'No PFZ Detected' | 'Restricted' | string;
  dataSourceSummary: string;
  primarySourceId?: string;
  sourceUrl?: string;
  factors?: ZoneFactor[];
}

export interface EvidenceSource {
  id: string;
  name: string;
  shortName: string;
  organization: string;
  parameter: string;
  title: string;
  description: string;
  type: 'Forecast' | 'Observation' | 'Advisory' | 'Geospatial Cadastre';
  dataType: 'forecast' | 'observation' | 'advisory' | 'warning' | 'static';
  timestamp: string;
  validFor?: string;
  retrievedAt?: string;
  sourceUrl: string;
  status: 'Connected / Demo' | 'Active / Demo' | 'Synced / Demo';
  freshness: string;
  badgeColor?: string;
}

export interface DataFreshnessItem {
  parameter: string;
  cadence: string;
  nature: 'Forecast' | 'Observation' | 'Advisory';
  validityTime: string;
  provider: string;
  freshnessState: 'Fresh' | 'Forecast Valid' | 'Latest Available';
}

export interface AgentTraceItem {
  agentName: string;
  action: string;
  status: 'completed' | 'active' | 'partial' | 'failed' | 'queued' | string;
  agentStatus?: 'COMPLETE' | 'PARTIAL' | 'FAILED' | 'QUEUED' | 'RUNNING' | string;
  toolsUsed?: string[];
  dataCategories?: string[];
  latencyMs?: number;
  evidenceCount?: number;
  details?: string;
}

export interface EvidenceGraphNode {
  id: string;
  source_id: string;
  organization: string;
  parameter: string;
  value: any;
  unit?: string;
  data_type: 'forecast' | 'observation' | 'advisory' | 'warning' | 'static';
  valid_time: string;
  retrieved_at: string;
  source_url: string;
  citation: string;
}

export interface MarineSafetyAlert {
  alert_id: string;
  fingerprint: string;
  severity: 'CRITICAL' | 'HIGH' | 'WARNING' | 'ADVISORY' | 'INFO';
  alert_type: string;
  title: string;
  zone_id: string;
  zone_code: string;
  zone_name: string;
  message: string;
  value: string;
  source_id: string;
  source_name: string;
  source_url: string;
  valid_time: string;
  created_at: string;
  acknowledged: boolean;
}

export interface MarineBriefReport {
  report_title: string;
  generated_at: string;
  reference_id: string;
  geographic_sector: string;
  temporal_envelope: string;
  operational_summary: {
    executive_decision: string;
    avoid_sectors: any[];
    candidate_sectors: any[];
  };
  evidence_provenance: any[];
  confidence_assessment: {
    score: string;
    level: string;
    explanation: string;
  };
  scientific_limitations: string[];
  governing_disclaimer: string;
}

export interface ORCAAnalysisResult {
  query: string;
  intent: string;
  location: string;
  time: string;
  summary: string;
  zonesToAvoid: MarineZone[];
  potentialZones: MarineZone[];
  focusedZoneId?: string;
  filterMode?: 'all' | 'safe' | 'hazards' | 'restricted';
  confidenceLevel: 'High' | 'Medium' | 'Low';
  confidenceScore: number; // 0-100
  confidenceExplanation: string;
  agentTrace: AgentTraceItem[];
  keyAdvisories: string[];
  all_zones?: MarineZone[];
  executionTimeMs?: number;
  limitations?: string[];
  evidenceGraph?: EvidenceGraphNode[];
  evidence_coverage?: number;
  target_language?: string;
}

