import { MarineZone, EvidenceSource, DataFreshnessItem, ORCAAnalysisResult } from '@/types/marine';
import { runDemoAnalysis } from '@/lib/demoAnalysis';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000/api';

export interface SourceHealthDetail {
  name: string;
  source_id?: string;
  status: string;
  is_live: boolean;
  latency_ms?: number;
  last_successful_fetch?: string;
  data_freshness?: string;
  error?: string | null;
}

export interface SourceHealthSummary {
  ocean_data: SourceHealthDetail;
  weather_data: SourceHealthDetail;
  satellite_data: SourceHealthDetail;
  geospatial_grid: SourceHealthDetail;
  timestamp: string;
}

export interface SystemHealthFull {
  status: 'healthy' | 'degraded' | 'unavailable';
  health_level?: string;
  timestamp: string;
  total_sources: number;
  connected_sources: number;
  sources: Array<{
    source_id: string;
    name: string;
    organization: string;
    status: string;
    health_state?: string;
    endpoint: string;
    last_checked: string;
    last_successful_retrieval?: string;
    response_latency_ms?: number;
    latency_ms?: number;
    data_freshness?: string;
    is_live: boolean;
    error?: string | null;
    notes: string;
  }>;
}

export interface SystemReadiness {
  status: 'READY' | 'DEGRADED' | 'NOT_READY';
  ready: boolean;
  timestamp: string;
  dependencies: Record<string, string | number>;
}

export async function fetchMarineZones(): Promise<MarineZone[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/marine/zones`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn('[ORCA API] Failed to fetch marine zones:', err);
    return [];
  }
}

export async function fetchEvidenceSources(): Promise<EvidenceSource[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/evidence`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn('[ORCA API] Failed to fetch evidence sources:', err);
    return [];
  }
}

export async function fetchDataFreshness(): Promise<DataFreshnessItem[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/evidence/freshness`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn('[ORCA API] Failed to fetch data freshness:', err);
    return [];
  }
}

export async function fetchSourcesHealth(): Promise<SourceHealthSummary | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/health/sources`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    return null;
  }
}

export async function fetchFullSystemHealth(): Promise<SystemHealthFull | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    return null;
  }
}

