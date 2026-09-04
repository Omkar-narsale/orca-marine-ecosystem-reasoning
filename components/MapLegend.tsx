import React from 'react';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface MapLegendProps {
  language?: string;
}

export const MapLegend: React.FC<MapLegendProps> = ({ language = 'en' }) => {
  const langKey = (language as LanguageCode) || 'en';
  
  const labels = {
    en: { highRisk: 'High Risk', caution: 'Caution', suitable: 'Suitable', restricted: 'Restricted' },
    hi: { highRisk: 'उच्च जोखिम', caution: 'सावधानी', suitable: 'अनुकूल', restricted: 'प्रतिबंधित' },
    mr: { highRisk: 'उच्च धोका', caution: 'सावधगिरी', suitable: 'अनुकूल', restricted: 'प्रतिबंधित' },
  }[langKey] || { highRisk: 'High Risk', caution: 'Caution', suitable: 'Suitable', restricted: 'Restricted' };

  return (
    <div className="bg-white/95 backdrop-blur-sm px-3 py-2 rounded-lg border border-slate-200/80 shadow-sm text-xs">
      <div className="flex items-center gap-4 text-[11px] text-slate-700">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-rose-500 shrink-0"></span>
          <span>{labels.highRisk}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-amber-500 shrink-0"></span>
          <span>{labels.caution}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 shrink-0"></span>
          <span>{labels.suitable}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-indigo-500 shrink-0"></span>
          <span>{labels.restricted}</span>
        </div>
      </div>
    </div>
  );
};
