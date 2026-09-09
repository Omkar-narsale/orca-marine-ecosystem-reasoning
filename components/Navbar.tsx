'use client';

import React, { useState, useEffect } from 'react';
import {
  Compass,
  User,
  Cpu,
  Bell,
  Globe,
  FileText,
  Activity,
  SlidersHorizontal,
  Sparkles,
  MapPin,
  ShieldCheck,
  Radio
} from 'lucide-react';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface NavbarProps {
  onOpenArchitectureModal: () => void;
  language?: string;
  onLanguageChange?: (lang: string) => void;
  unreadAlertCount?: number;
  onOpenAlerts?: () => void;
  onOpenMarineBrief?: () => void;
  onOpenWhatIf?: () => void;
  onOpenResearch?: () => void;
  onOpenSystemStatus?: () => void;
  isDemoMode?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenArchitectureModal,
  language = 'en',
  onLanguageChange,
  unreadAlertCount = 0,
  onOpenAlerts,
  onOpenMarineBrief,
  onOpenWhatIf,
  onOpenResearch,
  onOpenSystemStatus,
  isDemoMode = false,
}) => {
  const [currentTime, setCurrentTime] = useState<string>('');
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const formatted =
        now.toLocaleDateString('en-IN', {
          day: '2-digit',
          month: 'short',
        }) +
        ' · ' +
        now.toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        }) +
        ' IST';
      setCurrentTime(formatted);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-[60px] w-full bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800/80 shrink-0 sticky top-0 z-50 text-slate-200">
      <div className="w-full px-4 lg:px-6 h-full flex items-center justify-between gap-3">
        {/* Left: Brand Identity & Telemetry Status */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center font-bold shadow-xs">
            <Compass className="w-4 h-4 animate-spin-slow" />
          </div>
          <div className="flex items-center gap-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-extrabold tracking-wider text-white font-mono">
                  ORCA
                </span>
                <span className="text-[11px] font-semibold text-teal-400/90 pl-2 border-l border-slate-700 hidden sm:inline">
                  Marine Intelligence
                </span>
              </div>
            </div>

            {/* Live Scientific Data Trust Pill */}
            <div className="hidden md:flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold tracking-tight bg-slate-900/80 border border-slate-700/80 text-slate-300">
              <span className={`w-1.5 h-1.5 rounded-full ${isDemoMode ? 'bg-amber-400' : 'bg-emerald-400 pulse-indicator'}`}></span>
              <span>{isDemoMode ? 'DEMO SIMULATION' : 'LIVE SCIENTIFIC TELEMETRY'}</span>
            </div>
          </div>
        </div>

        {/* Center: Command Center Workstation Actions */}
        <div className="flex items-center gap-1.5">
          {/* Real-time System Status */}
          {onOpenSystemStatus && (
            <button
              onClick={onOpenSystemStatus}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-slate-300 bg-slate-900/60 hover:bg-slate-800 border border-slate-700/70 hover:border-slate-600 transition-colors"
              title="View Real-Time System Health & Source Connectors"
            >
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              <span className="hidden sm:inline">Status</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            </button>
          )}

          {/* What-If Scenario Simulation Drawer Trigger */}
          {onOpenWhatIf && (
            <button
              onClick={onOpenWhatIf}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition-colors"
              title="Simulate Parameter Modifications (Waves, Wind, Geofences)"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">What-If?</span>
            </button>
          )}

          {/* Research & Benchmark Evaluation Workspace Trigger */}
          {onOpenResearch && (
            <button
              onClick={onOpenResearch}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-purple-300 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 transition-colors"
              title="Open Research Benchmark Evaluation Workbench"
            >
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
              <span className="hidden sm:inline">Research</span>
            </button>
          )}

          {/* Active Safety Alerts Indicator */}
          {onOpenAlerts && (
            <button
              onClick={onOpenAlerts}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition-all ${
                unreadAlertCount > 0
                  ? 'bg-rose-500/15 text-rose-300 border-rose-500/40 hover:bg-rose-500/25 animate-pulse'
                  : 'bg-slate-900/60 text-slate-400 border-slate-700/70 hover:bg-slate-800'
              }`}
              title="Active Marine Safety Alerts"
            >
              <Bell className={`w-3.5 h-3.5 ${unreadAlertCount > 0 ? 'text-rose-400' : 'text-slate-400'}`} />
              <span className="hidden sm:inline">{t.alerts}</span>
              {unreadAlertCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[10px] font-mono font-bold">
                  {unreadAlertCount}
                </span>
              )}
            </button>
          )}

          {/* Operational Marine Intelligence Brief */}
          {onOpenMarineBrief && (
            <button
              onClick={onOpenMarineBrief}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 transition-colors"
              title="Generate Operational Marine Intelligence Brief"
            >
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden md:inline">{t.marineBrief}</span>
            </button>
          )}
        </div>

        {/* Right: Language, Clock & Officer Profile */}
        <div className="flex items-center gap-2.5 text-xs">
          {/* Language Selector Dropdown */}
          {onLanguageChange && (
            <div className="flex items-center gap-1 bg-slate-900/90 px-2 py-1 rounded-md border border-slate-700/80">
              <Globe className="w-3.5 h-3.5 text-teal-400" />
              <select
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
                className="bg-transparent text-xs font-mono font-semibold text-slate-200 focus:outline-none cursor-pointer"
                title="Select Response Language"
              >
                <option value="en" className="bg-slate-900 text-slate-200">EN</option>
                <option value="hi" className="bg-slate-900 text-slate-200">हिन्दी</option>
                <option value="mr" className="bg-slate-900 text-slate-200">मराठी</option>
              </select>
            </div>
          )}

          {/* Real-time Clock */}
          <span className="font-mono text-[11px] text-slate-400 hidden xl:inline-block">
            {currentTime || 'IST'}
          </span>

          {/* Architecture Spec Button */}
          <button
            onClick={onOpenArchitectureModal}
            className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-semibold text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-700/70 rounded-md transition-colors"
            title="View SIH 2026 Architecture Specification"
          >
            <Radio className="w-3.5 h-3.5 text-teal-400" />
            <span>SIH 2026</span>
          </button>

          <div className="h-4 w-px bg-slate-800 hidden sm:block"></div>

          {/* Officer Profile */}
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-slate-800 border border-teal-500/30 text-teal-300 flex items-center justify-center font-semibold text-xs shadow-inner">
              <User className="w-3.5 h-3.5" />
            </div>
            <span className="font-mono font-medium text-slate-300 hidden 2xl:inline-block text-xs">
              {t.officer}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
