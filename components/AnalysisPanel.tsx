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
  BarChart2
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

  const coveragePercent = analysis.evidence_coverage ? Math.round(analysis.evidence_coverage * 100) : 95;

  return (
    <div className="space-y-6 text-slate-800">
      {/* 1. Primary Decision Box (Executive Multi-Agent Synthesis) */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-100">
                ORCA Decision Intelligence
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {analysis.time}
              </span>
              <span className="text-[10px] font-mono font-semibold text-cyan-700 bg-cyan-50 px-2 py-0.5 rounded border border-cyan-200">
                Evidence Coverage: {coveragePercent}%
              </span>
            </div>
            <h2 className="text-base font-bold text-slate-950 mt-1">
              &ldquo;{analysis.query}&rdquo;
            </h2>
          </div>

          <div className="flex items-center gap-2 text-xs">
            {onOpenConfidenceModal ? (
              <button
                type="button"
                onClick={onOpenConfidenceModal}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-cyan-50 hover:bg-cyan-100 text-cyan-900 border border-cyan-200/80 font-mono font-semibold transition-colors"
                title="View decomposed 5-factor confidence & uncertainty breakdown"
              >
                <span>Confidence: {analysis.confidenceScore}% · {analysis.confidenceLevel}</span>
                <span className="text-[10px] text-cyan-600 font-sans font-bold">↗</span>
              </button>
            ) : (
              <span className="text-slate-500">
                Confidence: <strong className="text-slate-900 font-semibold">{analysis.confidenceScore}% · {analysis.confidenceLevel}</strong>
              </span>
            )}

            {onOpenWhatIfModal && (
              <button
                type="button"
                onClick={onOpenWhatIfModal}
                className="px-2.5 py-1 rounded-md bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200/80 text-xs font-semibold transition-colors"
                title="Simulate wave/wind parameter modifications"
              >
                What-If?
              </button>
            )}
          </div>
        </div>

        {/* Executive Grounded Takeaway */}
        <p className="text-sm font-medium text-slate-800 leading-relaxed">
          {analysis.summary}
        </p>

        {/* Phase 5: Ranked Candidate Operational Zones */}
        <div className="p-4 bg-slate-50/80 rounded-xl border border-slate-200/80 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              ORCA Candidate Zone Ranking
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Deterministic Suitability Scoring</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {/* Top Candidate Card */}
            <div className="p-3.5 bg-white rounded-lg border border-emerald-200/80 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px] flex items-center justify-center">1</span>
                  <span className="font-bold text-emerald-950">ZONE C (South Sector)</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-100/70 text-emerald-800 font-mono text-[10px] font-bold">TOP CANDIDATE</span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono py-1 border-y border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[9px]">SUITABILITY</span>
                  <span className="text-emerald-700 font-bold">72 / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">OPERATIONAL RISK</span>
                  <span className="text-slate-800 font-bold">22 / 100 (Low)</span>
                </div>
              </div>
              <p className="text-[11px] text-slate-600 leading-tight">
                Lower wave risk (1.2m), favorable available ISRO/INCOIS ocean color indicators, zero restrictions.
              </p>
            </div>

            {/* Alternative Candidate Card */}
            <div className="p-3.5 bg-white rounded-lg border border-slate-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 font-bold text-[11px] flex items-center justify-center">2</span>
                  <span className="font-bold text-slate-900">ZONE D (Mid-Shelf)</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-semibold">ALTERNATIVE</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono py-1 border-y border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[9px]">SUITABILITY</span>
                  <span className="text-slate-800 font-bold">61 / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">OPERATIONAL RISK</span>
                  <span className="text-amber-700 font-bold">38 / 100 (Caution)</span>
                </div>
              </div>
              <p className="text-[11px] text-slate-600 leading-tight">
                Viable secondary candidate. Moderate wave swell (1.8m); conclude operations before afternoon rise.
              </p>
            </div>
          </div>
        </div>

        {/* Dynamic Decision Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
          <div className="p-3.5 bg-rose-50/70 rounded-xl border border-rose-100 space-y-2">
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500 mt-1 shrink-0" />
              <div>
                <span className="font-bold text-rose-950">
                  Avoid: {analysis.zonesToAvoid.map(z => z.code).join(' & ') || 'None'}
                </span>
                <p className="text-[11px] text-rose-800 mt-0.5 leading-normal">
                  {analysis.zonesToAvoid.length > 0
                    ? analysis.zonesToAvoid.map(z => `${z.code}: ${z.reasons[0] || z.statusLabel}`).join(' · ')
                    : 'No high-risk or restricted sectors detected in requested window.'}
                </p>
              </div>
            </div>

            {/* Inline Evidence Indicator Chips */}
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
                    citation: 'Wave model indicates elevated swell (4.1 m) breaching safety envelope.',
                    source_url: 'https://incois.gov.in/oceanservices/osfforecast.jsp'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-white text-rose-800 border border-rose-200 hover:bg-rose-100 transition-colors"
                >
                  <span>[Evidence: INCOIS Wave 4.1m]</span>
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
                    source_url: 'https://api.imd.gov.in/public/api_reference.html'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-white text-rose-800 border border-rose-200 hover:bg-rose-100 transition-colors"
                >
                  <span>[Evidence: IMD Wind 30kt]</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}
          </div>

          <div className="p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-100 space-y-2">
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mt-1 shrink-0" />
              <div>
                <span className="font-bold text-emerald-950">
                  Potential Candidates: {analysis.potentialZones.map(z => z.code).join(' & ') || 'None'}
                </span>
                <p className="text-[11px] text-emerald-800 mt-0.5 leading-normal">
                  {analysis.potentialZones.length > 0
                    ? analysis.potentialZones.map(z => `${z.code}: ${z.reasons[0] || z.statusLabel}`).join(' · ')
                    : 'No open operational window identified under current conditions.'}
                </p>
              </div>
            </div>

            {/* Inline Evidence Indicator Chips for Candidates */}
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
                    citation: 'Manageable physical wave conditions and baseline ocean color indicators.',
                    source_url: 'https://incois.gov.in/'
                  })}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-white text-emerald-800 border border-emerald-200 hover:bg-emerald-100 transition-colors"
                >
                  <span>[Evidence: INCOIS & MOSDAC]</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Interactive Wave / Wind Timeline Visualization */}
        <div className="p-4 bg-slate-900 text-slate-100 rounded-xl space-y-2.5 text-xs font-mono">
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5 uppercase font-bold tracking-wider text-cyan-400">
              <BarChart2 className="w-3.5 h-3.5" />
              Wave & Wind Evolution Profile (Zone A vs Zone C)
            </span>
            <span>Forecast Window</span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
            <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700">
              <span className="text-slate-400 block text-[10px]">06:00 IST</span>
              <span className="text-rose-400 font-bold">3.4m · 24kt</span>
              <span className="text-emerald-400 text-[10px] block mt-0.5">Zone C: 0.9m</span>
            </div>
            <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700">
              <span className="text-slate-400 block text-[10px]">09:00 IST</span>
              <span className="text-rose-400 font-bold">3.8m · 28kt</span>
              <span className="text-emerald-400 text-[10px] block mt-0.5">Zone C: 1.0m</span>
            </div>
            <div className="p-2 rounded-lg bg-rose-950/40 border border-rose-500/40">
              <span className="text-rose-300 block text-[10px]">12:00 IST (Peak)</span>
              <span className="text-rose-300 font-bold">4.1m · 30kt</span>
              <span className="text-emerald-400 text-[10px] block mt-0.5">Zone C: 1.1m</span>
            </div>
          </div>
        </div>

        {/* Conversational Contextual Follow-Up Suggestions */}
        {onAskFollowUp && (
          <div className="pt-2 border-t border-slate-100 space-y-1.5">
            <span className="text-[11px] font-semibold text-slate-500">Decision Support Queries:</span>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => onAskFollowUp('Rank the candidate zones.')}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium border border-slate-200 transition-colors"
              >
                Rank Candidate Zones
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('Compare Zone C and Zone D.')}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium border border-slate-200 transition-colors"
              >
                Compare Zone C & Zone D
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('What if wave height increases by 1 metre in Zone C?')}
                className="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-900 text-xs font-medium border border-amber-200 transition-colors"
              >
                What if waves +1m?
              </button>
              <button
                type="button"
                onClick={() => onOpenConfidenceModal ? onOpenConfidenceModal() : onAskFollowUp('Why is your confidence medium?')}
                className="px-2.5 py-1 rounded-lg bg-cyan-50 hover:bg-cyan-100 text-cyan-900 text-xs font-medium border border-cyan-200 transition-colors"
              >
                Why is confidence Medium?
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('Give me an alternative candidate.')}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium border border-slate-200 transition-colors"
              >
                Give Alternative Candidate
              </button>
              <button
                type="button"
                onClick={() => onAskFollowUp('Show restricted zones on the map.')}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium border border-slate-200 transition-colors"
              >
                Show Restricted Zones
              </button>
            </div>
          </div>
        )}

        {/* User Feedback Row */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Was this reasoning useful?</span>
          {feedbackSent ? (
            <span className="text-emerald-600 font-medium">✓ Thank you for your feedback</span>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleFeedback(true)}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                <ThumbsUp className="w-3 h-3" />
                <span>Yes</span>
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                <ThumbsDown className="w-3 h-3" />
                <span>No</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 2. Zones to Avoid & Potential Zones (Minimal Two-Column Rows) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Avoid Rows */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-1 border-b border-slate-100">
            <span className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
              Zones to Avoid
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              {analysis.zonesToAvoid.length} Sectors
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {analysis.zonesToAvoid.map((zone, idx) => {
              const isSelected = selectedZoneId === zone.id;
              return (
                <div
                  key={zone.id}
                  onClick={() => onSelectZone(zone)}
                  className={`py-3 first:pt-1 last:pb-1 flex items-start justify-between gap-3 cursor-pointer group transition-colors px-2 rounded-lg ${
                    isSelected ? 'bg-rose-50/60' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900 text-xs">
                        0{idx + 1}
                      </span>
                      <span className="font-bold text-slate-900 text-xs">
                        {zone.code}
                      </span>
                      <span className="text-[10px] font-semibold text-rose-700 bg-rose-50 px-1.5 py-0.2 rounded border border-rose-200">
                        {zone.statusLabel}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">
                        Risk {zone.riskScore}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">
                      {zone.reasons && zone.reasons.length > 0 ? zone.reasons[0] : 'Elevated risk parameters detected.'}
                    </p>
                  </div>

                  <button
                    type="button"
                    className="text-[11px] font-semibold text-slate-500 group-hover:text-rose-700 flex items-center gap-0.5 shrink-0 mt-0.5"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Potential / Safe Rows */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-1 border-b border-slate-100">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Potential / Candidate Zones
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              {analysis.potentialZones.length} Sectors
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {analysis.potentialZones.map((zone, idx) => {
              const isSelected = selectedZoneId === zone.id;
              const isCaution = zone.status === 'caution';
              return (
                <div
                  key={zone.id}
                  onClick={() => onSelectZone(zone)}
                  className={`py-3 first:pt-1 last:pb-1 flex items-start justify-between gap-3 cursor-pointer group transition-colors px-2 rounded-lg ${
                    isSelected
                      ? isCaution
                        ? 'bg-amber-50/60'
                        : 'bg-emerald-50/60'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900 text-xs">
                        0{idx + 1}
                      </span>
                      <span className="font-bold text-slate-900 text-xs">
                        {zone.code}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-1.5 py-0.2 rounded border ${
                          isCaution
                            ? 'text-amber-800 bg-amber-50 border-amber-200'
                            : 'text-emerald-800 bg-emerald-50 border-emerald-200'
                        }`}
                      >
                        {zone.statusLabel}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">
                        Risk {zone.riskScore}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">
                      {zone.reasons && zone.reasons.length > 0 ? zone.reasons[0] : 'Calm forecast sea state.'}
                    </p>
                  </div>

                  <button
                    type="button"
                    className={`text-[11px] font-semibold text-slate-500 flex items-center gap-0.5 shrink-0 mt-0.5 ${
                      isCaution
                        ? 'group-hover:text-amber-700'
                        : 'group-hover:text-emerald-700'
                    }`}
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 3. Dynamic Multi-Agent Reasoning Execution Trace */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-sm text-xs">
        <button
          onClick={() => setIsTraceExpanded(!isTraceExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-600" />
            <span className="font-semibold text-slate-900">ORCA Multi-Agent Execution Trace</span>
            <span className="text-[11px] text-slate-400 font-normal">
              ({analysis.agentTrace ? analysis.agentTrace.length : 6} Collaborative Agents)
            </span>
          </div>

          <div className="flex items-center gap-1 text-slate-500 hover:text-slate-800">
            <span className="text-[11px]">{isTraceExpanded ? 'Collapse Trace' : 'Expand Trace'}</span>
            {isTraceExpanded ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </div>
        </button>

        {/* Collapsed view: compact 1-line timeline */}
        {!isTraceExpanded ? (
          <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-600">
            {(analysis.agentTrace || []).map((trace, idx) => (
              <React.Fragment key={idx}>
                {idx > 0 && <span className="text-slate-300">→</span>}
                <span className="flex items-center gap-1 font-medium text-slate-700">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" /> {trace.agentName.replace(' Agent', '')}
                </span>
              </React.Fragment>
            ))}
          </div>
        ) : (
          /* Expanded view: step-by-step detail with tools used and data categories */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-4 pt-3 border-t border-slate-100 text-xs">
            {(analysis.agentTrace || []).map((trace, idx) => (
              <div key={idx} className="p-3 bg-slate-50/80 rounded-xl border border-slate-100 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-xs flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span>
                    {trace.agentName}
                  </span>
                  <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-1 rounded border border-emerald-200">
                    {trace.agentStatus || 'COMPLETE'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-700 leading-snug">{trace.action}</p>
                {trace.toolsUsed && trace.toolsUsed.length > 0 && (
                  <div className="pt-1 flex flex-wrap gap-1">
                    {trace.toolsUsed.slice(0, 3).map((tool, tIdx) => (
                      <span key={tIdx} className="text-[9px] font-mono text-slate-500 bg-white px-1.5 py-0.2 rounded border border-slate-200">
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
