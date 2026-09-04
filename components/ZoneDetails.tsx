'use client';

import React from 'react';
import { MarineZone } from '@/types/marine';
import {
  AlertTriangle,
  Lock,
  Compass,
  Layers
} from 'lucide-react';
import { ViewSourceLink } from './ViewSourceLink';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface ZoneDetailsProps {
  zone: MarineZone | null;
  onHighlightOnMap?: (zone: MarineZone) => void;
  onViewSource?: (sourceId: string) => void;
  language?: string;
}

export const ZoneDetails: React.FC<ZoneDetailsProps> = ({
  zone,
  language = 'en',
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  if (!zone) {
    return (
      <div className="h-full bg-white rounded-2xl border border-slate-200/80 p-6 flex flex-col items-center justify-center text-center">
        <Compass className="w-8 h-8 text-slate-300 mb-2" />
        <h4 className="text-xs font-semibold text-slate-700">Select a Marine Zone</h4>
        <p className="text-[11px] text-slate-400 mt-1 max-w-[200px]">
          Click any sector on the map or select from analysis results.
        </p>
      </div>
    );
  }

  const getStatusStyle = () => {
    const statusKey = zone.status?.toLowerCase();
    switch (statusKey) {
      case 'high_risk':
        return 'text-rose-700 bg-rose-50 border-rose-200';
      case 'restricted':
        return 'text-indigo-700 bg-indigo-50 border-indigo-200';
      case 'suitable':
      case 'suitable_candidate':
        return 'text-emerald-700 bg-emerald-50 border-emerald-200';
      case 'insufficient_data':
        return 'text-slate-600 bg-slate-100 border-slate-300';
      case 'caution':
      default:
        return 'text-amber-700 bg-amber-50 border-amber-200';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 space-y-4 shadow-sm text-xs">
      {/* Zone Header & Geometry Badge */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono font-bold text-sm text-slate-900 tracking-tight">
            {zone.code}
          </span>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide border uppercase ${getStatusStyle()}`}
          >
            {zone.statusLabel}
          </span>
        </div>
        <p className="text-xs font-medium text-slate-700 mt-0.5">{zone.name}</p>
        
        {/* Explicit Prototype vs Official Label */}
        <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
          <Layers className="w-3 h-3 text-slate-400 shrink-0" />
          <span>{zone.geometry_type || 'Prototype / Demonstration Geometry'}</span>
        </div>
      </div>

      {/* Risk Score */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-slate-500 font-medium">{t.riskScore}</span>
          <span className="font-mono font-bold text-slate-900">
            {zone.riskScore} <span className="text-slate-400 font-normal">/ 100</span>
          </span>
        </div>
        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              zone.riskScore > 75
                ? 'bg-rose-500'
                : zone.riskScore > 40
                ? 'bg-amber-500'
                : 'bg-emerald-500'
            }`}
            style={{ width: `${zone.riskScore}%` }}
          />
        </div>
      </div>

      <div className="h-px bg-slate-100" />

      {/* Key Conditions - Compact 3-Column Metrics */}
      <div>
        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
          {t.keyForecastConditions}
        </p>
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-slate-50 p-2 rounded-lg">
            <span className="text-[10px] text-slate-500 block">{t.wave}</span>
            <span className="text-xs font-bold text-slate-900 font-mono">
              {zone.conditions.waveHeight.split(' ')[0]}
            </span>
          </div>
          <div className="bg-slate-50 p-2 rounded-lg">
            <span className="text-[10px] text-slate-500 block">{t.wind}</span>
            <span className="text-xs font-bold text-slate-900 font-mono">
              {zone.conditions.windSpeed.split(' ')[0]} kt
            </span>
          </div>
          <div className="bg-slate-50 p-2 rounded-lg">
            <span className="text-[10px] text-slate-500 block">{t.sst}</span>
            <span className="text-xs font-bold text-slate-900 font-mono">
              {zone.conditions.seaSurfaceTemp}
            </span>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="space-y-1.5 text-xs text-slate-700">
        <div className="flex items-center gap-2">
          {zone.conditions.marineWarning ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
              <span className="font-medium text-rose-900">{t.marineAdvisoryActive}</span>
            </>
          ) : (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 ml-1 shrink-0"></span>
              <span className="text-slate-600">{t.noWeatherAdvisory}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {zone.conditions.isRestricted ? (
            <>
              <Lock className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
              <span className="font-medium text-indigo-900 truncate">
                {zone.conditions.geofenceStatus || t.restrictedArea}
              </span>
            </>
          ) : (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-300 ml-1 shrink-0"></span>
              <span className="text-slate-600">Restricted area: No</span>
            </>
          )}
        </div>
      </div>

      <div className="h-px bg-slate-100" />

      {/* Why Section */}
      <div>
        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
          {t.why}
        </p>
        <p className="text-xs text-slate-700 leading-relaxed">
          {zone.reasons && zone.reasons.length > 0 ? zone.reasons[0] : 'Evaluated under deterministic physical safety constraints.'}
        </p>
      </div>

      <div className="h-px bg-slate-100" />

      {/* Source & Freshness with Real Clickable Official Link */}
      <div className="flex items-center justify-between text-[11px] text-slate-500">
        <div>
          <span className="font-semibold text-slate-800">
            {zone.id === 'zone-c'
              ? 'INCOIS PFZ & MOSDAC'
              : zone.id === 'zone-b'
              ? 'GIS Cadastre (NHO)'
              : 'INCOIS OSF'}
          </span>
          <span className="mx-1">·</span>
          <span>Forecast</span>
        </div>
        <ViewSourceLink
          sourceUrl={zone.sourceUrl || 'https://incois.gov.in'}
          label={t.viewSource}
        />
      </div>
    </div>
  );
};
