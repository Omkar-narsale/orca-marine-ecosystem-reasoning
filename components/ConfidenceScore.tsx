import React from 'react';
import { ArrowUpRight } from 'lucide-react';

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
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm text-xs space-y-3">
      <div className="flex items-center justify-between pb-1 border-b border-slate-100">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
          Confidence
        </span>
        <span className="font-semibold text-slate-900 font-mono">
          {score}% · {level}
        </span>
      </div>

      <div>
        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
          Why
        </p>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          {explanation ||
            '12h numerical forecast + recent satellite observation + verified maritime geofences.'}
        </p>
      </div>

      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
        <span className="text-slate-400 text-[10px]">Prototype confidence model</span>
        <button
          type="button"
          onClick={onViewMethodology}
          className="text-teal-700 hover:text-teal-900 font-medium inline-flex items-center gap-0.5"
        >
          <span>View methodology</span>
          <ArrowUpRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
};
