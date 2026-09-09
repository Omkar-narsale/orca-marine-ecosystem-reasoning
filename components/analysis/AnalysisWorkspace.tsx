'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { MarineZone, ORCAAnalysisResult, EvidenceSource } from '@/types/marine';
import { ZoneDetails } from '@/components/ZoneDetails';
import { ReasoningTab } from './ReasoningTab';
import { EvidenceTab } from './EvidenceTab';
import { DataTab } from './DataTab';
import {
  Map as MapIcon,
  BrainCircuit,
  Database,
  Table,
  ArrowLeft,
  Sparkles,
  SlidersHorizontal,
  FileText,
  Activity,
  Loader2
} from 'lucide-react';

const MarineMap = dynamic(
  () => import('@/components/MarineMap').then((mod) => mod.MarineMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[520px] lg:h-[620px] rounded-xl bg-[#0A1628] border border-slate-800 flex flex-col items-center justify-center text-slate-400 font-mono text-xs gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-teal-400" />
        <span>Initializing Operations Map...</span>
      </div>
    ),
  }
);

export type AnalysisTabKey = 'map' | 'reasoning' | 'evidence' | 'data';

interface AnalysisWorkspaceProps {
  analysis: ORCAAnalysisResult;
  zones: MarineZone[];
  selectedZone: MarineZone | null;
  onSelectZone: (zone: MarineZone) => void;
  activeFilter: 'all' | 'safe' | 'hazards' | 'restricted';
  evidenceSources?: EvidenceSource[];
  onInspectEvidence?: (evidence: any) => void;
  onAskFollowUp?: (query: string) => void;
  onOpenWhatIfModal?: () => void;
  onOpenConfidenceModal?: () => void;
  onOpenMarineBrief?: () => void;
  onBackToAsk?: () => void;
  language?: string;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({
  analysis,
  zones,
  selectedZone,
  onSelectZone,
  activeFilter,
  evidenceSources,
  onInspectEvidence,
  onAskFollowUp,
  onOpenWhatIfModal,
  onOpenConfidenceModal,
  onOpenMarineBrief,
  onBackToAsk,
  language = 'en',
}) => {
  const [activeTab, setActiveTab] = useState<AnalysisTabKey>('map');

  const tabs = [
    { key: 'map' as AnalysisTabKey, label: 'OPERATIONS MAP', icon: MapIcon },
    { key: 'reasoning' as AnalysisTabKey, label: 'DECISION REASONING', icon: BrainCircuit },
    { key: 'evidence' as AnalysisTabKey, label: 'EVIDENCE & SOURCES', icon: Database },
    { key: 'data' as AnalysisTabKey, label: 'SCIENTIFIC TELEMETRY', icon: Table },
  ];

  return (
    <div className="space-y-4 font-mono text-xs text-slate-200">
      {/* Persistent Analysis Header with Query & Workspace Tabs */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-3 lg:p-4 shadow-md space-y-3">
        {/* Top Query & Action Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5 min-w-0">
            {onBackToAsk && (
              <button
                onClick={onBackToAsk}
                className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-colors text-[11px] font-bold"
                title="Return to Ask ORCA prompt interface"
              >
                <ArrowLeft className="w-3.5 h-3.5 text-teal-400" />
                <span>Ask New</span>
              </button>
            )}
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-[9px] uppercase font-bold text-teal-400 bg-teal-500/10 px-1.5 py-0.2 rounded border border-teal-500/30">
                  Active Analysis
                </span>
                <span className="text-[10px] text-slate-400 truncate">
                  {analysis.time || '10:35 IST'}
                </span>
              </div>
              <h2 className="text-sm font-bold text-white tracking-wide truncate mt-0.5">
                &ldquo;{analysis.query}&rdquo;
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {onOpenWhatIfModal && (
              <button
                onClick={onOpenWhatIfModal}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-bold transition-colors"
                title="Run What-If Scenario Simulations"
              >
                <SlidersHorizontal className="w-3.5 h-3.5 text-amber-400" />
                <span>What-If?</span>
              </button>
            )}

            {onOpenMarineBrief && (
              <button
                onClick={onOpenMarineBrief}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold transition-colors"
                title="Generate Operational Marine Intelligence Brief"
              >
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                <span>Marine Brief</span>
              </button>
            )}
          </div>
        </div>

        {/* Tab Switchers (Only 1 Active Tab at a time!) */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-0.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-bold text-[11px] transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-xs'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Top Decision Summary Strip for Instant Awareness */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-2.5 shadow-md grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
        <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/20">
          <span className="text-[9px] text-rose-300 font-bold block uppercase">AVOID</span>
          <span className="text-xs font-bold text-rose-400 mt-0.5 block">
            {analysis.zonesToAvoid.length} {analysis.zonesToAvoid.length === 1 ? 'ZONE' : 'ZONES'}
          </span>
        </div>

        <div className="p-1.5 rounded bg-emerald-500/10 border border-emerald-500/20">
          <span className="text-[9px] text-emerald-300 font-bold block uppercase">CANDIDATES</span>
          <span className="text-xs font-bold text-emerald-400 mt-0.5 block">
            {analysis.potentialZones.filter(z => z.status === 'suitable' || z.status === 'suitable_candidate').length} ZONE
          </span>
        </div>

        <div className="p-1.5 rounded bg-cyan-500/10 border border-cyan-500/20 cursor-pointer hover:bg-cyan-500/20 transition-colors"
          onClick={onOpenConfidenceModal}
          title="Click to inspect decomposed confidence model"
        >
          <span className="text-[9px] text-cyan-300 font-bold block uppercase">CONFIDENCE INDEX</span>
          <span className="text-xs font-bold text-cyan-400 mt-0.5 block">
            {analysis.confidenceScore} / 100
          </span>
        </div>

        <div className="p-1.5 rounded bg-teal-500/10 border border-teal-500/20">
          <span className="text-[9px] text-teal-300 font-bold block uppercase">EVIDENCE COVERAGE</span>
          <span className="text-xs font-bold text-teal-400 mt-0.5 block">
            100% (4 SOURCES)
          </span>
        </div>
      </div>

      {/* TAB 1: OPERATIONS MAP (Dominant 68% map + 32% Sector Inspector) */}
      {activeTab === 'map' && (
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start animate-in fade-in duration-200">
          <div className="lg:col-span-8">
            <MarineMap
              zones={zones}
              selectedZone={selectedZone}
              onSelectZone={onSelectZone}
              filterMode={activeFilter}
              language={language}
            />
          </div>

          <div className="lg:col-span-4">
            <ZoneDetails
              zone={selectedZone}
              onHighlightOnMap={(zone) => onSelectZone(zone)}
              onViewSource={() => setActiveTab('evidence')}
              onViewReasoning={() => setActiveTab('reasoning')}
              onViewEvidence={() => setActiveTab('evidence')}
              language={language}
            />
          </div>
        </section>
      )}

      {/* TAB 2: REASONING & WHY */}
      {activeTab === 'reasoning' && (
        <div className="animate-in fade-in duration-200">
          <ReasoningTab
            analysis={analysis}
            onSelectZone={onSelectZone}
            onAskFollowUp={onAskFollowUp}
            onOpenWhatIfModal={onOpenWhatIfModal}
            onOpenConfidenceModal={onOpenConfidenceModal}
            language={language}
          />
        </div>
      )}

      {/* TAB 3: EVIDENCE & SOURCES */}
      {activeTab === 'evidence' && (
        <div className="animate-in fade-in duration-200">
          <EvidenceTab
            sources={evidenceSources}
            coveragePercent={100}
            onInspectEvidence={onInspectEvidence}
            onNavigateToMap={() => setActiveTab('map')}
          />
        </div>
      )}

      {/* TAB 4: RAW & NORMALIZED SCIENTIFIC DATA */}
      {activeTab === 'data' && (
        <div className="animate-in fade-in duration-200">
          <DataTab zones={zones} />
        </div>
      )}
    </div>
  );
};
