'use client';

import React, { useState } from 'react';
import { ORCAAnalysisResult, MarineZone, EvidenceGraphNode } from '@/types/marine';
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Clock,
  ExternalLink,
  Waves,
  Wind,
  HelpCircle,
  ThumbsUp,
  ThumbsDown,
  BarChart2,
  SlidersHorizontal,
  Compass,
  AlertTriangle,
  Info
} from 'lucide-react';
import { submitUserFeedback } from '@/lib/apiClient';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface AnalysisPanelProps {
  analysis: ORCAAnalysisResult;
  onSelectZone: (zone: MarineZone) => void;
  selectedZoneId?: string;
  onInspectEvidence?: (evidence: any) => void;
  onAskFollowUp?: (query: string) => void;
  onOpenConfidenceModal?: () => void;
  onOpenWhatIfModal?: () => void;
  language?: string;
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  analysis,
  onSelectZone,
  selectedZoneId,
  onInspectEvidence,
  onAskFollowUp,
  onOpenConfidenceModal,
  onOpenWhatIfModal,
  language = 'en',
}) => {
  const [isTraceExpanded, setIsTraceExpanded] = useState<boolean>(false);
  const [feedbackSent, setFeedbackSent] = useState<boolean>(false);
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  const handleFeedback = async (useful: boolean) => {
    await submitUserFeedback(analysis.query, useful, 5);
    setFeedbackSent(true);
  };

  const coveragePercent = analysis.evidence_coverage ? Math.round(analysis.evidence_coverage * 100) : 100;

  return (
    <div className="space-y-4 text-slate-200 font-mono text-xs">
      {/* 1. Compact Horizontal Decision Summary Strip */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-3 shadow-md grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center">
        <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
          <span className="text-[10px] text-rose-300 font-bold block uppercase">AVOID</span>
          <span className="text-sm font-bold text-rose-400 font-mono-num mt-0.5 block">
            {analysis.zonesToAvoid.length} {analysis.zonesToAvoid.length === 1 ? 'ZONE' : 'ZONES'}
          </span>
        </div>

        <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <span className="text-[10px] text-emerald-300 font-bold block uppercase">CANDIDATE</span>
          <span className="text-sm font-bold text-emerald-400 font-mono-num mt-0.5 block">
            {analysis.potentialZones.filter(z => z.status === 'suitable' || z.status === 'suitable_candidate').length} ZONE
          </span>
        </div>

        <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
          <span className="text-[10px] text-amber-300 font-bold block uppercase">CAUTION</span>
          <span className="text-sm font-bold text-amber-400 font-mono-num mt-0.5 block">
            {analysis.potentialZones.filter(z => z.status === 'caution').length} ZONE
          </span>
        </div>

        <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
          <span className="text-[10px] text-indigo-300 font-bold block uppercase">RESTRICTED</span>
          <span className="text-sm font-bold text-indigo-400 font-mono-num mt-0.5 block">
            1 ZONE
          </span>
        </div>

        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 cursor-pointer hover:bg-cyan-500/20 transition-colors"
          onClick={onOpenConfidenceModal}
          title="Click to view confidence & uncertainty methodology"
        >
          <span className="text-[10px] text-cyan-300 font-bold block uppercase">CONFIDENCE</span>
          <span className="text-sm font-bold text-cyan-400 font-mono-num mt-0.5 block">
            {analysis.confidenceScore}% · HIGH
          </span>
        </div>

        <div className="p-2 rounded-lg bg-teal-500/10 border border-teal-500/20">
          <span className="text-[10px] text-teal-300 font-bold block uppercase">EVIDENCE</span>
          <span className="text-sm font-bold text-teal-400 font-mono-num mt-0.5 block">
            {coveragePercent}% COVERAGE
          </span>
        </div>
      </div>

      {/* 2. Executive Decision & Ranked Candidates */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-300 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
              ORCA EXECUTIVE SYNTHESIS
            </span>
            <span className="text-[10px] text-slate-400">
              {analysis.time || '10:35 IST'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {onOpenConfidenceModal && (
              <button
                type="button"
                onClick={onOpenConfidenceModal}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold transition-colors"
              >
                <span>Confidence: {analysis.confidenceScore}%</span>
                <span className="text-[10px]">↗</span>
              </button>
            )}

            {onOpenWhatIfModal && (
              <button
                type="button"
                onClick={onOpenWhatIfModal}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-bold transition-colors"
              >
                <SlidersHorizontal className="w-3 h-3 text-amber-400" />
                <span>What-If?</span>
              </button>
            )}
          </div>
        </div>

        {/* Executive Grounded Takeaway */}
        <p className="text-xs sm:text-sm font-sans font-medium text-slate-100 leading-relaxed">
          {analysis.summary}
        </p>

        {/* Ranked Operational Candidates */}
        <div className="space-y-2.5 pt-1">
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Candidate Zone Ranking (Deterministic Suitability)
            </span>
            <span className="text-[10px] text-slate-400">INCOIS OSF / PFZ Telemetry</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Top Candidate */}
            <div
              onClick={() => {
                const zc = analysis.potentialZones.find(z => z.id === 'zone-c') || analysis.potentialZones[0];
                if (zc) onSelectZone(zc);
              }}
              className="p-3 bg-slate-900/90 rounded-lg border border-emerald-500/40 hover:border-emerald-400 cursor-pointer transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-300 font-bold text-[10px] flex items-center justify-center border border-emerald-500/40">1</span>
                  <span className="font-bold text-emerald-300">ZONE C (South Sector)</span>
                </div>
                <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold border border-emerald-500/40">
                  TOP CANDIDATE
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px] py-1 border-y border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[9px]">SUITABILITY</span>
                  <span className="text-emerald-400 font-bold">72 / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">OPERATIONAL RISK</span>
                  <span className="text-slate-200 font-bold">22 / 100 (Low)</span>
                </div>
              </div>

              <p className="text-[10px] font-sans text-slate-300 leading-snug">
                Favorable wave conditions (1.2m swell), baseline ocean color indicators, unrestricted passage.
              </p>
            </div>

            {/* Alternative Candidate */}
            <div
              onClick={() => {
                const zd = analysis.potentialZones.find(z => z.id === 'zone-d') || analysis.potentialZones[1];
                if (zd) onSelectZone(zd);
              }}
              className="p-3 bg-slate-900/90 rounded-lg border border-slate-700 hover:border-slate-600 cursor-pointer transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full bg-slate-800 text-slate-300 font-bold text-[10px] flex items-center justify-center border border-slate-700">2</span>
                  <span className="font-bold text-slate-200">ZONE D (Mid-Shelf)</span>
                </div>
                <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold border border-amber-500/40">
                  ALTERNATIVE
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px] py-1 border-y border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[9px]">SUITABILITY</span>
                  <span className="text-slate-200 font-bold">61 / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">OPERATIONAL RISK</span>
                  <span className="text-amber-400 font-bold">38 / 100 (Caution)</span>
                </div>
              </div>

              <p className="text-[10px] font-sans text-slate-300 leading-snug">
                Viable secondary candidate. Moderate wave swell (1.8m); conclude operations before afternoon rise.
              </p>
            </div>
          </div>
        </div>

        {/* Why This Decision Summary Rows */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {/* Avoid Summary */}
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 space-y-2">
            <div className="flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-rose-300 text-[11px]">
                  AVOID: {analysis.zonesToAvoid.map(z => z.code).join(' & ') || 'None'}
                </span>
                <p className="text-[10px] font-sans text-rose-200 mt-0.5 leading-snug">
                  {analysis.zonesToAvoid.length > 0
                    ? analysis.zonesToAvoid.map(z => `${z.code}: ${z.reasons[0] || z.statusLabel}`).join(' · ')
                    : 'No critical hazards detected.'}
                </p>
              </div>
            </div>

            {onInspectEvidence && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                <button
                  type="button"
                  onClick={() => onInspectEvidence({
                    parameter: 'Significant Wave Height',
                    value: '4.1 m',
                    organization: 'INCOIS Wave Watch III',
                    data_type: 'forecast',
                    valid_time: 'Tomorrow 06:00 IST',
                    citation: 'Wave model indicates elevated swell (4.1 m) breaching safety threshold.',
                    source_url: 'https://incois.gov.in/oceanservices/osfforecast.jsp'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] bg-slate-900 text-rose-300 border border-rose-500/30 hover:bg-slate-800 transition-colors"
                >
                  <span>[INCOIS Wave 4.1m]</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
                <button
                  type="button"
                  onClick={() => onInspectEvidence({
                    parameter: 'Coastal Wind Telemetry',
                    value: '30.0 kt',
                    organization: 'IMD Marine Division',
                    data_type: 'forecast',
                    valid_time: 'Tomorrow 06:00 IST',
                    citation: 'Sustained near-gale winds (30.0 kt) forecast across northern shelf.',
                    source_url: 'https://api.imd.gov.in/public/index.php'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] bg-slate-900 text-rose-300 border border-rose-500/30 hover:bg-slate-800 transition-colors"
                >
                  <span>[IMD Wind 30kt]</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}
          </div>

          {/* Candidate Summary */}
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 space-y-2">
            <div className="flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-emerald-300 text-[11px]">
                  CANDIDATES: {analysis.potentialZones.map(z => z.code).join(' & ') || 'None'}
                </span>
                <p className="text-[10px] font-sans text-emerald-200 mt-0.5 leading-snug">
                  {analysis.potentialZones.length > 0
                    ? analysis.potentialZones.map(z => `${z.code}: ${z.reasons[0] || z.statusLabel}`).join(' · ')
                    : 'No open operational window identified under current conditions.'}
                </p>
              </div>
            </div>

            {onInspectEvidence && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                <button
                  type="button"
                  onClick={() => onInspectEvidence({
                    parameter: 'Sea State & Ocean Color',
                    value: '1.0 m · 0.8 mg/m³',
                    organization: 'INCOIS & MOSDAC',
                    data_type: 'forecast & observation',
                    valid_time: 'Tomorrow 06:00 IST',
                    citation: 'Manageable wave conditions and baseline ocean color indicators.',
                    source_url: 'https://incois.gov.in/'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] bg-slate-900 text-emerald-300 border border-emerald-500/30 hover:bg-slate-800 transition-colors"
                >
                  <span>[INCOIS & MOSDAC Data]</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Forecast Evolution Timeline */}
        <div className="p-3.5 bg-slate-900/90 rounded-lg border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-[10px] text-slate-400">
            <span className="flex items-center gap-1.5 uppercase font-bold text-teal-400">
              <BarChart2 className="w-3.5 h-3.5" />
              Forecast Evolution Profile (Zone A vs Zone C)
            </span>
            <span>Forecast Window (IST)</span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
            <div className="p-2 rounded bg-slate-800/80 border border-slate-700">
              <span className="text-slate-400 block text-[9px]">06:00 IST</span>
              <span className="text-rose-400 font-bold block">Zone A: 3.4m · 24kt</span>
              <span className="text-emerald-400 block mt-0.5">Zone C: 0.9m · 12kt</span>
            </div>
            <div className="p-2 rounded bg-slate-800/80 border border-slate-700">
              <span className="text-slate-400 block text-[9px]">09:00 IST</span>
              <span className="text-rose-400 font-bold block">Zone A: 3.8m · 28kt</span>
              <span className="text-emerald-400 block mt-0.5">Zone C: 1.0m · 14kt</span>
            </div>
            <div className="p-2 rounded bg-rose-500/10 border border-rose-500/30">
              <span className="text-rose-300 block text-[9px]">12:00 IST (Peak Swell)</span>
              <span className="text-rose-300 font-bold block">Zone A: 4.1m · 30kt</span>
              <span className="text-emerald-400 block mt-0.5">Zone C: 1.1m · 15kt</span>
            </div>
          </div>
        </div>

        {/* Decision Support Follow-Up Query Chips */}
        {onAskFollowUp && (
          <div className="pt-2 border-t border-slate-800 space-y-1.5">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">
              Follow-Up Decision Inquiries:
            </span>
            <div className="flex flex-wrap items-center gap-1.5">
              <button
                type="button"
                onClick={() => onAskFollowUp('Rank candidate fishing zones.')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
              >
                Rank Candidate Zones
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('Compare Zone C and Zone D.')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
              >
                Compare Zone C & Zone D
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('What if wave height increases by 1 metre in Zone C?')}
                className="px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-[11px] border border-amber-500/30 transition-colors"
              >
                What if waves +1m?
              </button>
              <button
                type="button"
                onClick={() => onOpenConfidenceModal ? onOpenConfidenceModal() : onAskFollowUp('Why is confidence High?')}
                className="px-2.5 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-[11px] border border-cyan-500/30 transition-colors"
              >
                Why is confidence High?
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('Show restricted zones on the map.')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
              >
                Show Restricted Zones
              </button>
            </div>
          </div>
        )}

        {/* User Grounding Feedback */}
        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <span>Was this decision reasoning accurate & useful?</span>
          {feedbackSent ? (
            <span className="text-emerald-400 font-bold">✓ Feedback recorded</span>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleFeedback(true)}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700"
              >
                <ThumbsUp className="w-3 h-3 text-emerald-400" />
                <span>Yes</span>
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700"
              >
                <ThumbsDown className="w-3 h-3 text-rose-400" />
                <span>No</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 3. Horizontal Multi-Agent Pipeline Execution Trace */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-3.5 shadow-md space-y-2">
        <button
          onClick={() => setIsTraceExpanded(!isTraceExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-400" />
            <span className="font-bold text-white text-[11px] uppercase tracking-wider">
              ORCA Multi-Agent Execution Pipeline
            </span>
            <span className="text-[10px] text-slate-400">
              (6 Collaborative Specialized Agents)
            </span>
          </div>

          <div className="flex items-center gap-1 text-slate-400 hover:text-slate-200">
            <span className="text-[10px]">{isTraceExpanded ? 'Collapse Trace' : 'View Trace'}</span>
            {isTraceExpanded ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </div>
        </button>

        {/* Compact 1-line pipeline view */}
        {!isTraceExpanded ? (
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800 text-[10px]">
            {(analysis.agentTrace || []).map((trace, idx) => (
              <React.Fragment key={idx}>
                {idx > 0 && <span className="text-slate-600">→</span>}
                <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 font-bold">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  {trace.agentName.replace(' Agent', '')}
                </span>
              </React.Fragment>
            ))}
          </div>
        ) : (
          /* Expanded detail with tools and timings */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2 border-t border-slate-800 text-xs">
            {(analysis.agentTrace || []).map((trace, idx) => (
              <div key={idx} className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-teal-300 text-[11px]">
                    {trace.agentName}
                  </span>
                  <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 px-1 rounded border border-emerald-500/30">
                    {trace.agentStatus || 'COMPLETE'}
                  </span>
                </div>
                <p className="text-[10px] font-sans text-slate-300 leading-snug">{trace.action}</p>
                {trace.toolsUsed && trace.toolsUsed.length > 0 && (
                  <div className="pt-1 flex flex-wrap gap-1">
                    {trace.toolsUsed.map((tool, tIdx) => (
                      <span key={tIdx} className="text-[8px] text-slate-400 bg-slate-800 px-1 py-0.2 rounded border border-slate-700">
                        {tool}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
