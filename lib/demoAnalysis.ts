import { ORCAAnalysisResult } from '@/types/marine';

/**
 * Returns an explicit backend unavailable state when connection fails.
 * NEVER returns fabricated marine values or fake scientific analysis.
 */
export function runDemoAnalysis(queryText: string, language: string = 'en'): ORCAAnalysisResult {
  const isHi = language === 'hi';
  const isMr = language === 'mr';

  const unavailableMsg = isMr
    ? 'ORCA बॅकएंड अनुपलब्ध आहे. कृपया कनेक्शन तपासा.'
    : isHi
    ? 'ORCA बैकएंड अनुपलब्ध है। कृपया कनेक्शन जांचें।'
    : 'ORCA backend is unavailable. Live marine telemetry cannot be retrieved.';

  return {
    query: queryText,
    intent: 'BACKEND_UNAVAILABLE',
    location: 'Coastal Waters',
    time: 'Current',
    summary: unavailableMsg,
    zonesToAvoid: [],
    potentialZones: [],
    focusedZoneId: undefined,
    filterMode: 'all',
    confidenceLevel: 'Low',
    confidenceScore: 0,
    confidenceExplanation: 'Backend is unreachable. No live scientific data available.',
    agentTrace: [
      {
        agentName: 'System Gateway',
        action: 'Connection to ORCA backend failed. Refusing to generate fabricated marine metrics.',
        status: 'failed'
      }
    ],
    keyAdvisories: ['ORCA backend is currently offline. Please ensure the backend server is running.'],
    limitations: ['Live telemetry unavailable.']
  };
}
