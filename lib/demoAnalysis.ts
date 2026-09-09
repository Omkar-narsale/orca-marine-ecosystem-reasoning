import { ORCAAnalysisResult } from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';

export function runDemoAnalysis(queryText: string, language: string = 'en'): ORCAAnalysisResult {
  const normalized = queryText.toLowerCase().trim();

  let defaultSummary =
    'ORCA multi-agent reasoning identifies Zone A (elevated INCOIS wave swell & IMD squall warnings) and Zone B (restricted naval fairway corridor) as sectors to avoid. Zone C is identified as a candidate fishing zone with lower ORCA risk screening under available conditions.';

  if (language === 'mr') {
    defaultSummary =
      'ORCA बहु-एजंट सागरी विश्लेषणानुसार: ZONE A (High Risk) आणि ZONE B (Restricted) येथे जाणे टाळावे (INCOIS लाटा आणि IMD चेतावणी). ZONE C हे उपलब्ध परिस्थितीनुसार कमी जोखीम असलेले उमेदवार क्षेत्र आहे.';
  } else if (language === 'hi') {
    defaultSummary =
      'ORCA बहु-एजेंट समुद्री विश्लेषण के अनुसार: ZONE A (High Risk) और ZONE B (Restricted) में जाने से बचें (INCOIS तरंगें और IMD चेतावनी)। ZONE C उपलब्ध स्थितियों के तहत एक अनुकूल उम्मीदवार क्षेत्र है।';
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
        'Diagnostic evaluation indicates Zone A presents elevated maritime risks. Significant wave height forecasts from INCOIS reach 4.1m with IMD coastal gale gusts up to 34 knots. Zone A is flagged as HIGH RISK in ORCA risk screening.',
      zonesToAvoid: [zoneA, zoneB],
      potentialZones: [zoneC],
      focusedZoneId: 'zone-a',
      filterMode: 'hazards',
      confidenceLevel: 'High',
      confidenceScore: 89,
      confidenceExplanation:
        'High source agreement between INCOIS Wave Watch III numerical model and IMD Mumbai Coastal Bulletin. Swell and wind vector convergence verified.',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Deconstructed query into spatial bounding box [Zone A] & meteorological risk metrics', status: 'completed' },
        { agentName: 'Ocean Agent', action: 'Queried INCOIS wave model; detected swell height 3.4m - 4.1m contributing to risk elevation', status: 'completed' },
        { agentName: 'Weather Agent', action: 'Cross-referenced IMD coastal bulletin; confirmed active squall line and 34-knot gusts', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Synthesized hazard composite; assigned Risk Index 87/100 (HIGH RISK)', status: 'completed' },
      ],
      keyAdvisories: [
        'INCOIS High Swell Advisory (Active): Swell surge 3.4m - 4.1m with 11s peak period.',
        'IMD Squall Warning: Fishermen advised not to venture into North Maharashtra offshore waters.',
        'Re-evaluate after next INCOIS numerical forecast update cycle.',
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
      intent: 'Operational Suitability & Candidate Assessment',
      location: 'Southern Offshore Sector (Alibag-Murud Shelf / Lat 18.58°N)',
      time: 'Forecast Window: Tomorrow 05:00 - 14:00 IST',
      summary:
        'Zone C is evaluated as a suitable fishing candidate with an ORCA Risk Index of 18/100 and Suitability Index of 72/100. Favorable thermal gradients and manageable sea states (<1.2m swell) are observed. Candidate suitability is subject to forecast validity and does not guarantee fish catch.',
      zonesToAvoid: [zoneA],
      potentialZones: [zoneC, zoneD],
      focusedZoneId: 'zone-c',
      filterMode: 'safe',
      confidenceLevel: 'High',
      confidenceScore: 92,
      confidenceExplanation:
        'Convergence between INCOIS PFZ line, MOSDAC OCM-3 chlorophyll observation (3.4 mg/m³), and calm coastal wind reports from IMD.',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Identified candidate request; queried ocean color, SST gradients, and physical wave models', status: 'completed' },
        { agentName: 'Ocean Agent', action: 'Retrieved INCOIS OSF wave heights (0.8m - 1.2m) and MOSDAC thermal front overlay', status: 'completed' },
        { agentName: 'Geospatial Agent', action: 'Verified sector boundaries against GIS Cadastre; zero naval restrictions detected', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Calculated Risk Index 18/100 (LOW); marked as Fishing Suitability Candidate', status: 'completed' },
      ],
      keyAdvisories: [
        'INCOIS PFZ Advisory: Active thermal front gradient identified.',
        'IMD Marine Bulletin: Favorable coastal winds (8-12 knots).',
        'Suitability Assessment: Candidate fishing zone; subject to real-time weather observation.',
      ],
    };
  }

  // Zone B / Restricted area inquiry
  if (normalized.includes('zone b') || normalized.includes('restricted') || normalized.includes('naval')) {
    const zoneB = DEMO_ZONES.find((z) => z.id === 'zone-b')!;
    const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;
    const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;

    return {
      query: queryText,
      intent: 'Geospatial Boundary & Maritime Restriction Analysis',
      location: 'Mumbai Port Approaches & Fairway (Lat 18.97°N / Lon 72.64°E)',
      time: 'Status: Permanent Regulatory Cadastre Constraint',
      summary:
        'Zone B is a RESTRICTED maritime sector. It intersects the Mumbai Harbor Naval Anchorage Buffer and Vessel Traffic Separation (TSS) Corridor. Commercial and artisanal fishing is legally prohibited regardless of weather.',
      zonesToAvoid: [zoneB, zoneA],
      potentialZones: [zoneC],
      focusedZoneId: 'zone-b',
      filterMode: 'restricted',
      confidenceLevel: 'High',
      confidenceScore: 98,
      confidenceExplanation:
        'Authoritative GIS Cadastre and National Hydrographic Office boundary verification. Statutory non-navigable zone for fishing.',
      agentTrace: [
        { agentName: 'Planner Agent', action: 'Received regulatory query; routed to Geospatial and Risk agents', status: 'completed' },
        { agentName: 'Geospatial Agent', action: 'Checked spatial polygon intersection against GIS Cadastre naval envelopes', status: 'completed' },
        { agentName: 'Risk & Evidence Agent', action: 'Applied absolute constraint rule; marked zone as RESTRICTED', status: 'completed' },
        { agentName: 'Synthesis Agent', action: 'Generated statutory compliance advisory and alternative routing suggestions', status: 'completed' },
      ],
      keyAdvisories: [
        'Maritime Cadastre: Commercial fishing strictly prohibited in shipping channels.',
        'Naval Security: 2.5 nm buffer around defense anchorages enforced by Coastguard.',
        'Alternative Sector: Zone C is the closest unrestricted candidate zone.',
      ],
    };
  }

  // Default General Query
  const zoneA = DEMO_ZONES.find((z) => z.id === 'zone-a')!;
  const zoneB = DEMO_ZONES.find((z) => z.id === 'zone-b')!;
  const zoneC = DEMO_ZONES.find((z) => z.id === 'zone-c')!;
  const zoneD = DEMO_ZONES.find((z) => z.id === 'zone-d')!;

  return {
    query: queryText,
    intent: 'General Operational Marine Assessment',
    location: 'Maharashtra Coastal Domain (18.0°N–20.0°N)',
    time: 'Forecast Window: Tomorrow 06:00 - 18:00 IST',
    summary: defaultSummary,
    zonesToAvoid: [zoneA, zoneB],
    potentialZones: [zoneC, zoneD],
    focusedZoneId: 'zone-a',
    filterMode: 'all',
    confidenceLevel: 'High',
    confidenceScore: 88,
    confidenceExplanation:
      'Multi-source convergence across INCOIS wave models, IMD coastal synoptic bulletins, MOSDAC satellite telemetry, and GIS hydrographic cadastre.',
    agentTrace: [
      { agentName: 'Planner Agent', action: 'Decomposed operational query into 4 candidate sectors and 6 marine parameter domains', status: 'completed' },
      { agentName: 'Ocean Agent', action: 'Fetched INCOIS OSF wave telemetry (4.1m north vs 1.0m south) and MOSDAC SST/chlorophyll', status: 'completed' },
      { agentName: 'Weather Agent', action: 'Evaluated IMD coastal wind fields; identified 28-34kt squall warning in northern sector', status: 'completed' },
      { agentName: 'Geospatial Agent', action: 'Intersected zone geometries with GIS Cadastre; flagged Zone B naval fairway restriction', status: 'completed' },
      { agentName: 'Risk & Evidence Agent', action: 'Executed deterministic risk scoring and ranked candidate sectors', status: 'completed' },
      { agentName: 'Synthesis Agent', action: 'Synthesized executive decision recommendation with full evidence provenance citations', status: 'completed' },
    ],
    keyAdvisories: [
      'Avoid Zone A (elevated INCOIS wave forecast & IMD squall warning) and Zone B (restricted naval corridor).',
      'Zone C is a suitable candidate with favorable sea state (1.0m) and verified unrestricted boundaries.',
      'Zone D is a secondary alternative candidate; observe afternoon wind transitions.',
    ],
  };
}
