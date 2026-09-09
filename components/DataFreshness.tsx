import React from 'react';
import { DataFreshnessItem } from '@/types/marine';
import { Clock } from 'lucide-react';

interface DataFreshnessProps {
  items?: DataFreshnessItem[];
}

export const DataFreshness: React.FC<DataFreshnessProps> = ({
  items = [],
}) => {
  const activeItems = items || [];

  return (
    <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 shadow-md text-xs font-mono space-y-2.5 text-slate-300">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <span className="font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-teal-400" />
          Data Freshness Lifecycle
        </span>
        <span className="text-[10px] text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
          Telemetry Cycle
        </span>
      </div>

      <div className="space-y-1.5 text-[11px]">
        {activeItems.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between gap-2 py-1 px-1.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-300 truncate">{item.parameter}</span>
            <span className="text-teal-300 font-bold shrink-0 text-[10px]">
              {item.validityTime.replace('Forecast Valid: ', '').replace('Latest Available ', '')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
