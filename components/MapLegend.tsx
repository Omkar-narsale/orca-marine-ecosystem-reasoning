import React from 'react';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface MapLegendProps {
  language?: string;
}

export const MapLegend: React.FC<MapLegendProps> = ({ language = 'en' }) => {
  const langKey = (language as LanguageCode) || 'en';
  
  const labels = {
    en: { highRisk: 'HIGH RISK', caution: 'CAUTION', suitable: 'SUITABLE CANDIDATE', restricted: 'RESTRICTED', insufficientData: 'INSUFFICIENT DATA' },
    hi: { highRisk: 'उच्च जोखिम', caution: 'सावधानी', suitable: 'उपयुक्त उम्मीदवार', restricted: 'प्रतिबंधित', insufficientData: 'अपर्याप्त डेटा' },
    mr: { highRisk: 'उच्च धोका', caution: 'सावधगिरी', suitable: 'योग्य उमेदवार', restricted: 'प्रतिबंधित', insufficientData: 'अपुरा डेटा' },
  }[langKey] || { highRisk: 'HIGH RISK', caution: 'CAUTION', suitable: 'SUITABLE CANDIDATE', restricted: 'RESTRICTED', insufficientData: 'INSUFFICIENT DATA' };

  return (
    <div className="bg-[#0F172A]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 shadow-md text-xs font-mono">
      <div className="flex flex-wrap items-center gap-3 text-[10px] text-slate-300">
        <div className="flex items-center gap-1.5" title="Elevated hazard or active warning: Sector should be avoided">
          <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
          <span className="font-bold text-rose-300">{labels.highRisk}</span>
        </div>
        <div className="flex items-center gap-1.5" title="Moderate swell/wind: Requires caution">
          <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span>
          <span className="font-bold text-amber-300">{labels.caution}</span>
        </div>
        <div className="flex items-center gap-1.5" title="Lower risk screening under current forecast">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
          <span className="font-bold text-emerald-300">{labels.suitable}</span>
        </div>
        <div className="flex items-center gap-1.5" title="Statutory naval or shipping fairway constraint">
          <span className="w-2 h-2 rounded-full bg-indigo-400 shrink-0"></span>
          <span className="font-bold text-indigo-300">{labels.restricted}</span>
        </div>
        <div className="flex items-center gap-1.5" title="Safety determination unavailable due to unverified data">
          <span className="w-2 h-2 rounded-full bg-slate-400 shrink-0"></span>
          <span className="font-bold text-slate-400">{labels.insufficientData}</span>
        </div>
      </div>
    </div>
  );
};
