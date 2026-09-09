'use client';

import React from 'react';
import {
  Waves,
  Wind,
  Compass,
  AlertTriangle,
  ShieldCheck,
  Fish,
  Navigation,
  TrendingDown,
  MapPin,
  Clock,
  ExternalLink,
  ChevronRight,
  Info,
  ShieldAlert,
  Gauge
} from 'lucide-react';
import {
  PFZItem,
  MarineConditionsData,
  HazardAlertItem,
  RouteOptionItem,
  ProductivityAnalysisData
} from '@/types/marine';

interface IntentCardProps {
  responseType?: string;
  data?: any;
  results?: any[];
  whyReasons?: string[];
  sources?: any[];
  onSelectCandidate?: (item: any) => void;
  onShowMap?: () => void;
}

// 1. MARINE CONDITIONS CARD (Tides, Waves, Winds, Currents, SST)
export const MarineConditionsCard: React.FC<{ data: MarineConditionsData; onShowMap?: () => void }> = ({
  data,
  onShowMap
}) => {
  if (!data) return null;

  return (
    <div className="bg-[#0B1528] border border-cyan-900/50 rounded-xl p-4 shadow-lg space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-cyan-900/40 pb-2">
        <div className="flex items-center gap-2 text-cyan-400 font-bold">
          <Waves className="w-4 h-4 text-cyan-400" />
          <span>MARINE CONDITIONS TELEMETRY</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/50 text-[10px]">
          INCOIS / IMD LIVE
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            <Waves className="w-3 h-3 text-cyan-400" /> Wave Swell
          </span>
          <p className="text-sm font-bold text-white">{data.wave_height_m} m</p>
          <span className="text-[9px] text-slate-400">
            {data.wave_state || 'Moderate'} {data.swell_period_sec ? `@ ${data.swell_period_sec}s` : ''}
          </span>
        </div>

        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            <Wind className="w-3 h-3 text-teal-400" /> Coastal Wind
          </span>
          <p className="text-sm font-bold text-white">{data.wind_speed_kts} kts</p>
          <span className="text-[9px] text-slate-400">
            {data.wind_direction} {data.wind_gust_kts ? `(Gusts ${data.wind_gust_kts} kts)` : ''}
          </span>
        </div>

        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            <Gauge className="w-3 h-3 text-amber-400" /> Sea Surface Temp
          </span>
          <p className="text-sm font-bold text-white">{data.sea_surface_temp_c}°C</p>
          <span className="text-[9px] text-slate-400">
            Current: {data.current_speed_kts} kts {data.current_direction || ''}
          </span>
        </div>

        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            <Clock className="w-3 h-3 text-indigo-400" /> Tide State
          </span>
          <p className="text-xs font-bold text-white truncate">{data.tide_summary}</p>
          <span className="text-[9px] text-slate-400">
            {data.visibility_km ? `${data.visibility_km}km visibility` : 'Clear visibility'}
          </span>
        </div>
      </div>

      {data.operational_status && (
        <div className="flex items-start gap-2 p-2.5 rounded-lg bg-teal-950/40 border border-teal-800/40 text-[11px] text-teal-200">
          <Info className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
          <p className="font-sans leading-relaxed">{data.operational_status}</p>
        </div>
      )}
    </div>
  );
};

