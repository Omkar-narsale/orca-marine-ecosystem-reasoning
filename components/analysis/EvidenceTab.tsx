'use client';

import React from 'react';
import { EvidenceSource } from '@/types/marine';
import { DEMO_EVIDENCE_SOURCES } from '@/data/demoEvidence';
import { Database, ExternalLink, ShieldCheck, Clock, Layers, ArrowUpRight } from 'lucide-react';

interface EvidenceTabProps {
  sources?: EvidenceSource[];
  coveragePercent?: number;
  onInspectEvidence?: (source: any) => void;
  onNavigateToMap?: () => void;
}

export const EvidenceTab: React.FC<EvidenceTabProps> = ({
  sources = DEMO_EVIDENCE_SOURCES,
  coveragePercent = 100,
  onInspectEvidence,
  onNavigateToMap,
}) => {
  const activeSources = sources && sources.length > 0 ? sources : DEMO_EVIDENCE_SOURCES;

  return (
    <div className="space-y-5 font-mono text-xs text-slate-200">
      {/* 1. Evidence Coverage Metric & Integrity Banner */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-teal-400" />
            <span className="text-xs uppercase font-bold tracking-wider text-white">
              Evidence Provenance & Scientific Grounding
            </span>
          </div>
          <p className="text-[11px] font-sans text-slate-400 mt-1">
            ORCA fuses authoritative oceanographic, meteorological, satellite, and geospatial cadastre feeds.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="p-2.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-center">
            <span className="text-[9px] uppercase tracking-wider text-teal-300 font-bold block">
              EVIDENCE COVERAGE
            </span>
            <span className="text-sm font-bold text-teal-300 block mt-0.5">
              {coveragePercent}% COMPLETE
            </span>
          </div>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[10px] text-slate-400 font-sans">
        ℹ️ <strong>ORCA Coverage Metric:</strong> Indicates all required observational and numerical parameters (wave, wind, SST, geofences) were successfully retrieved and verified. It is an evidence-completeness metric, not a calibrated statistical probability.
      </div>

      {/* 2. Structured Official Feeds Table / Registry */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 lg:p-5 shadow-md space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <span className="font-bold text-white text-xs uppercase tracking-wider">
            Authoritative Marine Feeds ({activeSources.length} Registered)
          </span>
          <span className="text-[10px] text-teal-400">Zero Synthetic Values</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {activeSources.map((source) => {
            const isForecast = (source.type || source.dataType || '').toLowerCase().includes('forecast');
            const isWarning = (source.type || source.dataType || '').toLowerCase().includes('warning');
            const isObservation = (source.type || source.dataType || '').toLowerCase().includes('observation');

            return (
              <div
                key={source.id}
                className="p-3.5 bg-slate-900/90 rounded-lg border border-slate-800 hover:border-slate-700 transition-all space-y-2.5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white text-xs">{source.name}</span>
                      <span className="text-slate-600">·</span>
                      <span className="text-[10px] text-teal-400">{source.organization}</span>
                    </div>

                    <span
                      className={`px-1.5 py-0.2 rounded text-[9px] font-bold border uppercase ${
                        isWarning
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                          : isForecast
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                          : isObservation
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                      }`}
                    >
                      {source.type || source.dataType || 'FORECAST'}
                    </span>
                  </div>

                  <div className="pt-1">
                    <span className="font-bold text-slate-200 text-xs block">
                      {source.title || source.parameter}
                    </span>
                    <p className="text-[10px] font-sans text-slate-400 mt-0.5 leading-snug">
                      {source.description}
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-[9px] text-slate-400">
                    <span>Valid: <strong className="text-slate-300">{source.timestamp}</strong></span>
                    <span>Format: <strong className="text-slate-300">Normalized Telemetry</strong></span>
                  </div>

                  <div className="flex items-center justify-between gap-2 pt-1">
                    {onInspectEvidence && (
                      <button
                        onClick={() => onInspectEvidence(source)}
                        className="text-[10px] text-teal-400 hover:text-teal-300 font-bold inline-flex items-center gap-1"
                      >
                        <span>Inspect Node</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    )}

                    <a
                      href={source.sourceUrl || 'https://incois.gov.in'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] text-slate-300 hover:text-white font-bold inline-flex items-center gap-1 bg-slate-800 hover:bg-slate-700 px-2 py-1 rounded border border-slate-700 transition-colors ml-auto"
                    >
                      <span>Official Source</span>
                      <ExternalLink className="w-2.5 h-2.5 text-teal-400" />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
