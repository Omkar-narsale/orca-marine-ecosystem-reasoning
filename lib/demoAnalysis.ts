import { ORCAAnalysisResult } from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';

export function runDemoAnalysis(queryText: string, language: string = 'en'): ORCAAnalysisResult {
  const normalized = queryText.toLowerCase().trim();

  let defaultSummary =
    'ORCA multi-agent reasoning identifies Zone A (High Risk due to 4.1m swells & squall winds) and Zone B (Restricted naval fairway corridor) as critical areas to avoid tomorrow. Zone C offers clear and favorable operating conditions.';

  if (language === 'mr') {
    defaultSummary =
      'ORCA बहु-एजंट सागरी विश्लेषणानुसार: ZONE A (High Risk), ZONE B (Restricted) येथे जाणे टाळावे (INCOIS आणि IMD च्या अंदाजानुसार लाटा व वाऱ्यांचा धोका). सागरी हवामान ZONE C (Candidate) मध्ये अनुकूल राहण्याचा अंदाज आहे.';
  } else if (language === 'hi') {
    defaultSummary =
      'ORCA बहु-एजेंट समुद्री विश्लेषण के अनुसार: ZONE A (High Risk), ZONE B (Restricted) में जाने से बचें (INCOIS और IMD पूर्वानुमान के अनुसार तेज लहरों और हवाओं का जोखिम)। ZONE C में समुद्री स्थितियां अनुकूल रहने का अनुमान है।';
  }

  // Zone A specific inquiry
  if (normalized.includes('zone a') || normalized.includes('why is zone a') || normalized.includes('why should i avoid zone a')) {
    const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;
    const zoneB = DEMO_ZONES.find((z) => z.id === 'zone-b')!;
    const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;

    return {
      query: queryText,
      intent: 'Hazard Root-Cause & Risk Diagnostics',
      location: 'Northern Coastal Reach (Vasai-Manori Sector / Lat 19.3°N)',
      time: 'Forecast Window: Tomorrow 00:00 - 24:00 IST',
      summary:
        'Detailed diagnostic evaluation indicates Zone A presents severe maritime hazards. Significant wave height forecasts from INCOIS reach 4.1m with IMD coastal gale gusts up to 34 knots. Craft safety threshold is breached.',
      zonesToAvoid: [zoneA, zoneB],
      potentialZones: [zoneC],
      focusedZoneId: 'zone-a',
      filterMode: 'hazards',
      confidenceLevel: 'High',
      confidenceScore: 89,
      confidenceExplanation:
        'High source agreement between INCOIS Wave Watch III numerical model and IMD Mumbai Coastal Bulletin. Swell and wind vector convergence confirmed.',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Deconstructed query into spatial bounding box [Zone A] & meteorological risk metrics', status: 'completed' },
        { agentName: 'Ocean Agent', action: 'Queried INCOIS wave model; detected swell height 3.4m - 4.1m exceeding safety threshold', status: 'completed' },
        { agentName: 'Weather Agent', action: 'Cross-referenced IMD coastal bulletin; confirmed active squall line and 34-knot gusts', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Synthesized hazard composite; assigned Risk Score 87/100 (HIGH RISK)', status: 'completed' },
      ],
      keyAdvisories: [
        'INCOIS High Wave Warning (Active): Swell surge 3.4m - 4.1m with 11s peak period.',
        'IMD Squall Warning: Fishermen advised not to venture into North Maharashtra offshore waters.',
        'Vessel Safe Window: Estimated stabilization only after 48 hours.',
      ],
    };
  }

  // Zone C specific inquiry
  if (normalized.includes('zone c') || normalized.includes('is zone c safe')) {
    const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;
    const zoneD = DEMO_ZONES.find((z) => z.id === 'zone-d')!;
    const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;

    return {
      query: queryText,
      intent: 'Zone Suitability & Operational Window Verification',
      location: 'South Coastal Offshore (Alibag-Murud Shelf / Lat 18.6°N)',
      time: 'Operational Window: Tomorrow 05:00 - 14:00 IST',
      summary:
        'Zone C demonstrates optimal oceanographic safety and biological productivity indicators. Calm swell (<1.2m), gentle wind vectors (8-12 kts), and MOSDAC satellite chlorophyll front overlap make this a prime candidate.',
      zonesToAvoid: [zoneA],
      potentialZones: [zoneC, zoneD],
      focusedZoneId: 'zone-c',
      filterMode: 'safe',
      confidenceLevel: 'High',
      confidenceScore: 92,
      confidenceExplanation:
        'Strong corroboration between MOSDAC OCM-3 Chlorophyll thermal front and calm sea-state forecasts from INCOIS.',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Targeted Zone C coordinates for suitability and safety validation', status: 'completed' },
        { agentName: 'Ocean Agent', action: 'Fetched calm sea-state profile (wave <1.2m, SST 28.2°C)', status: 'completed' },
        { agentName: 'Geospatial Agent', action: 'Verified absence of naval anchorage and fairway restrictions in South Shelf', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Computed low risk index (18/100) and verified PFZ line synergy', status: 'completed' },
      ],
      keyAdvisories: [
        'Optimal departure window: Tomorrow 05:00 IST for morning pelagic operations.',
        'Clearance confirmed: Zero maritime fairway or defense exercise restrictions in effect.',
        'Weather outlook: Favorable skies with gentle breeze throughout the morning.',
      ],
    };
  }

  // Suitable / Best zones query
  if (
    normalized.includes('suitable') ||
    normalized.includes('best') ||
    normalized.includes('safe') ||
    normalized.includes('candidate')
  ) {
    const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;
    const zoneD = DEMO_ZONES.find((z) => z.id === 'zone-d')!;
    const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;
    const zoneB = DEMO_ZONES.find((z) => z.id === 'zone-b')!;

    return {
      query: queryText,
      intent: 'Candidate Fishing Zone Optimization',
      location: 'Mumbai & Konkan Coastal Offshore Region',
      time: 'Tomorrow — 05:30 to 14:00 IST',
      summary:
        'Multi-agent synthesis identifies Zone C as the primary safe operational candidate for tomorrow morning. Zone D is accessible with caution, whereas northern Zone A and central Zone B must be bypassed due to severe wave action and navigation restrictions respectively.',
      zonesToAvoid: [zoneA, zoneB],
      potentialZones: [zoneC, zoneD],
      focusedZoneId: 'zone-c',
      filterMode: 'safe',
      confidenceLevel: 'High',
      confidenceScore: 88,
      confidenceExplanation:
        'Confidence is reinforced by multi-sensor agreement across satellite ocean color (MOSDAC) and calibrated coastal wave models (INCOIS).',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Ranked all coastal sectors by combined safety-productivity index', status: 'completed' },
        { agentName: 'Ocean Agent', action: 'Isolated calm water pockets in South Sector; identified thermal front', status: 'completed' },
        { agentName: 'Weather Agent', action: 'Confirmed northern squall dissipation south of Mumbai harbor', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Flagged Zone C as Tier-1 candidate (Risk: 18) and Zone D as Tier-2 (Risk: 54)', status: 'completed' },
      ],
      keyAdvisories: [
        'Zone C recommended for all mechanized and motorized fishing craft.',
        'Zone D: Small crafts (<12m) should conclude operations prior to 13:00 IST afternoon swell rise.',
        'Avoid northern transit paths through Zone A and Zone B fairway corridor.',
      ],
    };
  }

  // Default / Avoid / Risky zones query
  const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;
  const zoneB = DEMO_ZONES.find((z) => z.id === 'zone-b')!;
  const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;
  const zoneD = DEMO_ZONES.find((z) => z.id === 'zone-d')!;

  return {
    query: queryText.trim() ? queryText : 'Which fishing zones should be avoided tomorrow?',
    intent: 'Fishing Safety & Maritime Hazard Analysis',
    location: 'Mumbai Coastal Region (Arabian Sea)',
    time: 'Tomorrow — 06:00 IST Forecast Window',
    summary:
      'ORCA agentic reasoning identifies Zone A (High Risk due to 4.1m swells & squall winds) and Zone B (Restricted naval fairway corridor) as critical areas to avoid tomorrow. Zone C offers clear and favorable operating conditions.',
    zonesToAvoid: [zoneA, zoneB],
    potentialZones: [zoneC, zoneD],
    focusedZoneId: 'zone-a',
    filterMode: 'all',
    confidenceLevel: 'Medium',
    confidenceScore: 78,
    confidenceExplanation:
      'Confidence is moderate based on available 12h forecast cycles, recent MOSDAC satellite imagery, and static cadastral geofences. Prototype confidence model.',
    agentTrace: [
      { agentName: 'Planner Agent', action: 'Initialized multi-source marine reasoning pipeline for Mumbai coastal perimeter', status: 'completed' },
      { agentName: 'Ocean Agent', action: 'Evaluated INCOIS Wave Watch III data: Rough seas (>3.5m) in Northern sector', status: 'completed' },
      { agentName: 'Weather Agent', action: 'Processed IMD Coastal Marine Advisory: 28-34kt gusts and squall alerts', status: 'completed' },
      { agentName: 'Geospatial Agent', action: 'Detected Naval Anchorage and Fairway geofence in Central Mumbai corridor', status: 'completed' },
      { agentName: 'Risk & Evidence Agent', action: 'Classified Zone A as High Risk (87/100) and Zone B as Restricted (72/100)', status: 'completed' },
    ],
    keyAdvisories: [
      'Zone A: High swell & wind speed advisory active. Craft return to port strongly recommended.',
      'Zone B: Prohibited commercial fishing zone (Naval & Commercial Fairway).',
      'Zone C: Recommended alternate operational area with calm sea state (0.8m - 1.2m).',
    ],
  };
}
