'use client';

import React from 'react';
import { EvidenceSource } from '@/types/marine';
import { DEMO_EVIDENCE_SOURCES } from '@/data/demoEvidence';
import { ViewSourceLink } from './ViewSourceLink';

interface EvidencePanelProps {
  sources?: EvidenceSource[];
  onInspectEvidence?: (source: any) => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  sources = DEMO_EVIDENCE_SOURCES,
  onInspectEvidence,
}) => {
  const activeSources = sources && sources.length > 0 ? sources : DEMO_EVIDENCE_SOURCES;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm space-y-4 text-xs">
      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
            Evidence & Source Provenance
          </span>
          <p className="text-[11px] text-slate-500 mt-0.5">
            ORCA fused {activeSources.length} authoritative official observation & forecast feeds
          </p>
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          Official Links
        </span>
      </div>

      {/* Clean Minimal Rows with Real Clickable URLs */}
      <div className="divide-y divide-slate-100">
        {activeSources.map((source) => (
          <div
            key={source.id}
            className="py-3.5 first:pt-1 last:pb-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
          >
            <div className="space-y-0.5 max-w-xl">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-xs">
                  {source.name}
                </span>
                <span className="text-slate-400">·</span>
                <span className="text-slate-600 font-medium">
                  {source.organization}
                </span>
              </div>
              <p className="text-[11px] text-slate-700 font-medium">
                {source.title || source.parameter}
              </p>
              <p className="text-[10px] text-slate-400">
                {source.description}
              </p>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-4 text-[11px] shrink-0">
              <span className="font-mono text-slate-400 text-[10px]">
                {source.timestamp}
              </span>
              <ViewSourceLink
                sourceUrl={source.sourceUrl}
                label="View Source"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
