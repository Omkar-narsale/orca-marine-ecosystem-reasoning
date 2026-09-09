export type ZoneStatus = 'high_risk' | 'caution' | 'suitable' | 'suitable_candidate' | 'restricted' | 'insufficient_data';

export type QueryIntent =
  | 'PFZ_DISCOVERY'
  | 'MARINE_SAFETY'
  | 'MARINE_CONDITIONS'
  | 'HAZARD_ALERT'
  | 'PRODUCTIVITY_SEARCH'
  | 'ROUTE_PLANNING'
  | 'PRODUCTIVITY_ANALYSIS'
  | 'RISK_AVOIDANCE'
  | 'GENERAL_MARINE_QUERY'
  | 'SOURCE_QUERY'
  | 'FOLLOW_UP'
  | 'COMPARISON'
  | 'WHAT_IF';

export type ActionIntent =
  | 'NONE'
  | 'SHOW_ON_MAP'
  | 'HIGHLIGHT_ON_MAP'
  | 'SHOW_DETAILS'
  | 'EXPLAIN'
  | 'SHOW_SOURCES'
  | 'COMPARE'
  | 'REFINE'
  | 'RE_RANK'
  | 'CHANGE_LOCATION'
  | 'CHANGE_TIME';

export interface MapActionCommand {
  action: 'SELECT' | 'HIGHLIGHT' | 'FIT_BOUNDS' | 'CLEAR' | 'CENTER' | 'NONE';
  target_id?: string;
  target_name?: string;
  geometry?: any;
  zoom?: number;
  center?: { lat: number; lng: number };
}

export type ResponseType =
  | 'CHAT'
  | 'MARINE_CONDITIONS'
  | 'SAFETY_ASSESSMENT'
  | 'PFZ_RESULTS'
  | 'HAZARD_ALERT'
  | 'PRODUCTIVITY_RESULTS'
  | 'PRODUCTIVITY_ANALYSIS'
  | 'ROUTE_RESULT'
  | 'RISK_MAP'
  | 'COMPARISON'
  | 'SOURCE_EXPLANATION';

export interface PFZItem {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  bearing: string;
  depth_range: string;
  advisory_date: string;
  sst_celsius: number;
  chlorophyll_mg_m3: number;
  feature_type: string;
  recommendation: string;
  confidence: string;
  source: string;
  source_url: string;
}

export interface MarineConditionsData {
  wave_height_m: number;
  wave_state: string;
  swell_height_m: number;
  swell_period_sec?: number;
  wind_speed_kts: number;
  wind_direction: string;
  wind_gust_kts?: number;
  sea_surface_temp_c: number;
  current_speed_kts: number;
  current_direction?: string;
  tide_summary: string;
  visibility_km?: number;
  operational_status?: string;
}

export interface HazardAlertItem {
  alert_id: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  valid_time: string;
  distance_km?: number;
  wind_speed_kts?: number;
  source_name: string;
  source_url: string;
}

export interface RouteOptionItem {
  route_id: string;
  name: string;
  is_recommended: boolean;
  distance_nm: number;
  distance_km: number;
  estimated_transit_hours: number;
  max_wave_height_m: number;
  avg_wind_speed_kts: number;
  hazard_flags: string[];
  hazards_summary: string;
  waypoints: [number, number][];
}

export interface ProductivityAnalysisData {
  historical_baseline_chlorophyll: string;
  current_chlorophyll: string;
  historical_sst: string;
  current_sst: string;
  timeseries: Array<{
    month: string;
    chlorophyll: number;
    sst: number;
    productivity_index: number;
  }>;
  contributing_factors: Array<{
    factor: string;
    impact: string;
    evidence: string;
  }>;
}

export interface DynamicMapConfig {
  show_map: boolean;
  center: { lat: number; lng: number };
  zoom: number;
  layers: Array<{ id: string; name: string; visible: boolean }>;
  features: Array<{
    type: string;
    id: string;
    name: string;
    coordinates: any;
    properties: Record<string, any>;
  }>;
}

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
  action_intent?: ActionIntent | string;
  target_result_id?: string;
  target_name?: string;
  map_actions?: MapActionCommand[];
  entities?: any[];
  status?: string;
  response_type?: ResponseType | string;
  location: string;
  time: string;
  summary: string;
  answer?: string;
  data?: any;
  results?: any[];
  map?: DynamicMapConfig | any;
  sources?: any[];
  warnings?: any[];
  why_reasons?: string[];
  follow_up_context?: any;
  follow_up_suggestions?: string[];
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
  decision?: any;
  claim_evidence_map?: any[];
  human_friendly?: any;
}
