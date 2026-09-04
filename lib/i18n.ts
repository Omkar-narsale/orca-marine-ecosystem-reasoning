export type LanguageCode = 'en' | 'hi' | 'mr';

export interface TranslationDictionary {
  brandTitle: string;
  brandSubtitle: string;
  dataFeedsOnline: string;
  alerts: string;
  marineBrief: string;
  officer: string;
  askOrca: string;
  askOrcaSubtitle: string;
  inputPlaceholder: string;
  analyzeBtn: string;
  analyzingBtn: string;
  suggestedLabel: string;
  suggestedQueries: { label: string; query: string }[];
  
  // Nav
  navOverview: string;
  navMarineZones: string;
  navSafetyHazards: string;
  navEvidenceSources: string;
  navSettings: string;
  mapFocus: string;
  allZones: string;
  suitable: string;
  highRisk: string;
  restricted: string;
  
  // Zone details
  riskScore: string;
  keyForecastConditions: string;
  wave: string;
  wind: string;
  sst: string;
  marineAdvisoryActive: string;
  noWeatherAdvisory: string;
  restrictedArea: string;
  why: string;
  viewSource: string;
  inspect: string;

  // Analysis panel
  decisionTitle: string;
  confidence: string;
  evidenceCoverage: string;
  avoidHeader: string;
  candidatesHeader: string;
  followUpsLabel: string;
  wasUseful: string;
  yes: string;
  no: string;
  traceTitle: string;
  expandTrace: string;
  collapseTrace: string;

  // Alerts modal
  alertCenterTitle: string;
  activeAlertsCount: string;
  markViewed: string;
  acknowledged: string;
  zoomZone: string;
  noAlertsMsg: string;
  close: string;

  // Marine brief modal
  briefTitle: string;
  exportPrint: string;
  refId: string;
  sectorBounds: string;
  temporalEnvelope: string;
  executiveSummary: string;
  sectorRiskClass: string;
  authoritativeCitations: string;
}

