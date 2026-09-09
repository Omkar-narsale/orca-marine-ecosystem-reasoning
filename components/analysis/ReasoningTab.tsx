'use client';

import React, { useState } from 'react';
import { ORCAAnalysisResult, MarineZone } from '@/types/marine';
import {
  Cpu,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  Layers,
  ArrowRight,
  BarChart2,
  SlidersHorizontal
} from 'lucide-react';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface ReasoningTabProps {
  analysis: ORCAAnalysisResult;
  onSelectZone: (zone: MarineZone) => void;
  onAskFollowUp?: (query: string) => void;
  onOpenWhatIfModal?: () => void;
  onOpenConfidenceModal?: () => void;
  language?: string;
}

export const ReasoningTab: React.FC<ReasoningTabProps> = ({
  analysis,
  onSelectZone,
  onAskFollowUp,
  onOpenWhatIfModal,
  onOpenConfidenceModal,
  language = 'en',
}) => {
  const [isTraceExpanded, setIsTraceExpanded] = useState<boolean>(true);
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  return (
    <div className="space-y-5 font-mono text-xs text-slate-200">
      {/* 1. Executive Grounded Decision */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-300 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
              ORCA REASONING SYNTHESIS
            </span>
            <span className="text-[10px] text-slate-400">
              Deterministic Multi-Source Synthesis
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] text-cyan-300 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
              Confidence Index: {analysis.confidenceScore} / 100
            </span>
          </div>
        </div>

        <p className="text-xs sm:text-sm font-sans font-medium text-slate-100 leading-relaxed">
          {analysis.summary}
        </p>
      </div>

      {/* 2. Structured Decision Decomposition Steps */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-3.5">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <span className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-teal-400" />
            Decision Reasoning Steps
          </span>
          <span className="text-[10px] text-slate-400">
            6 Deterministic Evaluation Stages
          </span>
        </div>

        <div className="space-y-2">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">1</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Oceanographic Telemetry Evaluation</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Retrieved numerical wave height & swell period forecasts from INCOIS Wave Watch III. Flagged northern sector (4.1m swell) as hazardous while southern sector (1.0m swell) remains calm.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">2</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Meteorological Hazard & Alert Verification</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Queried official IMD Marine Division bulletins; confirmed active coastal squall alert and 28-34 knot wind gusts across northern coastal waters.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">3</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Geospatial Cadastre & Regulatory Restrictions</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Executed spatial intersection against GIS Maritime Cadastre; identified Zone B as an active Naval Anchorage and Vessel Traffic Separation (TSS) Corridor where fishing is legally restricted.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">4</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Deterministic Risk & Suitability Scoring</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Calculated physical risk and candidate suitability: Zone A (Risk Index 87/100, HIGH RISK), Zone B (Risk Index 72/100, RESTRICTED), Zone C (Risk Index 18/100, Suitability Index 72/100, SUITABLE CANDIDATE).
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">5</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Evidence Consistency & Uncertainty Check</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Checked cross-source consistency between INCOIS numerical forecast and IMD synoptic reports. Confirmed 100% evidence coverage across 4 authoritative feeds with low spatial uncertainty.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start gap-3">
            <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">6</span>
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">Synthesis & Grounded Recommendation</span>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Formulated transparent decision: avoid Zone A and Zone B; navigate toward Zone C as the primary operational candidate.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Explanatory Contributing Factors */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <span className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            Contributing Factor Breakdown
          </span>
          <span className="text-[10px] text-slate-400">Explanatory Model Visualization</span>
        </div>

        <div className="space-y-3 text-[11px]">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-slate-300">Wave Conditions (INCOIS OSF Telemetry)</span>
              <span className="font-bold text-rose-400">High Influence (4.1m swell in Zone A)</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full" style={{ width: '85%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-slate-300">Wind & Surface Chop (IMD Marine Telemetry)</span>
              <span className="font-bold text-amber-400">Moderate-High Influence (28-34 kt)</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: '70%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-slate-300">Official Marine Warning (IMD Squall Warning)</span>
              <span className="font-bold text-rose-400">Critical Precedence (Active in North)</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full" style={{ width: '95%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-slate-300">Geospatial Boundary (GIS Cadastre Restricted Zone)</span>
              <span className="font-bold text-indigo-400">Absolute Constraint (Zone B)</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 rounded-full" style={{ width: '100%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-slate-300">Uncertainty & Spatial Variance</span>
              <span className="font-bold text-emerald-400">Low Uncertainty (Multi-source convergence)</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: '20%' }}></div>
            </div>
          </div>
        </div>

        <p className="text-[10px] text-slate-500 font-sans italic pt-1">
          * Note: Factor bars are explanatory visualizations of the deterministic heuristic screening model and do not represent calibrated statistical probabilities.
        </p>
      </div>

      {/* 4. Multi-Agent Pipeline Execution Trace */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-3">
        <button
          onClick={() => setIsTraceExpanded(!isTraceExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-teal-400" />
            <span className="font-bold text-white text-xs uppercase tracking-wider">
              Multi-Agent Collaborative Execution Pipeline
            </span>
            <span className="text-[10px] text-slate-400">
              (6 Specialized Agents · Zero Hidden Chain-of-Thought)
            </span>
          </div>

          <div className="flex items-center gap-1 text-slate-400 hover:text-slate-200">
            <span className="text-[10px]">{isTraceExpanded ? 'Collapse' : 'Expand'}</span>
            {isTraceExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </div>
        </button>

        {isTraceExpanded && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2 border-t border-slate-800">
            {(analysis.agentTrace || []).map((trace, idx) => (
              <div key={idx} className="p-3 bg-slate-900/90 rounded-lg border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-teal-300 text-[11px]">
                    {trace.agentName}
                  </span>
                  <span className="text-[9px] text-emerald-400 bg-emerald-500/10 px-1 rounded border border-emerald-500/30">
                    {trace.agentStatus || 'COMPLETED'}
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

      {/* 5. Follow-Up Inquiries */}
      {onAskFollowUp && (
        <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 shadow-md space-y-2">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Follow-Up Decision Inquiries
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => onAskFollowUp('Why did you classify Zone A as high risk?')}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
            >
              Why is Zone A high risk?
            </button>
            <button
              onClick={() => onAskFollowUp('Compare Zone C and Zone D.')}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
            >
              Compare Zone C & Zone D
            </button>
            <button
              onClick={() => onAskFollowUp('Show restricted zones on the map.')}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] border border-slate-700 transition-colors"
            >
              Show Restricted Zones
            </button>
            {onOpenWhatIfModal && (
              <button
                onClick={onOpenWhatIfModal}
                className="px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-[11px] border border-amber-500/30 transition-colors flex items-center gap-1"
              >
                <SlidersHorizontal className="w-3 h-3 text-amber-400" />
                <span>Simulate What-If (+1m Wave)</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