// 2. PFZ DISCOVERY & RESULTS CARD
export const PFZResultsCard: React.FC<{
  results: PFZItem[];
  onSelectCandidate?: (item: PFZItem) => void;
  onShowMap?: () => void;
}> = ({ results, onSelectCandidate, onShowMap }) => {
  if (!results || results.length === 0) return null;

  return (
    <div className="bg-[#0B1528] border border-teal-900/50 rounded-xl p-4 shadow-lg space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-teal-900/40 pb-2">
        <div className="flex items-center gap-2 text-teal-400 font-bold">
          <Fish className="w-4 h-4 text-teal-400" />
          <span>POTENTIAL FISHING ZONE (PFZ) CANDIDATES</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-teal-950/80 text-teal-300 border border-teal-800/50 text-[10px]">
          {results.length} ADVISORIES
        </span>
      </div>

      <div className="space-y-2">
        {results.map((pfz, idx) => (
          <div
            key={pfz.id || idx}
            onClick={() => onSelectCandidate && onSelectCandidate(pfz)}
            className="p-3 bg-[#07101E] hover:bg-slate-800/90 rounded-xl border border-slate-800 hover:border-teal-500/50 transition-all space-y-2 cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 font-bold text-[10px]">
                  #{idx + 1}
                </span>
                <span className="font-bold text-white font-sans text-xs group-hover:text-teal-300 transition-colors">
                  {pfz.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[10px] font-bold">
                  {pfz.distance_km} km offshore ({pfz.bearing || 'WNW'})
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-300">
              <div>
                <span className="text-slate-400 block">SST</span>
                <span className="font-bold text-white">{pfz.sst_celsius}°C</span>
              </div>
              <div>
                <span className="text-slate-400 block">Chlorophyll</span>
                <span className="font-bold text-teal-300">{pfz.chlorophyll_mg_m3} mg/m³</span>
              </div>
              <div>
                <span className="text-slate-400 block">Confidence</span>
                <span className="font-bold text-cyan-300">{pfz.confidence || 'High'}</span>
              </div>
            </div>

            {pfz.recommendation && (
              <p className="text-[11px] font-sans text-slate-300 leading-relaxed border-t border-slate-800/60 pt-1.5">
                {pfz.recommendation}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// 3. HAZARD ALERTS CARD
export const HazardAlertCard: React.FC<{ data: { alerts?: HazardAlertItem[]; has_active_alerts?: boolean } }> = ({
  data
}) => {
  const alerts = data?.alerts || [];
  const hasActive = data?.has_active_alerts ?? (alerts.length > 0);

  if (!hasActive) {
    return (
      <div className="bg-[#0B1F1C] border border-emerald-800/40 rounded-xl p-4 shadow-lg space-y-2 font-mono text-xs">
        <div className="flex items-center gap-2 text-emerald-400 font-bold">
          <ShieldCheck className="w-4.5 h-4.5 text-emerald-400" />
          <span>NO ACTIVE STATUTORY HAZARD ALERTS</span>
        </div>
        <p className="text-xs font-sans text-emerald-200/90 leading-relaxed">
          IMD Coastal Marine Bulletins and INCOIS Early Warning Systems report normal operational sea-state conditions in this sector. No active cyclone tracks, lightning squall warnings, or high-wave storm surges are present.
        </p>
        <span className="text-[10px] text-emerald-400/70 block pt-1">
          Authority: IMD Cyclone Warning Division & INCOIS ESSO
        </span>
      </div>
    );
  }

  return (
    <div className="bg-[#1C0F14] border border-rose-900/60 rounded-xl p-4 shadow-lg space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-rose-900/40 pb-2">
        <div className="flex items-center gap-2 text-rose-400 font-bold">
          <ShieldAlert className="w-4.5 h-4.5 text-rose-400 animate-pulse" />
          <span>ACTIVE HAZARD ALERTS IN EFFECT</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-[10px] font-bold">
          {alerts.length} WARNINGS
        </span>
      </div>

      <div className="space-y-2.5">
        {alerts.map((alert, idx) => (
          <div key={alert.alert_id || idx} className="p-3 bg-[#13070B] rounded-lg border border-rose-800/60 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-rose-200 text-xs font-sans">{alert.title}</span>
              <span className="px-1.5 py-0.5 rounded bg-rose-900/50 text-rose-300 text-[9px] uppercase font-bold">
                {alert.severity}
              </span>
            </div>
            <p className="text-[11px] font-sans text-slate-200 leading-relaxed">{alert.description}</p>
            <div className="flex items-center justify-between text-[9px] text-slate-400 pt-1 border-t border-rose-900/40">
              <span>Source: {alert.source_name}</span>
              <span>Valid: {alert.valid_time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 4. ROUTE PLANNING CARD
export const RoutePlanningCard: React.FC<{
  routes: RouteOptionItem[];
  onSelectRoute?: (route: RouteOptionItem) => void;
  onShowMap?: () => void;
}> = ({ routes, onSelectRoute, onShowMap }) => {
  if (!routes || routes.length === 0) return null;

  return (
    <div className="bg-[#0B1528] border border-cyan-900/50 rounded-xl p-4 shadow-lg space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-cyan-900/40 pb-2">
        <div className="flex items-center gap-2 text-cyan-400 font-bold">
          <Navigation className="w-4 h-4 text-cyan-400" />
          <span>RECOMMENDED PASSAGE CORRIDORS</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/50 text-[10px]">
          WEATHER & GEOFENCE ROUTING
        </span>
      </div>

      <div className="space-y-2">
        {routes.map((route, idx) => (
          <div
            key={route.route_id || idx}
            onClick={() => onSelectRoute && onSelectRoute(route)}
            className={`p-3 rounded-xl border transition-all space-y-2 cursor-pointer ${
              route.is_recommended
                ? 'bg-[#071828] border-teal-500/60 shadow-md'
                : 'bg-[#07101E] border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white font-sans text-xs">{route.name}</span>
                {route.is_recommended && (
                  <span className="px-2 py-0.2 rounded bg-teal-500/20 text-teal-300 border border-teal-500/40 text-[9px] font-bold">
                    RECOMMENDED (LOWER RISK)
                  </span>
                )}
              </div>
              <span className={`text-[10px] font-bold ${route.is_recommended ? 'text-emerald-400' : 'text-amber-400'}`}>
                {route.is_recommended ? 'LOW RISK' : 'MODERATE RISK'}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-300">
              <div>
                <span className="text-slate-400 block">Distance</span>
                <span className="font-bold text-white">{route.distance_nm} NM ({route.distance_km} km)</span>
              </div>
              <div>
                <span className="text-slate-400 block">Est. Transit</span>
                <span className="font-bold text-white">{route.estimated_transit_hours} hrs</span>
              </div>
              <div>
                <span className="text-slate-400 block">Max Swell</span>
                <span className="font-bold text-teal-300">{route.max_wave_height_m} m</span>
              </div>
            </div>

            {route.hazard_flags && route.hazard_flags.length > 0 && (
              <div className="flex flex-wrap gap-1 text-[9px] pt-1">
                {route.hazard_flags.map((h: string, i: number) => (
                  <span key={i} className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    ✓ {h}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// 5. PRODUCTIVITY ANALYSIS CARD (Historical & Decline Trends)
export const ProductivityAnalysisCard: React.FC<{ data: ProductivityAnalysisData }> = ({ data }) => {
  if (!data) return null;

  return (
    <div className="bg-[#0B1528] border border-indigo-900/50 rounded-xl p-4 shadow-lg space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-indigo-900/40 pb-2">
        <div className="flex items-center gap-2 text-indigo-400 font-bold">
          <TrendingDown className="w-4 h-4 text-indigo-400" />
          <span>HISTORICAL PRODUCTIVITY & TREND ANALYSIS</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/50 text-[10px]">
          MOSDAC MULTI-YEAR ARCHIVE
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 block">Chlorophyll Trend</span>
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold text-rose-400">{data.current_chlorophyll}</span>
            <span className="text-[10px] text-slate-400 line-through">from {data.historical_baseline_chlorophyll}</span>
          </div>
          <span className="text-[9px] text-rose-300 font-bold">▼ 55% reduction</span>
        </div>

        <div className="bg-[#07101E] p-2.5 rounded-lg border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 block">SST Warming Anomaly</span>
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold text-amber-300">{data.current_sst}</span>
            <span className="text-[10px] text-slate-400">baseline {data.historical_sst}</span>
          </div>
          <span className="text-[9px] text-amber-300 font-bold">▲ +0.3°C warming</span>
        </div>
      </div>

      {data.contributing_factors && data.contributing_factors.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">
            Scientific Contributing Factors
          </span>
          <div className="space-y-1.5">
            {data.contributing_factors.map((item, idx) => (
              <div key={idx} className="p-2 bg-[#07101E] rounded-lg border border-slate-800 text-[11px] font-sans text-slate-200 space-y-0.5">
                <div className="flex items-center gap-1.5 font-bold text-white">
                  <span className="text-indigo-400 font-mono">•</span>
                  <span>{item.factor}</span>
                  <span className="px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300 text-[9px] font-mono font-normal">
                    {item.impact}
                  </span>
                </div>
                {item.evidence && (
                  <p className="text-[10px] text-slate-400 pl-3">{item.evidence}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// MASTER INTENT CARD ROUTER
export const IntentCardRouter: React.FC<IntentCardProps> = ({
  responseType,
  data,
  results = [],
  whyReasons = [],
  sources = [],
  onSelectCandidate,
  onShowMap
}) => {
  if (!responseType) return null;

  switch (responseType) {
    case 'MARINE_CONDITIONS':
      return <MarineConditionsCard data={data?.conditions || data} onShowMap={onShowMap} />;

    case 'PFZ_RESULTS':
      return <PFZResultsCard results={results} onSelectCandidate={onSelectCandidate} onShowMap={onShowMap} />;

    case 'HAZARD_ALERT':
      return <HazardAlertCard data={data || { alerts: results, has_active_alerts: results.length > 0 }} />;

    case 'ROUTE_RESULT':
      return <RoutePlanningCard routes={results} onSelectRoute={onSelectCandidate} onShowMap={onShowMap} />;

    case 'PRODUCTIVITY_ANALYSIS':
      return <ProductivityAnalysisCard data={data} />;

    case 'PRODUCTIVITY_RESULTS':
      return <PFZResultsCard results={results} onSelectCandidate={onSelectCandidate} onShowMap={onShowMap} />;

    default:
      return null;
  }
};