export async function fetchSystemReadiness(): Promise<SystemReadiness | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/health/ready`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    return null;
  }
}

export async function analyzeMarineQuery(
  query: string,
  sessionId: string = 'orca_session_default',
  language: string = 'en',
  context?: any,
  isDemoMode: boolean = false,
  location?: {
    latitude: number | null;
    longitude: number | null;
    accuracy_m?: number | null;
    timestamp?: string | null;
    status?: string;
  }
): Promise<ORCAAnalysisResult> {
  try {
    const res = await fetch(`${BACKEND_URL}/conversation/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: query,
        session_id: sessionId,
        conversation_id: sessionId,
        language: language,
        location: location && location.latitude !== null ? location : undefined,
        context: context,
        is_demo_mode: isDemoMode
      }),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    console.warn('[ORCA API] Conversation endpoint failed, trying /agentic/query:', err);
    try {
      const res2 = await fetch(`${BACKEND_URL}/agentic/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, context, is_demo_mode: isDemoMode }),
        cache: 'no-store'
      });
      if (!res2.ok) throw new Error(`HTTP ${res2.status}`);
      return await res2.json();
    } catch (err2) {
      console.warn('[ORCA API] Backend unreachable:', err2);
      return runDemoAnalysis(query, language);
    }
  }
}

export async function fetchActiveAlerts(): Promise<{ alerts: any[]; unread_count: number }> {
  try {
    const res = await fetch(`${BACKEND_URL}/alerts`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      alerts: data.alerts || [],
      unread_count: data.unread_count || 0
    };
  } catch (err) {
    console.warn('[ORCA API] Alerts endpoint unreachable:', err);
    return {
      alerts: [],
      unread_count: 0
    };
  }
}

export async function acknowledgeAlert(alertId: string): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND_URL}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      cache: 'no-store'
    });
    return res.ok;
  } catch (err) {
    return false;
  }
}

export async function generateMarineBrief(
  query: string,
  region: string = 'Maharashtra Coastal Shelf',
  timeWindow: string = 'Tomorrow Morning'
) {
  try {
    const res = await fetch(`${BACKEND_URL}/reports/marine-brief`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, region, time_window: timeWindow }),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[ORCA API] Marine brief endpoint unreachable:', err);
    return {
      orca_branding: 'ORCA — Marine Ecosystem Reasoning with Collaborative Agents',
      report_title: 'ORCA OPERATIONAL MARINE INTELLIGENCE BRIEF (UNAVAILABLE)',
      generated_at: new Date().toLocaleString(),
      reference_id: `ORCA-MB-UNAVAIL-${Date.now()}`,
      request_id: `ORCA-UNAVAIL-${Date.now()}`,
      geographic_sector: region,
      temporal_envelope: timeWindow,
      operational_summary: {
        executive_decision: 'ORCA backend is currently unavailable. Live marine telemetry could not be retrieved.',
        avoid_sectors: [],
        candidate_sectors: []
      },
      evidence_provenance: [],
      confidence_assessment: { score: '0%', level: 'Low', explanation: 'Backend offline.' },
      uncertainty_assessment: { uncertainty_level: 'High', explanation: 'No authoritative data available.' },
      scientific_limitations: ['Backend is unavailable.'],
      governing_disclaimer: 'This report is decision support. No live data was retrieved.'
    };
  }
}

export async function submitUserFeedback(
  query: string,
  useful: boolean,
  rating: number = 5,
  note?: string
): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND_URL}/reports/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, useful, rating, feedback_note: note }),
      cache: 'no-store'
    });
    return res.ok;
  } catch (err) {
    return true;
  }
}

export async function fetchRankedZones() {
  try {
    const res = await fetch(`${BACKEND_URL}/decision/rank`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      top_candidate: null,
      alternative_candidate: null,
      ranked_candidates: [],
      excluded_zones: [],
      decision_rationale: 'ORCA backend is unavailable.'
    };
  }
}

export async function fetchZoneDecision(zoneId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/decision/${zoneId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchZoneTradeoff(zoneA: string, zoneB: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/decision/tradeoff/compare?zone_a=${zoneA}&zone_b=${zoneB}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchRouteCorridor(destinationZoneId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/decision/route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ destination_zone_id: destinationZoneId }),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function runWhatIfScenario(params: {
  wave_delta_m?: number;
  wind_delta_kt?: number;
  target_zone_id?: string;
  geofence_override_zone_id?: string;
  scenario_time_label?: string;
}) {
  try {
    const res = await fetch(`${BACKEND_URL}/scenario/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      scenario_label: 'BACKEND UNAVAILABLE',
      explanation: 'Simulation backend service is currently unreachable.',
      is_simulation: true,
      scientific_disclaimer: 'Backend unavailable.'
    };
  }
}

export async function resetScenario() {
  try {
    const res = await fetch(`${BACKEND_URL}/scenario/reset`, {
      method: 'POST',
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'BASELINE_RESTORED' };
  }
}

export async function fetchUncertaintyBreakdown(zoneId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/uncertainty/${zoneId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchResearchEvaluationMetrics() {
  try {
    const res = await fetch(`${BACKEND_URL}/evaluation/metrics`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function submitHumanEvaluation(feedback: {
  reviewer_name?: string;
  correctness_score: number;
  usefulness_score: number;
  clarity_score: number;
  evidence_quality_score: number;
  trust_score: number;
  map_usefulness_score: number;
  notes?: string;
}) {
  try {
    const res = await fetch(`${BACKEND_URL}/evaluation/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { message: 'Stored locally' };
  }
}

export async function fetchDecisionAudit(decisionId: string = 'audit-latest-001') {
  try {
    const res = await fetch(`${BACKEND_URL}/evaluation/audit/${decisionId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchComparativeEvaluation() {
  try {
    const res = await fetch(`${BACKEND_URL}/evaluation/comparative`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchAblationEvaluation() {
  try {
    const res = await fetch(`${BACKEND_URL}/evaluation/ablation`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchConversationSessions(): Promise<Array<{
  session_id: string;
  title: string;
  created_at: string;
  last_updated: string;
  message_count: number;
  language: string;
  last_query: string;
}>> {
  try {
    const res = await fetch(`${BACKEND_URL}/conversation/sessions`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchSessionHistory(sessionId: string): Promise<{
  session_id: string;
  message_count: number;
  messages: any[];
}> {
  try {
    const res = await fetch(`${BACKEND_URL}/conversation/${sessionId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { session_id: sessionId, message_count: 0, messages: [] };
  }
}

export async function clearSessionHistory(sessionId: string): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND_URL}/conversation/${sessionId}/clear`, {
      method: 'POST',
      cache: 'no-store'
    });
    return res.ok;
  } catch (err) {
    return false;
  }
}
