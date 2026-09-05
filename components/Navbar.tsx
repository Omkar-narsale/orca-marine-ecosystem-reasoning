import React, { useState, useEffect } from 'react';
import { Compass, User, Cpu, Bell, Globe, FileText, Activity } from 'lucide-react';
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
  isDemoMode = false
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
    <header className="h-[72px] w-full bg-white border-b border-slate-200/70 shrink-0 sticky top-0 z-50">
      <div className="max-w-[1520px] mx-auto h-full px-6 flex items-center justify-between gap-4">
        {/* Left: Brand / Title */}
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-lg bg-marine-950 text-teal-400 flex items-center justify-center font-bold shadow-sm">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-tight text-marine-950">
                {t.brandTitle}
              </span>
              <span className="text-xs font-semibold text-slate-600 pl-2 border-l border-slate-300">
                Decision Intelligence
              </span>
              {/* Trust / Data Status Badge */}
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-tight ${
                isDemoMode 
                  ? 'bg-amber-100 text-amber-900 border border-amber-300' 
                  : 'bg-emerald-50 text-emerald-800 border border-emerald-300'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isDemoMode ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
                <span>{isDemoMode ? 'CONTROLLED DEMO DATA' : 'LIVE SCIENTIFIC DATA'}</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-normal leading-none mt-0.5">
              {t.brandSubtitle}
            </p>
          </div>
        </div>

        {/* Center: System Status, What-If, Research, Alerts */}
        <div className="flex items-center gap-2">
          {/* Compact System Status Trigger */}
          {onOpenSystemStatus && (
            <button
              onClick={onOpenSystemStatus}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 transition-colors shadow-xs"
              title="View Real-Time System Health & Source Status"
            >
              <Activity className="w-3.5 h-3.5 text-teal-600" />
              <span>Status</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            </button>
          )}

          {/* What-If Scenario Trigger */}
          {onOpenWhatIf && (
            <button
              onClick={onOpenWhatIf}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-amber-900 bg-amber-50 hover:bg-amber-100 border border-amber-200/70 transition-colors shadow-xs"
              title="Run What-If Scenario Simulations"
            >
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              <span>What-If?</span>
            </button>
          )}

          {/* Research & Evaluation Modal Trigger */}
          {onOpenResearch && (
            <button
              onClick={onOpenResearch}
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-purple-900 bg-purple-50 hover:bg-purple-100 border border-purple-200/70 transition-colors shadow-xs"
              title="View Research Evaluation & Benchmarks"
            >
              <Cpu className="w-3.5 h-3.5 text-purple-600" />
              <span>Research</span>
            </button>
          )}

          {/* Proactive Safety Alerts Button */}
          {onOpenAlerts && (
            <button
              onClick={onOpenAlerts}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border transition-all ${
                unreadAlertCount > 0
                  ? 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'
                  : 'bg-slate-50 text-slate-600 border-slate-200/60 hover:bg-slate-100'
              }`}
              title="Active Marine Safety Alerts"
            >
              <Bell className={`w-3.5 h-3.5 ${unreadAlertCount > 0 ? 'text-rose-600' : 'text-slate-500'}`} />
              <span>{t.alerts}</span>
              {unreadAlertCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[10px] font-mono font-bold">
                  {unreadAlertCount}
                </span>
              )}
            </button>
          )}

          {/* Marine Brief Report Button */}
          {onOpenMarineBrief && (
            <button
              onClick={onOpenMarineBrief}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-marine-900 bg-cyan-50 hover:bg-cyan-100/80 border border-cyan-200/70 transition-colors"
              title="Generate Operational Marine Intelligence Brief"
            >
              <FileText className="w-3.5 h-3.5 text-cyan-600" />
              <span>{t.marineBrief}</span>
            </button>
          )}
        </div>

        {/* Right: Language Selector, Metadata & Profile */}
        <div className="flex items-center gap-3.5 text-xs">
          {/* Language Selector Dropdown */}
          {onLanguageChange && (
            <div className="flex items-center gap-1 bg-slate-100/80 px-2.5 py-1.5 rounded-md border border-slate-200 shadow-xs">
              <Globe className="w-3.5 h-3.5 text-teal-600" />
              <select
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
                className="bg-transparent text-xs font-bold text-slate-800 focus:outline-none cursor-pointer"
                title="Select Response Language"
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="mr">मराठी (Marathi)</option>
              </select>
            </div>
          )}

          <span className="font-mono text-slate-500 hidden lg:inline-block">
            {currentTime || 'Loading clock...'}
          </span>

          <button
            onClick={onOpenArchitectureModal}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-marine-900 bg-slate-100 hover:bg-slate-200/80 rounded-md transition-colors"
            title="View SIH 2026 Architecture Specification"
          >
            <Cpu className="w-3.5 h-3.5 text-slate-600" />
            <span>SIH 2026</span>
          </button>

          <div className="h-4 w-px bg-slate-200 hidden sm:block"></div>

          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-teal-300 flex items-center justify-center font-semibold text-xs">
              <User className="w-3.5 h-3.5" />
            </div>
            <span className="font-medium text-slate-700 hidden xl:inline-block text-xs">
              {t.officer}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
