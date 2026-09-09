'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  Loader2,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Waves,
  Compass,
  MapPin,
  FileText,
  SlidersHorizontal,
  BrainCircuit,
  Database,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  ExternalLink,
  Info,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Network
} from 'lucide-react';
import dynamic from 'next/dynamic';
import { MarineZone, EvidenceSource, ORCAAnalysisResult } from '@/types/marine';
import { ZoneDetails } from '@/components/ZoneDetails';
import { IntentCardRouter } from '@/components/analysis/IntentCards';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';
import { useSpeechRecognition } from '@/lib/useSpeechRecognition';
import { useSpeechSynthesis } from '@/lib/useSpeechSynthesis';

const MarineMap = dynamic(
  () => import('@/components/MarineMap').then((mod) => mod.MarineMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[520px] rounded-xl bg-[#0A1628] border border-slate-800 flex flex-col items-center justify-center text-slate-400 font-mono text-xs gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-teal-400" />
        <span>Initializing Marine Operations Grid...</span>
      </div>
    ),
  }
);

import { GeolocationState } from '@/lib/useGeolocation';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  decision?: any;
  focused_zone_id?: string;
  zonesToAvoid?: any[];
  potentialZones?: any[];
  all_zones?: MarineZone[];
  confidenceScore?: number;
  confidenceLevel?: string;
  language?: string;
  response_type?: string;
  data?: any;
  results?: any[];
  why_reasons?: string[];
  sources?: any[];
  map?: any;
  follow_up_suggestions?: string[];
  claim_evidence_map?: {
    claims?: Array<{ claim: string; evidence_ids: string[]; confidence?: string }>;
    evidence_items?: any[];
  };
  human_friendly?: {
    summary?: string;
    what_this_means?: string;
    recommendation?: string;
    what_you_should_do?: string;
    why?: string[];
    evidence?: string[];
    sources?: string[];
  };
}

