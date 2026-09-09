'use client';

import React, { useEffect, useState } from 'react';
import { fetchUncertaintyBreakdown } from '@/lib/apiClient';

interface ConfidenceBreakdownModalProps {
  isOpen: boolean;
  onClose: () => void;
  zoneId?: string;
}

export default function ConfidenceBreakdownModal({ isOpen, onClose, zoneId = 'zone-c' }: ConfidenceBreakdownModalProps) {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetchUncertaintyBreakdown(zoneId).then((res) => {
        setData(res);
        setLoading(false);
      });
    }
  }, [isOpen, zoneId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="w-full max-w-xl max-h-[90vh] bg-[#0c121e] border border-cyan-500/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden relative z-[100000]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-cyan-500/20 bg-[#090d16]/90">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </span>
            <div>
              <div className="text-[10px] font-mono tracking-widest uppercase text-cyan-400 font-semibold">Scientific Evidence Decomposition</div>
              <h2 className="text-base font-bold text-white">Confidence & Uncertainty Quantification</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-slate-200">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
              <svg className="animate-spin w-6 h-6 text-cyan-400" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-xs font-mono">Quantifying 5-Factor Confidence Dimensions...</span>
            </div>
          ) : data ? (
            <>
              {/* Overall Summary Cards */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">Evidence Confidence Index</div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-2xl font-bold font-mono text-cyan-300">{data.confidence.overall_confidence_pct} / 100</span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">{data.confidence.confidence_level}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">ORCA confidence index reflects evidence completeness, source agreement and data quality. It is not a calibrated probability of correctness.</p>
                </div>

                <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-semibold">Residual Uncertainty</div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-xl font-bold font-mono text-amber-300">{data.uncertainty_level}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Biological congregation & forecast horizon variance.</p>
                </div>
              </div>

              {/* 5-Factor Progress Breakdown */}
              <div className="space-y-3.5">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">Decomposed Confidence Dimensions:</div>
                
                {Object.entries(data.confidence.breakdown).map(([key, dim]: [string, any]) => (
                  <div key={key} className="space-y-1 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-200">{dim.label}</span>
                      <span className="font-mono text-cyan-400 font-bold">{dim.percentage}%</span>
                    </div>
                    {/* Visual Bar Indicator */}
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-500"
                        style={{ width: `${dim.percentage}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-slate-400">{dim.description}</div>
                  </div>
                ))}
              </div>

              {/* Scientific Principles Distinction */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
                <div className="text-[11px] font-mono uppercase tracking-wider text-slate-300 font-semibold">Scientific Separation Principle:</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-slate-400">
                  <div className="p-2 rounded bg-slate-800/60">
                    <span className="text-cyan-300 font-semibold block mb-0.5">Confidence</span>
                    {data.scientific_distinction.confidence_concept}
                  </div>
                  <div className="p-2 rounded bg-slate-800/60">
                    <span className="text-amber-300 font-semibold block mb-0.5">Uncertainty</span>
                    {data.scientific_distinction.uncertainty_concept}
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