export const I18N_STRINGS: Record<LanguageCode, TranslationDictionary> = {
  en: {
    brandTitle: 'ORCA',
    brandSubtitle: 'Conversational Multi-Agent Operational System',
    dataFeedsOnline: 'Data Feeds Online',
    alerts: 'Alerts',
    marineBrief: 'Marine Brief',
    officer: 'Officer',
    askOrca: 'Ask ORCA',
    askOrcaSubtitle: 'Ask a marine intelligence question',
    inputPlaceholder: 'e.g. Which fishing zones should be avoided tomorrow?',
    analyzeBtn: 'Analyze',
    analyzingBtn: 'Analyzing...',
    suggestedLabel: 'Suggested:',
    suggestedQueries: [
      { label: 'Avoid risky zones', query: 'Which fishing zones should be avoided tomorrow?' },
      { label: 'Suitable zones', query: 'Which fishing zones may be suitable tomorrow morning?' },
      { label: 'Marine hazards', query: 'Show risky zones near Mumbai' },
      { label: 'Why is Zone A risky?', query: 'Why should I avoid Zone A?' }
    ],
    navOverview: 'Overview',
    navMarineZones: 'Marine Zones',
    navSafetyHazards: 'Safety & Hazards',
    navEvidenceSources: 'Evidence & Sources',
    navSettings: 'Settings',
    mapFocus: 'MAP FOCUS',
    allZones: 'All Zones (4)',
    suitable: 'Suitable (Zone C)',
    highRisk: 'High Risk (Zone A)',
    restricted: 'Restricted (Zone B)',
    riskScore: 'Risk Score',
    keyForecastConditions: 'Key Forecast Conditions',
    wave: 'Wave',
    wind: 'Wind',
    sst: 'SST',
    marineAdvisoryActive: 'Marine advisory active',
    noWeatherAdvisory: 'No weather advisory',
    restrictedArea: 'Restricted: Naval Security Buffer',
    why: 'Why?',
    viewSource: 'View Source',
    inspect: 'Inspect',
    decisionTitle: 'ORCA Multi-Agent Decision',
    confidence: 'Confidence',
    evidenceCoverage: 'Evidence Coverage',
    avoidHeader: 'Zones to Avoid',
    candidatesHeader: 'Potential / Candidate Zones',
    followUpsLabel: 'Contextual Follow-ups:',
    wasUseful: 'Was this reasoning useful?',
    yes: 'Yes',
    no: 'No',
    traceTitle: 'ORCA Multi-Agent Execution Trace',
    expandTrace: 'Expand Trace',
    collapseTrace: 'Collapse Trace',
    alertCenterTitle: 'Active Marine Safety Alerts',
    activeAlertsCount: 'Active Marine Safety Alerts',
    markViewed: 'Mark Viewed',
    acknowledged: '✓ Acknowledged',
    zoomZone: 'Zoom Zone',
    noAlertsMsg: '✓ No active hazard alerts detected in currently evaluated operational zones.',
    close: 'Close',
    briefTitle: 'ORCA Marine Intelligence Brief',
    exportPrint: 'Export / Print',
    refId: 'Reference ID',
    sectorBounds: 'Sector Bounds',
    temporalEnvelope: 'Temporal Envelope',
    executiveSummary: 'Executive Decision Summary',
    sectorRiskClass: 'Sector Risk Classifications',
    authoritativeCitations: 'Authoritative Evidence Citations'
  },
  hi: {
    brandTitle: 'ORCA',
    brandSubtitle: 'संवादात्मक बहु-एजेंट समुद्री संचालन प्रणाली',
    dataFeedsOnline: 'डेटा फीड सक्रिय',
    alerts: 'अलर्ट',
    marineBrief: 'समुद्री ब्रीफ',
    officer: 'अधिकारी',
    askOrca: 'ORCA से पूछें',
    askOrcaSubtitle: 'समुद्री खुफिया से जुड़ा प्रश्न पूछें',
    inputPlaceholder: 'जैसे: कल सुबह कौन से मछली पकड़ने के क्षेत्र से बचना चाहिए?',
    analyzeBtn: 'विश्लेषण करें',
    analyzingBtn: 'विश्लेषण जारी...',
    suggestedLabel: 'सुझाए गए प्रश्न:',
    suggestedQueries: [
      { label: 'खतरनाक क्षेत्रों से बचें', query: 'कल सुबह कौन से मछली पकड़ने के क्षेत्र से बचना चाहिए?' },
      { label: 'उपयुक्त क्षेत्र', query: 'कल सुबह कौन से क्षेत्र मछली पकड़ने के लिए उपयुक्त हैं?' },
      { label: 'समुद्री खतरे', query: 'मुंबई के पास जोखिम भरे क्षेत्र दिखाएं' },
      { label: 'Zone A क्यों खतरनाक है?', query: 'Zone A क्यों खतरनाक है?' }
    ],
    navOverview: 'अवलोकन',
    navMarineZones: 'समुद्री क्षेत्र',
    navSafetyHazards: 'सुरक्षा और खतरे',
    navEvidenceSources: 'साक्ष्य और स्रोत',
    navSettings: 'सेटिंग्स',
    mapFocus: 'मानचित्र फोकस',
    allZones: 'सभी क्षेत्र (4)',
    suitable: 'अनुकूल (Zone C)',
    highRisk: 'उच्च जोखिम (Zone A)',
    restricted: 'प्रतिबंधित (Zone B)',
    riskScore: 'जोखिम स्कोर',
    keyForecastConditions: 'पूर्वानुमान मुख्य स्थितियां',
    wave: 'लहर',
    wind: 'हवा',
    sst: 'एसएसटी',
    marineAdvisoryActive: 'सक्रिय समुद्री चेतावनी',
    noWeatherAdvisory: 'कोई मौसम चेतावनी नहीं',
    restrictedArea: 'प्रतिबंधित: नौसेना सुरक्षा बफर',
    why: 'कारण?',
    viewSource: 'स्रोत देखें',
    inspect: 'जांचें',
    decisionTitle: 'ORCA बहु-एजेंट निर्णय',
    confidence: 'विश्वसनीयता',
    evidenceCoverage: 'साक्ष्य कवरेज',
    avoidHeader: 'बचने योग्य क्षेत्र',
    candidatesHeader: 'संभावित / अनुकूल क्षेत्र',
    followUpsLabel: 'प्रासंगिक अनुवर्ती प्रश्न:',
    wasUseful: 'क्या यह विश्लेषण उपयोगी था?',
    yes: 'हाँ',
    no: 'नहीं',
    traceTitle: 'ORCA बहु-एजेंट निष्पादन ट्रेस',
    expandTrace: 'ट्रेस देखें',
    collapseTrace: 'ट्रेस समेटें',
    alertCenterTitle: 'सक्रिय समुद्री सुरक्षा अलर्ट',
    activeAlertsCount: 'सक्रिय समुद्री सुरक्षा अलर्ट',
    markViewed: 'देखा गया',
    acknowledged: '✓ स्वीकृत',
    zoomZone: 'ज़ूम क्षेत्र',
    noAlertsMsg: '✓ वर्तमान परिचालन क्षेत्रों में कोई गंभीर चेतावनी नहीं पाई गई।',
    close: 'बंद करें',
    briefTitle: 'ORCA परिचालन समुद्री खुफिया ब्रीफ',
    exportPrint: 'निर्यात / प्रिंट',
    refId: 'संदर्भ आईडी',
    sectorBounds: 'क्षेत्र सीमाएं',
    temporalEnvelope: 'समय सीमा',
    executiveSummary: 'कार्यकारी निर्णय सारांश',
    sectorRiskClass: 'क्षेत्र जोखिम वर्गीकरण',
    authoritativeCitations: 'आधिकारिक साक्ष्य संदर्भ'
  },
  mr: {
    brandTitle: 'ORCA',
    brandSubtitle: 'संभाषणक्षम बहु-एजंट सागरी संचालन प्रणाली',
    dataFeedsOnline: 'डेटा फीड्स कार्यरत',
    alerts: 'सावधानता सूचना',
    marineBrief: 'सागरी माहिती अहवाल',
    officer: 'अधिकारी',
    askOrca: 'ORCA ला विचारा',
    askOrcaSubtitle: 'सागरी परिस्थितीबद्दल प्रश्न विचारा',
    inputPlaceholder: 'उदा: उद्या सकाळी कोणते मासेमारी क्षेत्र टाळावे?',
    analyzeBtn: 'विश्लेषण करा',
    analyzingBtn: 'विश्लेषण सुरू...',
    suggestedLabel: 'सुचवलेले प्रश्न:',
    suggestedQueries: [
      { label: 'धोकादायक क्षेत्र टाळा', query: 'उद्या सकाळी कोणते मासेमारी क्षेत्र टाळावे?' },
      { label: 'अनुकूल क्षेत्र', query: 'उद्या सकाळी मासेमारीसाठी कोणते क्षेत्र योग्य आहे?' },
      { label: 'सागरी धोके', query: 'मुंबईजवळील धोकादायक क्षेत्रे दाखवा' },
      { label: 'Zone A चे कारण काय?', query: 'Zone A का टाळावे?' }
    ],
    navOverview: 'आढावा',
    navMarineZones: 'सागरी क्षेत्रे',
    navSafetyHazards: 'सुरक्षा आणि धोके',
    navEvidenceSources: 'पुरावे आणि स्रोत',
    navSettings: 'सेटिंग्ज',
    mapFocus: 'नकाशा फोकस',
    allZones: 'सर्व क्षेत्रे (4)',
    suitable: 'अनुकूल (Zone C)',
    highRisk: 'उच्च धोका (Zone A)',
    restricted: 'प्रतिबंधित (Zone B)',
    riskScore: 'धोका गुण (Risk Score)',
    keyForecastConditions: 'हवामान अंदाज ठळक बाबी',
    wave: 'लाटा',
    wind: 'वारे',
    sst: 'तापमान',
    marineAdvisoryActive: 'सागरी इशारा सक्रिय',
    noWeatherAdvisory: 'कोणताही हवामान इशारा नाही',
    restrictedArea: 'प्रतिबंधित: नौदल सुरक्षा क्षेत्र',
    why: 'कारण?',
    viewSource: 'मूळ स्रोत पहा',
    inspect: 'तपासा',
    decisionTitle: 'ORCA बहु-एजंट निर्णय',
    confidence: 'विश्वासार्हता',
    evidenceCoverage: 'पुरावा कव्हरेज',
    avoidHeader: 'टाळण्याची क्षेत्रे',
    candidatesHeader: 'संभाव्य / अनुकूल क्षेत्रे',
    followUpsLabel: 'पुढील संबंधित प्रश्न:',
    wasUseful: 'हे विश्लेषण उपयुक्त ठरले का?',
    yes: 'होय',
    no: 'नाही',
    traceTitle: 'ORCA बहु-एजंट अंमलबजावणी ट्रेस',
    expandTrace: 'ट्रेस पहा',
    collapseTrace: 'ट्रेस लपवा',
    alertCenterTitle: 'सक्रिय सागरी सुरक्षा इशारे',
    activeAlertsCount: 'सक्रिय सागरी सुरक्षा इशारे',
    markViewed: 'पाहिले',
    acknowledged: '✓ मान्य केले',
    zoomZone: 'क्षेत्र झूम करा',
    noAlertsMsg: '✓ सध्याच्या परिचालन क्षेत्रात कोणताही गंभीर इशारा आढळलेला नाही.',
    close: 'बंद करा',
    briefTitle: 'ORCA ऑपरेशनल सागरी गुप्तवार्ता अहवाल',
    exportPrint: 'डाउनलोड / प्रिंट करा',
    refId: 'संदर्भ क्रमांक (Ref ID)',
    sectorBounds: 'क्षेत्र व्याप्ती',
    temporalEnvelope: 'वेळेची मर्यादा',
    executiveSummary: 'कार्यकारी निर्णय सारांश',
    sectorRiskClass: 'क्षेत्रनिहाय धोका वर्गीकरण',
    authoritativeCitations: 'अधिकृत वैज्ञानिक पुरावे'
  }
};
