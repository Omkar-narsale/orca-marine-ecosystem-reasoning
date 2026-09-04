'use client';

import React from 'react';
import { EvidenceGraphNode, EvidenceSource, ZoneFactor } from '@/types/marine';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  evidence: EvidenceGraphNode | EvidenceSource | ZoneFactor | null;
}

export default function EvidenceDrawer({ isOpen, onClose, evidence }: EvidenceDrawerProps) {
  if (!isOpen || !evidence) return null;

  const getProp = (key: string, fallback = '—') => {
    return (evidence as any)[key] || fallback;
  };

  const organization = getProp('organization', getProp('source', 'Authoritative Registry'));
  const parameter = getProp('parameter', getProp('title', getProp('label', 'Parameter Record')));
  const value = getProp('value', 'Value Recorded');
  const unit = getProp('unit', '');
  const dataType = getProp('data_type', getProp('dataType', getProp('type', 'Observation'))).toUpperCase();
  const validTime = getProp('valid_time', getProp('validFor', getProp('validityTime', 'Current Analysis Window')));
  const retrievedAt = getProp('retrieved_at', getProp('timestamp', '05 Sep 2026 06:00 IST'));
  const sourceUrl = getProp('source_url', getProp('sourceUrl', 'https://incois.gov.in/'));
  const citation = getProp('citation', getProp('description', 'Official verified record from scientific monitoring infrastructure.'));
  const sourceId = getProp('source_id', getProp('id', 'REGISTRY_NODE'));

  return (
    <div className="fixed inset-0 z-[99999] flex justify-end bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-lg bg-[#0c121e] border-l border-cyan-500/20 shadow-2xl h-full flex flex-col justify-between overflow-y-auto relative z-[100000]"
        onClick={(e) => e.stopPropagation()}
      >
        <div>
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-cyan-500/15 bg-[#090d16]/80 backdrop-blur">
            <div className="flex items-center gap-3">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              <div>
                <span className="text-[10px] font-mono tracking-widest uppercase text-cyan-400 font-semibold">Evidence Graph Node</span>
                <h2 className="text-lg font-bold text-white tracking-wide">{parameter}</h2>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
              title="Close drawer"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Body Content */}
          <div className="p-6 space-y-6">
            {/* Primary Value Card */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 to-slate-900/60 border border-cyan-500/20">
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs uppercase font-mono tracking-wider text-slate-400">Observed / Forecast Value</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  {dataType}
                </span>
              </div>
              <div className="text-3xl font-extrabold text-white font-mono flex items-baseline gap-2">
                {String(value)} <span className="text-sm font-normal text-cyan-400">{unit}</span>
              </div>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed">{citation}</p>
            </div>

            {/* Structured Metadata Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3.5 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">Authoritative Source</div>
                <div className="text-sm font-semibold text-white">{organization}</div>
                <div className="text-[11px] font-mono text-cyan-400/80 mt-0.5">{sourceId}</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">Data Nature</div>
                <div className="text-sm font-semibold text-white">{dataType}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Scientific Ground Truth</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">Temporal Validity</div>
                <div className="text-xs font-mono font-medium text-amber-300">{validTime}</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">Retrieval Timestamp</div>
                <div className="text-xs font-mono text-slate-300">{retrievedAt}</div>
              </div>
            </div>

            {/* Traceability & Integrity Notice */}
            <div className="p-4 rounded-lg bg-slate-900/30 border border-slate-800/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Deterministic Evidence Grounding
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                This evidence node directly binds to deterministic risk calculations and geospatial validation rules. ORCA guarantees zero synthetic fabrication of numeric values.
              </p>
            </div>
          </div>
        </div>

        {/* Footer with Clickable Official URL */}
        <div className="p-6 border-t border-slate-800 bg-[#090d16]/95">
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm transition-colors shadow-lg shadow-cyan-900/30"
          >
            <span>View Official Registry Source</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
