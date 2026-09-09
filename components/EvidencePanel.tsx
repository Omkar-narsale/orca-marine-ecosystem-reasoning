'use client';

import React from 'react';
import { EvidenceSource } from '@/types/marine';
import { ViewSourceLink } from './ViewSourceLink';
import { Database, ShieldCheck } from 'lucide-react';

interface EvidencePanelProps {
  sources?: EvidenceSource[];
  onInspectEvidence?: (source: any) => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  sources = [],
  onInspectEvidence,
}) => {
  const activeSources = sources || [];

  return (
    <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-3.5 text-xs font-mono text-slate-300">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-teal-400" />
          <span className="font-bold uppercase tracking-wider text-white">
            Evidence Provenance & Source Registry
          </span>
        </div>
        <span className="text-[10px] text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
          {activeSources.length} Feeds Fused
        </span>
      </div>

      {/* Structured Feeds Grid */}
      <div className="divide-y divide-slate-800/80">
        {activeSources.map((source) => (
          <div
            key={source.id}
            className="py-3 first:pt-0.5 last:pb-0.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5"
          >
            <div className="space-y-0.5 max-w-xl">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-xs">
                  {source.name}
                </span>
                <span className="text-slate-600">·</span>
                <span className="text-teal-400/90 font-medium text-[11px]">
                  {source.organization}
                </span>
              </div>
              <p className="text-[11px] font-sans text-slate-200">
                {source.title || source.parameter}
              </p>
              <p className="text-[10px] font-sans text-slate-400">
                {source.description}
              </p>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-3 text-[10px] shrink-0">
              <span className="text-slate-400">
                {source.timestamp}
              </span>
              <ViewSourceLink
                sourceUrl={source.sourceUrl}
                label="View Source ↗"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
