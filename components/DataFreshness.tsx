import React from 'react';
import { DataFreshnessItem } from '@/types/marine';
import { DEMO_FRESHNESS_ITEMS } from '@/data/demoEvidence';

interface DataFreshnessProps {
  items?: DataFreshnessItem[];
}

export const DataFreshness: React.FC<DataFreshnessProps> = ({
  items = DEMO_FRESHNESS_ITEMS,
}) => {
  const activeItems = items && items.length > 0 ? items : DEMO_FRESHNESS_ITEMS;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm text-xs space-y-3">
      <div className="flex items-center justify-between pb-1 border-b border-slate-100">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
          Data Freshness
        </span>
        <span className="text-[10px] text-slate-400 font-mono">
          Forecast vs Observation
        </span>
      </div>

      <div className="space-y-2 text-[11px]">
        {activeItems.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between gap-2 py-0.5">
            <span className="text-slate-600 truncate">{item.parameter}</span>
            <span className="font-mono text-slate-500 shrink-0 text-[10px]">
              {item.validityTime.replace('Forecast Valid: ', '').replace('Latest Available ', '')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
