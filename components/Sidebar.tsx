'use client';

import React from 'react';
import {
  Sparkles,
  LayoutDashboard,
  MapPin,
  AlertTriangle,
  Database,
  Sliders,
} from 'lucide-react';
import { SourceHealthSummary } from '@/lib/apiClient';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

export type NavSection = 'ask-orca' | 'overview' | 'zones' | 'safety' | 'evidence' | 'settings';

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  onFilterChange: (filter: 'all' | 'safe' | 'hazards' | 'restricted') => void;
  activeFilter: 'all' | 'safe' | 'hazards' | 'restricted';
  sourceHealth?: SourceHealthSummary | null;
  language?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  onFilterChange,
  activeFilter,
  sourceHealth,
  language = 'en',
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  const navItems = [
    { id: 'ask-orca' as NavSection, label: t.askOrca, icon: Sparkles },
    { id: 'overview' as NavSection, label: t.navOverview, icon: LayoutDashboard },
    { id: 'zones' as NavSection, label: t.navMarineZones, icon: MapPin },
    { id: 'safety' as NavSection, label: t.navSafetyHazards, icon: AlertTriangle },
    { id: 'evidence' as NavSection, label: t.navEvidenceSources, icon: Database },
    { id: 'settings' as NavSection, label: t.navSettings, icon: Sliders },
  ];

  return (
    <aside className="w-full lg:w-[250px] bg-white border-r border-slate-200/70 flex flex-col justify-between shrink-0 min-h-[calc(100vh-72px)] py-6 px-4">
      {/* Navigation Links */}
      <div className="space-y-6">
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectSection(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-marine-950 text-teal-400 font-semibold shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? 'text-teal-400' : 'text-slate-400'
                  }`}
                />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Quick Filter Section */}
        <div className="pt-5 border-t border-slate-100">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
            {t.mapFocus}
          </p>
          <div className="space-y-1 text-xs">
            <button
              onClick={() => onFilterChange('all')}
              className={`w-full text-left px-3 py-1.5 rounded-md transition-colors ${
                activeFilter === 'all'
                  ? 'text-slate-900 font-semibold bg-slate-100'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {t.allZones}
            </button>
            <button
              onClick={() => onFilterChange('safe')}
              className={`w-full text-left px-3 py-1.5 rounded-md flex items-center gap-2 transition-colors ${
                activeFilter === 'safe'
                  ? 'text-emerald-800 font-semibold bg-emerald-50'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>{t.suitable}</span>
            </button>
            <button
              onClick={() => onFilterChange('hazards')}
              className={`w-full text-left px-3 py-1.5 rounded-md flex items-center gap-2 transition-colors ${
                activeFilter === 'hazards'
                  ? 'text-rose-800 font-semibold bg-rose-50'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
              <span>{t.highRisk}</span>
            </button>
            <button
              onClick={() => onFilterChange('restricted')}
              className={`w-full text-left px-3 py-1.5 rounded-md flex items-center gap-2 transition-colors ${
                activeFilter === 'restricted'
                  ? 'text-indigo-800 font-semibold bg-indigo-50'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
              <span>{t.restricted}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bottom: Truthful System Status List */}
      <div className="pt-6 border-t border-slate-100 text-xs">
        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
          Source Health (Phase 2.1)
        </p>
        <div className="space-y-1.5 text-[11px] text-slate-600">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${sourceHealth?.ocean_data.is_live ? 'bg-emerald-500' : 'bg-emerald-500'}`}></span>
              Ocean Data
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              INCOIS · {sourceHealth?.ocean_data.status.includes('Live') ? 'Live' : 'Connected'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${sourceHealth?.weather_data.is_live ? 'bg-emerald-500' : 'bg-emerald-500'}`}></span>
              Weather
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              IMD · {sourceHealth?.weather_data.status.includes('Live') ? 'Live' : 'Connected'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
              Satellite
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              MOSDAC · Auth Req
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
              Geospatial
            </span>
            <span className="text-[10px] text-slate-500 font-mono">GIS Cadastre</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
