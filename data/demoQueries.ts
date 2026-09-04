export interface DemoQueryItem {
  id: string;
  query: string;
  label: string;
  category: 'Safety' | 'Suitability' | 'Zone Detail' | 'Overview';
  description: string;
}

export const DEMO_QUERIES: DemoQueryItem[] = [
  {
    id: 'query-1',
    query: 'Which fishing zones should be avoided tomorrow?',
    label: 'Which zones should be avoided tomorrow?',
    category: 'Safety',
    description: 'Highlights high-risk and restricted marine sectors based on forecast wave, wind and geofences.',
  },
  {
    id: 'query-2',
    query: 'Which fishing zones may be suitable tomorrow morning?',
    label: 'Best fishing zones tomorrow morning',
    category: 'Suitability',
    description: 'Identifies safe operational candidate zones with favorable oceanographic parameters and PFZ cues.',
  },
  {
    id: 'query-3',
    query: 'Why should I avoid Zone A?',
    label: 'Why is Zone A risky?',
    category: 'Zone Detail',
    description: 'Deep dives into specific risk factors, wave alerts, and gale conditions for Northern Sector (Zone A).',
  },
  {
    id: 'query-4',
    query: 'Show risky zones near Mumbai',
    label: 'Show risky zones near Mumbai',
    category: 'Safety',
    description: 'Filters coastal map layers to isolate hazards, active squalls, and security buffer restrictions.',
  },
  {
    id: 'query-5',
    query: 'Is Zone C safe for fishing tomorrow?',
    label: 'Is Zone C safe for fishing tomorrow?',
    category: 'Suitability',
    description: 'Verifies safety envelope, sea state, and advisory window for South Coastal Zone C.',
  },
];
