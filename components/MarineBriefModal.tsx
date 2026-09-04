'use client';

import React, { useState } from 'react';
import { MarineBriefReport } from '@/types/marine';
import { submitUserFeedback } from '@/lib/apiClient';

interface MarineBriefModalProps {
  isOpen: boolean;
  onClose: () => void;
  report: MarineBriefReport | null;
  isLoading?: boolean;
}

export default function MarineBriefModal({ isOpen, onClose, report, isLoading }: MarineBriefModalProps) {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [rating, setRating] = useState(5);

  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleFeedback = async (useful: boolean) => {
    if (report) {
      await submitUserFeedback(report.report_title, useful, rating, 'Marine Brief user evaluation');
      setFeedbackSent(true);
    }
  };

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="w-full max-w-3xl max-h-[90vh] bg-[#0c121e] border border-cyan-500/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden relative z-[100000]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-cyan-500/20 bg-[#090d16]/90">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </span>
            <div>
              <div className="text-[10px] font-mono tracking-widest uppercase text-cyan-400 font-semibold">Auditable Operational Document</div>
              <h2 className="text-base font-bold text-white">ORCA Marine Intelligence Brief</h2>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>Export / Print</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {isLoading ? (
            <div className="py-16 text-center space-y-3">
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-slate-400 text-xs font-mono">Compiling deterministic operational brief...</p>
            </div>
          ) : report ? (
            <>
              {/* Document Metadata Bar */}
              <div className="grid grid-cols-3 gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono">
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Reference ID</span>
                  <span className="text-cyan-300 font-semibold">{report.reference_id}</span>
                </div>
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Sector Bounds</span>
                  <span className="text-white truncate block">{report.geographic_sector}</span>
                </div>
                <div>
                  <span className="text-slate-500 uppercase block text-[10px]">Temporal Envelope</span>
                  <span className="text-amber-300 block">{report.temporal_envelope}</span>
                </div>
              </div>

              {/* Operational Executive Decision */}
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-2">
                <div className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-semibold">Executive Decision Summary</div>
                <p className="text-slate-200 font-medium leading-relaxed">{report.operational_summary.executive_decision}</p>
              </div>

              {/* Sector Breakdown */}
              <div className="space-y-3">
                <div className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-semibold">Sector Risk Classifications</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {/* Avoid Sectors */}
                  <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-500/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-red-400 font-mono">AVOID SECTORS</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-red-500/20 text-red-300">
                        {report.operational_summary.avoid_sectors.length} Active
                      </span>
                    </div>
                    {report.operational_summary.avoid_sectors.map((s, idx) => (
                      <div key={idx} className="text-xs p-2 rounded bg-black/40 border border-red-500/15">
                        <div className="flex justify-between font-semibold text-white">
                          <span>{s.code} ({s.name})</span>
                          <span className="text-red-400 font-mono">{s.risk_score}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{s.primary_hazard}</div>
                      </div>
                    ))}
                  </div>

                  {/* Candidate Sectors */}
                  <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-400 font-mono">POTENTIAL CANDIDATES</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300">
                        {report.operational_summary.candidate_sectors.length} Candidate
                      </span>
                    </div>
                    {report.operational_summary.candidate_sectors.map((s, idx) => (
                      <div key={idx} className="text-xs p-2 rounded bg-black/40 border border-emerald-500/15">
                        <div className="flex justify-between font-semibold text-white">
                          <span>{s.code} ({s.name})</span>
                          <span className="text-emerald-400 font-mono">{s.risk_score}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{s.suitability_summary}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Evidence Provenance Table */}
              <div className="space-y-2">
                <div className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-semibold">Authoritative Evidence Citations</div>
                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 font-mono text-[10px] uppercase">
                      <tr>
                        <th className="px-3 py-2">Parameter</th>
                        <th className="px-3 py-2">Value</th>
                        <th className="px-3 py-2">Source</th>
                        <th className="px-3 py-2">Type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/40 text-slate-300 font-mono">
                      {report.evidence_provenance.map((ev, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/30">
                          <td className="px-3 py-2 font-medium text-white">{ev.parameter}</td>
                          <td className="px-3 py-2 text-cyan-300">{ev.value}</td>
                          <td className="px-3 py-2 text-slate-400">{ev.organization}</td>
                          <td className="px-3 py-2 text-amber-300/90 text-[10px]">{ev.data_type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Confidence & Disclaimers */}
              <div className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800 text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">Confidence Assessment: {report.confidence_assessment.score} ({report.confidence_assessment.level})</span>
                  <span className="text-[11px] font-mono text-cyan-400">Coverage Grounded</span>
                </div>
                <p className="text-[11px] text-slate-400">{report.confidence_assessment.explanation}</p>
                {report.scientific_limitations.length > 0 && (
                  <p className="text-[10px] text-amber-400/90 pt-1 font-mono">
                    ⚠ {report.scientific_limitations[0]}
                  </p>
                )}
              </div>
            </>
          ) : (
            <p className="text-center text-slate-400 text-xs py-8">No brief data available.</p>
          )}
        </div>

        {/* Modal Footer / Feedback */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-[#090d16]/95 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400">Was this brief useful?</span>
            {feedbackSent ? (
              <span className="text-xs text-emerald-400 font-medium">✓ Feedback recorded</span>
            ) : (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => handleFeedback(true)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs border border-slate-700 transition-colors"
                >
                  👍 Yes
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs border border-slate-700 transition-colors"
                >
                  👎 No
                </button>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium border border-slate-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