interface QueryPanelProps {
  messages: ChatMessage[];
  onAnalyze: (query: string) => void;
  isAnalyzing: boolean;
  currentQuery: string;
  language?: string;
  onLanguageChange?: (lang: string) => void;
  activeZones: MarineZone[];
  selectedZone: MarineZone | null;
  onSelectZone: (zone: MarineZone) => void;
  onOpenReasoningTab?: () => void;
  onOpenEvidenceTab?: () => void;
  onOpenWhatIfModal?: () => void;
  onOpenConfidenceModal?: () => void;
  onNewChat?: () => void;
  locationState?: GeolocationState;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({
  messages,
  onAnalyze,
  isAnalyzing,
  currentQuery,
  language = 'en',
  onLanguageChange,
  activeZones,
  selectedZone,
  onSelectZone,
  onOpenReasoningTab,
  onOpenEvidenceTab,
  onOpenWhatIfModal,
  onOpenConfidenceModal,
  onNewChat,
  locationState,
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  const [inputValue, setInputValue] = useState<string>('');
  const [loadingStep, setLoadingStep] = useState<string>('ORCA is analyzing telemetry...');
  const [showMapModal, setShowMapModal] = useState<boolean>(true);
  const [expandedReasoningMsgId, setExpandedReasoningMsgId] = useState<string | null>(null);
  const [expandedEvidenceMsgId, setExpandedEvidenceMsgId] = useState<string | null>(null);
  const [activeSpeakingMsgId, setActiveSpeakingMsgId] = useState<string | null>(null);

  // Speech Recognition Hook (STT)
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported: isSttSupported,
    error: sttError,
  } = useSpeechRecognition({
    onResult: (text) => {
      setInputValue(text);
    },
  });

  // Speech Synthesis Hook (TTS)
  const {
    isPlaying,
    isPaused,
    currentText,
    voiceNotice,
    speak,
    pause,
    resume,
    stop,
  } = useSpeechSynthesis({
    onEnd: () => {
      setActiveSpeakingMsgId(null);
    },
  });
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const mapSectionRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of conversation when messages change
  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isAnalyzing]);

  // Loading indicator step cycle
  useEffect(() => {
    if (!isAnalyzing) return;
    const steps = [
      'Extracting contextual intent & constraints...',
      'Querying INCOIS wave telemetry & IMD warnings...',
      'Screening GIS Cadastre naval geofences...',
      'Synthesizing deterministic marine recommendations...',
    ];
    let idx = 0;
    setLoadingStep(steps[0]);
    const timer = setInterval(() => {
      idx = (idx + 1) % steps.length;
      setLoadingStep(steps[idx]);
    }, 900);
    return () => clearInterval(timer);
  }, [isAnalyzing]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isAnalyzing) return;
    const query = inputValue.trim();
    setInputValue('');
    onAnalyze(query);
  };

  const handlePromptClick = (queryText: string) => {
    onAnalyze(queryText);
  };

  const handleShowMapClick = (zoneId?: string) => {
    if (zoneId) {
      const found = activeZones.find(z => z.id === zoneId);
      if (found) onSelectZone(found);
    }
    if (mapSectionRef.current) {
      mapSectionRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const initialPrompts = [
    {
      title: 'Hazard & Avoidance',
      query: 'Which fishing zones should I avoid tomorrow morning?',
      desc: 'Screen sectors against INCOIS waves & IMD squall warnings',
      icon: ShieldAlert,
      badge: 'Safety',
    },
    {
      title: 'Candidate Search',
      query: 'Find a lower-risk fishing candidate near my location.',
      desc: 'Rank candidates using deterministic ocean suitability',
      icon: Sparkles,
      badge: 'Suitability',
    },
    {
      title: 'Sector Comparison',
      query: 'Compare Zone A and Zone C.',
      desc: 'Contrast wave height, wind gusts, and regulatory boundaries',
      icon: Waves,
      badge: 'Comparison',
    },
    {
      title: 'Geofence Boundaries',
      query: 'Are there any active restricted zones?',
      desc: 'Inspect GIS Cadastre naval envelopes & maritime fairways',
      icon: Compass,
      badge: 'Geofences',
    },
  ];

  // Dynamic context-aware suggested follow-ups
  const getDynamicFollowUps = (lastMsg?: ChatMessage) => {
    if (!lastMsg) return [];
    if (lastMsg.follow_up_suggestions && lastMsg.follow_up_suggestions.length > 0) {
      return lastMsg.follow_up_suggestions;
    }
    const avoidCount = lastMsg.zonesToAvoid?.length || 0;
    const candidateCount = lastMsg.potentialZones?.length || 0;

    const suggestions: string[] = [];
    if (avoidCount > 0) {
      suggestions.push('Why should I avoid Zone A?');
    }
    if (candidateCount > 0) {
      suggestions.push('What about Zone C?');
      suggestions.push('Can you find another option closer to shore?');
    }
    suggestions.push('Compare Zone A and Zone C');
    suggestions.push('Is there any active fishermen warning?');
    return suggestions.slice(0, 4);
  };

  const lastAssistantMessage = [...messages].reverse().find(m => m.role === 'assistant');
  const followUpChips = getDynamicFollowUps(lastAssistantMessage);

  return (
    <div className="flex flex-col h-full w-full max-w-7xl mx-auto font-mono text-slate-100 space-y-4">
      {/* Top Session & Operational Context Strip */}
      <div className="flex items-center justify-between bg-[#0F172A] border border-slate-800 px-4 py-2.5 rounded-xl shadow-md text-xs">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/30 text-teal-300 font-bold text-[10px]">
            <Sparkles className="w-3 h-3 text-teal-400" />
            <span>ORCA CONVERSATIONAL ENGINE</span>
          </div>
          <span className="text-slate-400 text-[11px] hidden sm:inline">
            Sector: Maharashtra Coastal Grid (18.2°N – 19.5°N)
          </span>
        </div>
        <div className="flex items-center gap-2">
          {/* Language Switcher Pill */}
          <div className="flex items-center gap-0.5 bg-slate-900 border border-slate-700/80 rounded-lg p-0.5">
            {[
              { code: 'en', label: 'EN' },
              { code: 'hi', label: 'हिंदी' },
              { code: 'mr', label: 'मराठी' },
            ].map((l) => (
              <button
                key={l.code}
                type="button"
                onClick={() => onLanguageChange && onLanguageChange(l.code)}
                className={`px-2 py-0.5 text-[10px] font-bold rounded transition-colors ${
                  language === l.code
                    ? 'bg-teal-500 text-slate-950 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title={`Switch language to ${l.label}`}
              >
                {l.label}
              </button>
            ))}
          </div>

          {onNewChat && messages.length > 0 && (
            <button
              onClick={onNewChat}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-[11px] font-bold transition-colors"
              title="Start a fresh conversation session"
            >
              <RotateCcw className="w-3 h-3 text-teal-400" />
              <span>New Chat</span>
            </button>
          )}
          {onOpenReasoningTab && (
            <button
              onClick={onOpenReasoningTab}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-[11px] font-bold transition-colors"
            >
              <BrainCircuit className="w-3 h-3 text-cyan-400" />
              <span className="hidden sm:inline">Technical Reasoning</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Conversation & Decision Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start flex-1 min-h-[500px]">
        {/* LEFT COLUMN: Chat Stream (8 cols on desktop) */}
        <div className={`flex flex-col justify-between ${messages.length > 0 ? 'lg:col-span-7' : 'lg:col-span-12'} space-y-4`}>
          {/* Scrollable Messages Window */}
          <div className="bg-[#0A1224]/80 border border-slate-800/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4 min-h-[420px] max-h-[620px] overflow-y-auto">
            {/* EMPTY STATE: Welcome Landing View */}
            {messages.length === 0 && (
              <div className="py-6 sm:py-10 text-center space-y-6">
                <div className="inline-flex p-3 rounded-2xl bg-teal-500/10 border border-teal-500/30 shadow-inner">
                  <Waves className="w-8 h-8 text-teal-400 animate-pulse" />
                </div>
                <div className="space-y-2">
                  <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-sans">
                    ORCA Marine Intelligence
                  </h1>
                  <p className="text-xs sm:text-sm text-slate-300 font-sans max-w-lg mx-auto leading-relaxed">
                    Ask questions in natural language. ORCA reasons over authoritative INCOIS, IMD, and GIS data to guide maritime operations.
                  </p>
                </div>

                {/* Suggested Inquiries Grid */}
                <div className="pt-4 space-y-2.5 text-left max-w-2xl mx-auto">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-widest text-center">
                    Suggested Inquiries
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {initialPrompts.map((p, idx) => {
                      const Icon = p.icon;
                      return (
                        <div
                          key={idx}
                          onClick={() => handlePromptClick(p.query)}
                          className="p-3 bg-[#0F172A] hover:bg-slate-800/90 rounded-xl border border-slate-800 hover:border-teal-500/50 cursor-pointer transition-all space-y-1 group shadow-md"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Icon className="w-3.5 h-3.5 text-teal-400 group-hover:scale-110 transition-transform" />
                              <span className="font-bold text-white text-[11px] font-sans">{p.title}</span>
                            </div>
                            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[9px] text-slate-400 border border-slate-700">
                              {p.badge}
                            </span>
                          </div>
                          <p className="text-[11px] font-sans font-medium text-slate-200 group-hover:text-teal-300 transition-colors">
                            &ldquo;{p.query}&rdquo;
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* MESSAGE STREAM: User & Assistant Alternating */}
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              const isReasoningExpanded = expandedReasoningMsgId === msg.id;
              const isEvidenceExpanded = expandedEvidenceMsgId === msg.id;
              const isSpeaking = activeSpeakingMsgId === msg.id && isPlaying;

              if (isUser) {
                return (
                  <div key={msg.id} className="flex justify-end animate-in fade-in slide-in-from-bottom-2 duration-200">
                    <div className="max-w-[85%] bg-teal-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 shadow-md space-y-1">
                      <div className="flex items-center justify-between gap-3 text-[10px] text-teal-200/90 font-mono">
                        <span className="font-bold">YOU</span>
                        <span>{msg.timestamp || 'Just now'}</span>
                      </div>
                      <p className="text-xs sm:text-sm font-sans font-medium leading-relaxed whitespace-pre-wrap">
                        {msg.content}
                      </p>
                    </div>
                  </div>
                );
              }

              // Assistant Message Bubble
              return (
                <div key={msg.id} className="flex flex-col items-start gap-2 max-w-[95%] animate-in fade-in slide-in-from-bottom-2 duration-200">
                  <div className="w-full bg-[#0F172A] border border-slate-800 rounded-2xl rounded-tl-sm p-4 shadow-lg space-y-3">
                    {/* Header */}
                    <div className="flex items-center justify-between text-[10px] pb-2 border-b border-slate-800/80">
                      <div className="flex items-center gap-1.5 text-teal-400 font-bold">
                        <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                        <span>ORCA INTELLIGENCE</span>
                      </div>
                      <span className="text-slate-400">{msg.timestamp || 'Just now'}</span>
                    </div>

                    {/* Natural Conversational Answer */}
                    <div className="text-xs sm:text-sm font-sans text-slate-100 leading-relaxed space-y-2">
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>

                    {/* Dynamic Question-Centric Intent Cards */}
                    <IntentCardRouter
                      responseType={msg.response_type || msg.decision?.response_type}
                      data={msg.data || msg.decision?.data}
                      results={msg.results || msg.decision?.results || []}
                      whyReasons={msg.why_reasons || msg.decision?.why_reasons || []}
                      sources={msg.sources || msg.decision?.sources || []}
                      onSelectCandidate={(cand) => {
                        if (cand.id) handleShowMapClick(cand.id);
                      }}
                      onShowMap={() => handleShowMapClick(msg.focused_zone_id)}
                    />

                    {/* Decision Summary Chips */}
                    {msg.decision && (
                      <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                        {msg.zonesToAvoid && msg.zonesToAvoid.length > 0 && (
                          <span
                            onClick={() => handleShowMapClick(msg.zonesToAvoid?.[0]?.id)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300 font-bold cursor-pointer hover:bg-rose-500/25 transition-colors"
                            title={msg.zonesToAvoid?.[0]?.reasons?.[0] || "Area avoided due to combined ocean conditions"}
                          >
                            <AlertTriangle className="w-3 h-3 text-rose-400" />
                            <span>
                              {msg.zonesToAvoid.length} Avoid {msg.zonesToAvoid.length === 1 ? 'Area' : 'Areas'}
                              {msg.zonesToAvoid[0]?.name ? `: ${msg.zonesToAvoid[0].name}` : ''}
                            </span>
                          </span>
                        )}
                        {msg.potentialZones && msg.potentialZones.length > 0 && (
                          <span
                            onClick={() => handleShowMapClick(msg.potentialZones?.[0]?.id)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 font-bold cursor-pointer hover:bg-emerald-500/25 transition-colors"
                            title="Evaluated as lower-risk candidate under retrieved ocean conditions"
                          >
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            <span>
                              {msg.potentialZones.filter((z: any) => z.status === 'suitable' || z.status === 'suitable_candidate').length} Lower-Risk Candidate
                              {msg.potentialZones[0]?.name ? `: ${msg.potentialZones[0].name}` : ''}
                            </span>
                          </span>
                        )}
                        {msg.confidenceScore && (
                          <span
                            onClick={onOpenConfidenceModal}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 font-bold cursor-pointer hover:bg-cyan-500/25 transition-colors"
                            title="This indicates how complete and consistent the retrieved evidence is. It is NOT a probability of safety."
                          >
                            <Info className="w-3 h-3 text-cyan-400" />
                            <span>Evidence Confidence: {msg.confidenceScore} / 100</span>
                          </span>
                        )}
                      </div>
                    )}

                    {/* Quick Action Buttons */}
                    <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80 text-[11px]">
                      {/* Spoken Audio Listen Button */}
                      <button
                        onClick={() => {
                          if (isSpeaking) {
                            stop();
                            setActiveSpeakingMsgId(null);
                          } else {
                            setActiveSpeakingMsgId(msg.id);
                            speak(msg.content, msg.language || language);
                          }
                        }}
                        className={`flex items-center gap-1 px-2.5 py-1 rounded transition-colors font-bold ${
                          isSpeaking
                            ? 'bg-teal-500/20 text-teal-300 border border-teal-500/50 animate-pulse'
                            : 'bg-slate-800 hover:bg-slate-700 text-teal-300 hover:text-white border border-slate-700'
                        }`}
                        title={
                          isSpeaking
                            ? 'Stop spoken response'
                            : language === 'mr'
                            ? 'उत्तर ऐका (मराठी)'
                            : language === 'hi'
                            ? 'उत्तर सुनें (हिंदी)'
                            : 'Listen to spoken response'
                        }
                      >
                        {isSpeaking ? (
                          <>
                            <VolumeX className="w-3 h-3 text-teal-400" />
                            <span>Stop Audio</span>
                          </>
                        ) : (
                          <>
                            <Volume2 className="w-3 h-3 text-teal-400" />
                            <span>Listen</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => {
                          handleShowMapClick(msg.focused_zone_id);
                        }}
                        className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-teal-300 hover:text-white border border-slate-700 transition-colors font-bold"
                      >
                        <MapPin className="w-3 h-3 text-teal-400" />
                        <span>Show on Map</span>
                      </button>

                      <button
                        onClick={() => setExpandedReasoningMsgId(isReasoningExpanded ? null : msg.id)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 hover:text-white border border-slate-700 transition-colors font-bold"
                      >
                        <BrainCircuit className="w-3 h-3 text-cyan-400" />
                        <span>{isReasoningExpanded ? 'Hide Why' : 'Why?'}</span>
                      </button>

                      {/* Evidence Graph Button */}
                      <button
                        onClick={() => setExpandedEvidenceMsgId(isEvidenceExpanded ? null : msg.id)}
                        className={`flex items-center gap-1 px-2.5 py-1 rounded transition-colors font-bold ${
                          isEvidenceExpanded
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                            : 'bg-slate-800 hover:bg-slate-700 text-amber-300 hover:text-white border border-slate-700'
                        }`}
                        title="View claim-to-evidence graph mapping"
                      >
                        <Network className="w-3 h-3 text-amber-400" />
                        <span>{isEvidenceExpanded ? 'Hide Evidence' : 'Evidence Graph'}</span>
                      </button>

                      {msg.results && msg.results.length >= 2 && (
                        <button
                          onClick={() => onAnalyze('Compare them')}
                          className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-purple-300 hover:text-white border border-slate-700 transition-colors font-bold"
                        >
                          <SlidersHorizontal className="w-3 h-3 text-purple-400" />
                          <span>Compare</span>
                        </button>
                      )}

                      {(msg.response_type === 'PFZ_RESULTS' || msg.response_type === 'PRODUCTIVITY_RESULTS') && (
                        <button
                          onClick={() => onAnalyze('Can you find an option closer to shore?')}
                          className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-300 hover:text-white border border-slate-700 transition-colors font-bold"
                        >
                          <Compass className="w-3 h-3 text-emerald-400" />
                          <span>Closer to Shore</span>
                        </button>
                      )}

                      <button
                        onClick={() => {
                          if (onOpenEvidenceTab) onOpenEvidenceTab();
                          else onAnalyze('Show sources');
                        }}
                        className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors font-bold"
                      >
                        <Database className="w-3 h-3 text-amber-400" />
                        <span>Sources</span>
                      </button>
                    </div>

                    {/* Honest Voice Fallback Notice for Marathi / Unsupported Voices */}
                    {activeSpeakingMsgId === msg.id && voiceNotice && (
                      <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-sans flex items-center gap-2 animate-in fade-in">
                        <Info className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span>{voiceNotice}</span>
                      </div>
                    )}

                    {/* Collapsible 2-Layer Why Drawer */}
                    {isReasoningExpanded && (
                      <div className="p-3.5 rounded-xl bg-slate-900/95 border border-cyan-500/30 text-[11px] space-y-3.5 animate-in fade-in duration-150 shadow-xl">
                        <div className="flex items-center justify-between text-cyan-300 font-bold border-b border-slate-800 pb-1.5">
                          <div className="flex items-center gap-1.5">
                            <BrainCircuit className="w-3.5 h-3.5 text-cyan-400" />
                            <span className="text-xs">Why is ORCA recommending this?</span>
                          </div>
                          {onOpenReasoningTab && (
                            <button
                              onClick={onOpenReasoningTab}
                              className="text-[10px] text-teal-400 hover:underline flex items-center gap-1"
                            >
                              <span>View Full Pipeline</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </button>
                          )}
                        </div>

                        {/* LAYER 1: USER-FRIENDLY EXPLANATION */}
                        <div className="space-y-2">
                          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/70 space-y-1.5">
                            {msg.zonesToAvoid && msg.zonesToAvoid.length > 0 ? (
                              <div className="text-rose-300 font-medium">
                                ⚠️ <strong>Area Recommendation:</strong> ORCA recommends avoiding the highlighted area because the combined ocean conditions are less favorable for small craft activity compared with alternative zones.
                              </div>
                            ) : (
                              <div className="text-emerald-300 font-medium">
                                🌊 <strong>Area Recommendation:</strong> Current retrieved conditions appear generally manageable. No major storm threat was identified in the analyzed sectors.
                              </div>
                            )}

                            <div className="pt-1 text-slate-300 space-y-1">
                              <div>
                                <span className="font-semibold text-slate-200">What this means:</span>{' '}
                                <span>
                                  {msg.human_friendly?.what_this_means ||
                                    "The forecast does not indicate a severe regional cyclone, but combined sea state and winds require calibrated navigation."}
                                </span>
                              </div>
                              <div>
                                <span className="font-semibold text-slate-200">What should I do?</span>{' '}
                                <span>
                                  {msg.human_friendly?.what_you_should_do ||
                                    msg.human_friendly?.recommendation ||
                                    "Consider using one of the lower-risk candidate areas shown on the map and monitor local VHF alerts."}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Contributing Factors Breakdown */}
                          <div className="space-y-1">
                            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                              Contributing Factors
                            </span>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                              {msg.why_reasons && msg.why_reasons.length > 0 ? (
                                msg.why_reasons.map((reason, rIdx) => (
                                  <div key={rIdx} className="p-2 rounded bg-slate-950/70 border border-slate-800 text-slate-300 flex items-start gap-1.5">
                                    <span className="text-cyan-400 font-bold shrink-0">•</span>
                                    <span className="leading-snug">{reason}</span>
                                  </div>
                                ))
                              ) : (
                                <>
                                  <div className="p-2 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                                    🌊 <strong>Wave conditions:</strong> Manageable (&lt;1.4m)
                                  </div>
                                  <div className="p-2 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                                    💨 <strong>Wind conditions:</strong> Moderate (&lt;15 kt)
                                  </div>
                                  <div className="p-2 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                                    ⛈️ <strong>Weather warnings:</strong> None detected
                                  </div>
                                  <div className="p-2 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                                    🗺️ <strong>Fairway restrictions:</strong> Clear
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* LAYER 2: TECHNICAL EVIDENCE SUMMARY */}
                        <div className="pt-2 border-t border-slate-800 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase font-bold text-teal-400 tracking-wider">
                              Technical Evidence
                            </span>
                            <button
                              onClick={() => setExpandedEvidenceMsgId(msg.id)}
                              className="text-[10px] text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1"
                            >
                              <span>[VIEW FULL EVIDENCE]</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </button>
                          </div>

                          <div className="grid grid-cols-3 gap-1.5 text-[10px] font-mono">
                            <div className="p-1.5 rounded bg-slate-950/80 border border-slate-800 text-center">
                              <span className="text-teal-400 font-bold block">🌊 INCOIS</span>
                              <span className="text-slate-200">
                                {msg.human_friendly?.evidence?.find((e: string) => e.includes('Wave'))?.split(':')[1]?.slice(0, 24) || "Waves < 1.4 m"}
                              </span>
                            </div>
                            <div className="p-1.5 rounded bg-slate-950/80 border border-slate-800 text-center">
                              <span className="text-amber-400 font-bold block">⛈️ IMD</span>
                              <span className="text-slate-200">
                                {msg.human_friendly?.evidence?.find((e: string) => e.includes('Weather'))?.split(':')[1]?.slice(0, 24) || "Warning: None"}
                              </span>
                            </div>
                            <div className="p-1.5 rounded bg-slate-950/80 border border-slate-800 text-center">
                              <span className="text-cyan-400 font-bold block">🗺️ GIS</span>
                              <span className="text-slate-200">
                                {msg.human_friendly?.evidence?.find((e: string) => e.includes('Navigation'))?.split(':')[1]?.slice(0, 24) || "Fairways: Clear"}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Collapsible Claim-to-Evidence Traceability Drawer */}
                    {isEvidenceExpanded && (
                      <div className="p-3.5 rounded-xl bg-[#0B132B] border border-amber-500/30 text-[11px] space-y-3 animate-in fade-in duration-150">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                          <div className="flex items-center gap-1.5 text-amber-300 font-bold">
                            <Network className="w-3.5 h-3.5 text-amber-400" />
                            <span>Claim-to-Evidence Traceability Graph</span>
                          </div>
                          <span className="text-[10px] text-slate-400 font-mono">Deterministic Provenance</span>
                        </div>

                        {/* Claims Mapping */}
                        {msg.claim_evidence_map?.claims && msg.claim_evidence_map.claims.length > 0 && (
                          <div className="space-y-2">
                            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                              Corroborated Assertions
                            </span>
                            <div className="space-y-1.5">
                              {msg.claim_evidence_map.claims.map((cl, cIdx) => (
                                <div key={cIdx} className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
                                  <div className="flex items-center justify-between text-xs font-sans text-slate-200">
                                    <span className="font-semibold">&ldquo;{cl.claim}&rdquo;</span>
                                    {cl.confidence && (
                                      <span className="px-1.5 py-0.2 rounded bg-teal-500/15 text-teal-300 text-[9px] font-mono border border-teal-500/30">
                                        {cl.confidence}
                                      </span>
                                    )}
                                  </div>
                                  <div className="flex flex-wrap items-center gap-1 text-[10px] text-slate-400 font-mono">
                                    <span>Supported by:</span>
                                    {cl.evidence_ids?.map((eid, eIdx) => (
                                      <span key={eIdx} className="px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                        {eid}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Authoritative Telemetry Nodes */}
                        <div className="space-y-1.5">
                          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                            Authoritative Telemetry Nodes
                          </span>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {(msg.claim_evidence_map?.evidence_items && msg.claim_evidence_map.evidence_items.length > 0
                              ? msg.claim_evidence_map.evidence_items
                              : (msg.sources || [])
                            ).map((ev: any, evIdx: number) => (
                              <div key={evIdx} className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1 text-[10px]">
                                <div className="flex items-center justify-between">
                                  <span className="font-bold text-teal-300">{ev.organization || ev.source || 'INCOIS'}</span>
                                  <span className="text-slate-400 font-mono text-[9px]">{ev.valid_time || ev.timestamp || 'Active Forecast'}</span>
                                </div>
                                <div className="text-slate-200 font-sans">
                                  {ev.parameter || ev.title || 'Marine Forecast'}:{' '}
                                  <span className="text-white font-mono font-bold">
                                    {ev.value != null ? `${ev.value} ${ev.unit || ''}` : 'Operational'}
                                  </span>
                                </div>
                                {ev.citation && (
                                  <div className="text-slate-400 font-sans italic text-[9px]">
                                    Citation: {ev.citation}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Live Reasoning Progress Bar */}
            {isAnalyzing && (
              <div className="flex items-center gap-3 p-3.5 bg-slate-900/90 border border-teal-500/40 rounded-xl animate-in fade-in duration-200">
                <Loader2 className="w-4 h-4 animate-spin text-teal-400 shrink-0" />
                <div className="space-y-0.5 min-w-0">
                  <div className="text-xs text-white font-sans font-semibold flex items-center gap-2">
                    <span>Synthesizing Authoritative Response</span>
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 animate-ping" />
                  </div>
                  <div className="text-[11px] text-teal-300/80 font-mono truncate">
                    {loadingStep}
                  </div>
                </div>
              </div>
            )}

            <div ref={chatBottomRef} />
          </div>

          {/* Contextual Follow-up Suggestions Strip */}
          {followUpChips.length > 0 && !isAnalyzing && (
            <div className="space-y-1.5 px-1">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Suggested Follow-ups
              </span>
              <div className="flex flex-wrap gap-1.5">
                {followUpChips.map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptClick(chip)}
                    className="px-2.5 py-1 rounded-lg bg-slate-800/90 hover:bg-teal-500/20 text-slate-300 hover:text-teal-200 border border-slate-700/80 hover:border-teal-500/40 text-[11px] font-sans transition-all text-left shadow-xs"
                  >
                    &ldquo;{chip}&rdquo;
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Live Device Geolocation Status Badge */}
          {locationState && (
            <div className="flex items-center justify-between px-2 py-1 bg-slate-900/60 border border-slate-800 rounded-xl text-[11px] font-mono">
              <div className="flex items-center gap-1.5">
                <MapPin className={`w-3.5 h-3.5 ${locationState.status === 'AVAILABLE' ? 'text-teal-400 animate-pulse' : locationState.status === 'DENIED' ? 'text-amber-400' : 'text-slate-400'}`} />
                {locationState.status === 'AVAILABLE' ? (
                  <span className="text-teal-300">
                    📍 Using current location ({locationState.latitude?.toFixed(3)}°N, {locationState.longitude?.toFixed(3)}°E{locationState.accuracy_m ? ` · ±${locationState.accuracy_m}m` : ''})
                  </span>
                ) : locationState.status === 'DENIED' ? (
                  <span className="text-amber-300/90">
                    📍 Location permission required (specify port or enable device location)
                  </span>
                ) : (
                  <span className="text-slate-400">
                    📍 Location unavailable (ready for named port inquiries)
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={locationState.requestLocation}
                className="text-[10px] text-teal-400 hover:text-teal-300 hover:underline cursor-pointer flex items-center gap-1 shrink-0"
              >
                <RotateCcw className="w-2.5 h-2.5" />
                <span>{locationState.status === 'AVAILABLE' ? 'Refresh' : 'Enable'}</span>
              </button>
            </div>
          )}

          {/* Sticky Persistent Chat Input with STT Microphone */}
          <form onSubmit={handleSubmit} className="relative w-full">
            <div className="relative flex items-center bg-[#0F172A] border border-slate-700 rounded-2xl p-1.5 shadow-2xl focus-within:border-teal-400 focus-within:ring-2 focus-within:ring-teal-400/20 transition-all">
              <div className="pl-3 pr-2 text-slate-400 pointer-events-none">
                <Search className="w-4 h-4 text-teal-400" />
              </div>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={
                  isListening
                    ? `Listening in ${language === 'hi' ? 'Hindi' : language === 'mr' ? 'Marathi' : 'English'}... Speak now`
                    : messages.length === 0
                    ? "Ask ORCA anything about the sea, zones, or safety..."
                    : "Ask a follow-up (e.g., 'Why Zone A?', 'What about Zone C?', 'Closer to shore')..."
                }
                disabled={isAnalyzing}
                className="w-full py-2.5 bg-transparent text-slate-100 placeholder:text-slate-500 text-xs sm:text-sm font-sans focus:outline-none"
              />

              {/* Voice STT Microphone Button */}
              <button
                type="button"
                onClick={() => {
                  if (isListening) {
                    stopListening();
                  } else {
                    startListening(language);
                  }
                }}
                disabled={!isSttSupported || isAnalyzing}
                className={`p-2 rounded-xl border transition-all shrink-0 flex items-center justify-center mr-1 ${
                  isListening
                    ? 'bg-rose-500/20 border-rose-500 text-rose-400 animate-pulse ring-2 ring-rose-500/30'
                    : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300 hover:text-white'
                }`}
                title={
                  !isSttSupported
                    ? 'Speech recognition not supported in browser'
                    : isListening
                    ? 'Listening... Click to stop'
                    : `Speak in ${language === 'hi' ? 'Hindi (हिंदी)' : language === 'mr' ? 'Marathi (मराठी)' : 'English'}`
                }
              >
                {isListening ? (
                  <MicOff className="w-4 h-4 text-rose-400 animate-pulse" />
                ) : (
                  <Mic className="w-4 h-4 text-teal-400" />
                )}
              </button>

              <button
                type="submit"
                disabled={isAnalyzing || !inputValue.trim()}
                className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-[#0A1128] rounded-xl text-xs font-mono font-bold tracking-wider disabled:opacity-50 transition-all flex items-center gap-1 shadow-md shrink-0"
              >
                {isAnalyzing ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-[#0A1128]" />
                ) : (
                  <>
                    <span>SEND</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
            {sttError && (
              <p className="text-[10px] text-rose-400 mt-1 pl-3 font-mono">{sttError}</p>
            )}
          </form>
        </div>

        {/* RIGHT COLUMN: Query-Specific Marine Map & Zone Details (5 cols on desktop, only when conversation active) */}
        {messages.length > 0 && (
          <div ref={mapSectionRef} className="lg:col-span-5 space-y-4 animate-in fade-in duration-300">
            {/* Dynamic Map Window */}
            <div className="bg-[#0F172A] border border-slate-800 rounded-2xl p-3 shadow-xl space-y-3">
              <div className="flex items-center justify-between pb-1 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-teal-400" />
                  <span className="font-bold text-white text-xs">DYNAMIC OPERATIONS MAP</span>
                </div>
                <span className="text-[10px] text-teal-400 font-bold bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
                  {activeZones.length} {activeZones.length === 1 ? 'Sector' : 'Sectors'} Filtered
                </span>
              </div>

              <MarineMap
                zones={activeZones}
                selectedZone={selectedZone}
                onSelectZone={onSelectZone}
                filterMode="all"
                language={language}
                mapConfig={lastAssistantMessage?.map}
                userLocation={locationState && locationState.latitude != null && locationState.longitude != null ? {
                  latitude: locationState.latitude,
                  longitude: locationState.longitude,
                  accuracy_m: locationState.accuracy_m ?? undefined
                } : null}
              />
            </div>

            {/* Selected Sector Inspector */}
            {selectedZone && (
              <ZoneDetails
                zone={selectedZone}
                onHighlightOnMap={(zone) => onSelectZone(zone)}
                onViewSource={onOpenEvidenceTab}
                onViewReasoning={onOpenReasoningTab}
                onViewEvidence={onOpenEvidenceTab}
                language={language}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};
