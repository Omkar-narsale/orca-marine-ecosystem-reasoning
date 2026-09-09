import React from 'react';
import { ExternalLink, ShieldCheck, Activity } from 'lucide-react';

interface ConfidenceScoreProps {
  level: 'High' | 'Medium' | 'Low';
  score: number;
  explanation?: string;
  onViewMethodology?: () => void;
}

export const ConfidenceScore: React.FC<ConfidenceScoreProps> = ({
  level,
  score,
  explanation,
  onViewMethodology,
}) => {
  return (
    <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 shadow-md text-xs font-mono space-y-2.5 text-slate-300">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <span className="font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          Confidence Quantification
        </span>
        <span
          className="font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30 cursor-help"
          title="ORCA confidence index reflects evidence completeness, source agreement and data quality. It is not a calibrated probability of correctness."
        >
          Confidence Index {score} / 100 · {level.toUpperCase()}
        </span>
      </div>

      <div>
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
          CONVERGENCE RATIONALE
        </p>
        <p className="text-[11px] font-sans text-slate-300 leading-relaxed">
          {explanation ||
            '12h numerical forecast + recent satellite observation + verified maritime geofences.'}
        </p>
        <p className="text-[10px] text-slate-400 font-sans italic mt-1">
          * ORCA confidence index reflects evidence completeness, source agreement and data quality. It is not a calibrated probability of correctness.
        </p>
      </div>

      <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
        <span className="text-slate-400">5-Factor Uncertainty Model</span>
        <button
          type="button"
          onClick={onViewMethodology}
          className="text-cyan-400 hover:text-cyan-300 font-bold inline-flex items-center gap-1 transition-colors"
        >
          <span>Decompose & Inspect</span>
          <ExternalLink className="w-2.5 h-2.5" />
        </button>
      </div>
    </div>
  );
};
