'use client';

import React from 'react';
import { MarineZone } from '@/types/marine';
import {
  AlertTriangle,
  Lock,
  Compass,
  Layers,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  Waves,
  Wind,
  Thermometer
} from 'lucide-react';
import { ViewSourceLink } from './ViewSourceLink';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface ZoneDetailsProps {
  zone: MarineZone | null;
  onHighlightOnMap?: (zone: MarineZone) => void;
  onViewSource?: (sourceId: string) => void;
  onViewReasoning?: () => void;
  onViewEvidence?: () => void;
  language?: string;
}

export const ZoneDetails: React.FC<ZoneDetailsProps> = ({
  zone,
  onViewReasoning,
  onViewEvidence,
  language = 'en',
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  if (!zone) {
    return (
      <div className="h-full min-h-[300px] bg-[#0F172A] rounded-xl border border-slate-800 p-5 flex flex-col items-center justify-center text-center font-mono text-xs">
        <Compass className="w-8 h-8 text-slate-600 mb-2" />
        <h4 className="font-bold text-slate-300 uppercase tracking-wider">Sector Inspector</h4>
        <p className="text-[11px] text-slate-500 mt-1 max-w-[200px]">
          Select any zone on the map or from the decision panel to inspect telemetry.
        </p>
      </div>
    );
  }

  const getStatusStyle = () => {
    const statusKey = zone.status?.toLowerCase();
    switch (statusKey) {
      case 'high_risk':
        return 'text-rose-300 bg-rose-500/15 border-rose-500/30';
      case 'restricted':
        return 'text-indigo-300 bg-indigo-500/15 border-indigo-500/30';
      case 'suitable':
      case 'suitable_candidate':
        return 'text-emerald-300 bg-emerald-500/15 border-emerald-500/30';
      case 'insufficient_data':
        return 'text-slate-400 bg-slate-800 border-slate-700';
      case 'caution':
      default:
        return 'text-amber-300 bg-amber-500/15 border-amber-500/30';
    }
  };

  return (
    <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 space-y-3.5 shadow-md text-xs font-mono text-slate-300">
      {/* Zone Header & Status */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm text-white tracking-wider">
              {zone.code}
            </span>
            <span className="text-[10px] text-slate-400 font-sans">
              ({zone.name})
            </span>
          </div>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border uppercase ${getStatusStyle()}`}
          >
            {zone.statusLabel}
          </span>
        </div>
        
        <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-500">
          <Layers className="w-3 h-3 text-slate-500 shrink-0" />
          <span>{zone.geometry_type || 'Demonstration Sector Geometry'}</span>
        </div>
      </div>

      {/* Deterministic Risk Meter */}
      <div>
        <div className="flex items-center justify-between text-[11px] mb-1">
          <span className="text-slate-400 uppercase font-bold">{t.riskScore || 'RISK INDEX'}</span>
          <span className="font-bold text-white">
            {zone.riskScore} <span className="text-slate-500 font-normal">/ 100</span>
          </span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              zone.riskScore > 70
                ? 'bg-rose-500'
                : zone.riskScore > 35
                ? 'bg-amber-500'
                : 'bg-emerald-500'
            }`}
            style={{ width: `${zone.riskScore}%` }}
          />
        </div>
      </div>

      {/* Precision Telemetry Grid */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[9px] text-slate-400 uppercase block font-bold">WAVE</span>
          <span className="text-xs font-bold text-teal-300 block mt-0.5">
            {zone.conditions.waveHeight.split(' ')[0]} m
          </span>
        </div>
        <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[9px] text-slate-400 uppercase block font-bold">WIND</span>
          <span className="text-xs font-bold text-teal-300 block mt-0.5">
            {zone.conditions.windSpeed.split(' ')[0]} kt
          </span>
        </div>
        <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[9px] text-slate-400 uppercase block font-bold">SST</span>
          <span className="text-xs font-bold text-teal-300 block mt-0.5">
            {zone.conditions.seaSurfaceTemp}
          </span>
        </div>
      </div>

      {/* Safety & Geofence Constraints */}
      <div className="space-y-1.5 text-[11px]">
        <div className="flex items-center gap-2 py-1 px-2 rounded bg-slate-900/50 border border-slate-800/80">
          {zone.conditions.marineWarning ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
              <span className="text-rose-300 font-semibold">{t.marineAdvisoryActive || 'Marine Warning Active'}</span>
            </>
          ) : (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span className="text-slate-300">{t.noWeatherAdvisory || 'No Marine Hazard Advisory'}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2 py-1 px-2 rounded bg-slate-900/50 border border-slate-800/80">
          {zone.conditions.isRestricted ? (
            <>
              <Lock className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <span className="text-indigo-300 font-semibold truncate">
                {zone.conditions.geofenceStatus || t.restrictedArea || 'Restricted Maritime Enclave'}
              </span>
            </>
          ) : (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-600 ml-1 shrink-0"></span>
              <span className="text-slate-400">Naval Geofence: Unrestricted</span>
            </>
          )}
        </div>
      </div>

      {/* Grounded Why Rationale & Direct Tab Jump Buttons */}
      <div className="pt-2 border-t border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            {t.why || 'WHY THIS DECISION'}
          </span>
          <div className="flex items-center gap-1.5">
            {onViewReasoning && (
              <button
                onClick={onViewReasoning}
                className="px-2 py-0.5 rounded bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/30 text-[10px] font-bold transition-colors"
                title="Open Decision Reasoning Workspace for this sector"
              >
                Why?
              </button>
            )}
            {onViewEvidence && (
              <button
                onClick={onViewEvidence}
                className="px-2 py-0.5 rounded bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold transition-colors"
                title="View Official Evidence & Source Citations"
              >
                View Evidence
              </button>
            )}
          </div>
        </div>
        <p className="text-[11px] font-sans text-slate-300 leading-relaxed">
          {zone.reasons && zone.reasons.length > 0 ? zone.reasons[0] : 'Evaluated under deterministic physical safety constraints.'}
        </p>
      </div>

      {/* Source Citation & Official Link */}
      <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
        <span className="text-slate-400">
          Source: <strong className="text-slate-200">{zone.id === 'zone-c' ? 'INCOIS & MOSDAC' : zone.id === 'zone-b' ? 'GIS Cadastre' : 'INCOIS OSF'}</strong>
        </span>
        <a
          href={zone.sourceUrl || 'https://incois.gov.in'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 font-bold transition-colors"
        >
          <span>Official Source</span>
          <ExternalLink className="w-2.5 h-2.5" />
        </a>
      </div>
    </div>
  );
};
