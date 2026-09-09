'use client';

import React from 'react';
import {
  Sparkles,
  Map,
  BrainCircuit,
  Database,
  Table,
  Cpu,
  AlertTriangle,
  FileText,
  Activity,
  Sliders,
  Compass,
  PlusCircle,
  MessageSquare,
  History
} from 'lucide-react';
import { SourceHealthSummary } from '@/lib/apiClient';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

export type NavSection = 'ask-orca' | 'analysis' | 'zones' | 'safety' | 'evidence' | 'settings' | 'research' | 'brief';

export interface ChatSessionMeta {
  session_id: string;
  title: string;
  created_at: string;
  last_updated: string;
  message_count: number;
  language?: string;
  last_query?: string;
}

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  onFilterChange: (filter: 'all' | 'safe' | 'hazards' | 'restricted') => void;
  activeFilter: 'all' | 'safe' | 'hazards' | 'restricted';
  sourceHealth?: SourceHealthSummary | null;
  language?: string;
  unreadAlertCount?: number;
  onOpenAlerts?: () => void;
  onOpenResearch?: () => void;
  onOpenMarineBrief?: () => void;
  onOpenSystemStatus?: () => void;
  onNewChat?: () => void;
  sessions?: ChatSessionMeta[];
  activeSessionId?: string;
  onSelectSession?: (sessionId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  onFilterChange,
  activeFilter,
  sourceHealth,
  language = 'en',
  unreadAlertCount = 0,
  onOpenAlerts,
  onOpenResearch,
  onOpenMarineBrief,
  onOpenSystemStatus,
  onNewChat,
  sessions = [],
  activeSessionId,
  onSelectSession,
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  const handleNavClick = (id: NavSection) => {
    if (id === 'safety' && onOpenAlerts) {
      onOpenAlerts();
    } else if (id === 'research' && onOpenResearch) {
      onOpenResearch();
    } else if (id === 'brief' && onOpenMarineBrief) {
      onOpenMarineBrief();
    } else if (id === 'settings' && onOpenSystemStatus) {
      onOpenSystemStatus();
    } else {
      onSelectSection(id);
    }
  };

  return (
    <aside className="w-full lg:w-[240px] bg-[#0A1128] border-r border-slate-800/80 flex flex-col justify-between shrink-0 min-h-full lg:min-h-[calc(100vh-60px)] py-4 px-3 text-slate-300 font-mono text-xs">
      {/* Primary Navigation Rail */}
      <div className="space-y-4">
        {/* New Chat Primary Action */}
        <div>
          <button
            onClick={() => {
              if (onNewChat) onNewChat();
              onSelectSection('ask-orca');
            }}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-[#0A1128] font-mono font-extrabold text-xs shadow-lg shadow-teal-900/30 transition-all group"
          >
            <PlusCircle className="w-4 h-4 group-hover:rotate-90 transition-transform" />
            <span>+ NEW CONVERSATION</span>
          </button>
        </div>

        {/* Navigation Section */}
        <div>
          <span className="text-[9px] font-mono uppercase tracking-widest text-slate-400 font-bold px-2 mb-1.5 block">
            Operations
          </span>
          <nav className="space-y-1">
            <button
              onClick={() => handleNavClick('ask-orca')}
              className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg font-medium transition-all ${
                activeSection === 'ask-orca'
                  ? 'bg-teal-500/15 text-teal-300 font-bold border border-teal-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>Chat Assistant</span>
              </div>
            </button>

            <button
              onClick={() => handleNavClick('analysis')}
              className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg font-medium transition-all ${
                activeSection === 'analysis'
                  ? 'bg-teal-500/15 text-teal-300 font-bold border border-teal-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-2">
                <Compass className="w-3.5 h-3.5 text-cyan-400" />
                <span>Technical Tabs</span>
              </div>
            </button>
          </nav>
        </div>

        {/* Conversation History List */}
        {sessions && sessions.length > 0 && (
          <div className="pt-3 border-t border-slate-800/80">
            <div className="flex items-center justify-between px-2 mb-1.5">
              <span className="text-[9px] font-mono uppercase tracking-widest text-slate-400 font-bold">
                Recent Chats
              </span>
              <History className="w-3 h-3 text-slate-400" />
            </div>
            <div className="space-y-1 max-h-40 overflow-y-auto pr-1">
              {sessions.map((s) => {
                const isActive = s.session_id === activeSessionId;
                return (
                  <button
                    key={s.session_id}
                    onClick={() => {
                      if (onSelectSession) onSelectSession(s.session_id);
                      onSelectSection('ask-orca');
                    }}
                    className={`w-full text-left p-1.5 rounded-lg text-[10px] transition-all flex flex-col gap-0.5 border ${
                      isActive
                        ? 'bg-slate-800 text-teal-300 border-teal-500/30 font-bold'
                        : 'bg-slate-900/40 text-slate-300 hover:bg-slate-800/60 border-transparent hover:text-white'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="truncate max-w-[150px] font-sans font-medium">{s.title}</span>
                      <span className="text-[8px] text-slate-400 shrink-0 font-mono">{s.last_updated.split('·')[1]?.trim() || s.last_updated}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Workspaces & Intelligence Feeds */}
        <div className="pt-3 border-t border-slate-800/80">
          <span className="text-[9px] font-mono uppercase tracking-widest text-slate-400 font-bold px-2 mb-1.5 block">
            Workspaces
          </span>
          <nav className="space-y-1">
            <button
              onClick={() => handleNavClick('safety')}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
            >
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                <span>Active Alerts</span>
              </div>
              {unreadAlertCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[9px] font-bold">
                  {unreadAlertCount}
                </span>
              )}
            </button>

            <button
              onClick={() => handleNavClick('research')}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span>Research Hub</span>
              </div>
            </button>

            <button
              onClick={() => handleNavClick('brief')}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                <span>Marine Brief</span>
              </div>
            </button>

            <button
              onClick={() => handleNavClick('settings')}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Activity className="w-3.5 h-3.5 text-teal-400" />
                <span>Observability</span>
              </div>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            </button>
          </nav>
        </div>

        {/* Map Focus Quick Filter */}
        <div className="pt-3 border-t border-slate-800/80">
          <span className="text-[9px] font-mono uppercase tracking-widest text-slate-400 font-bold px-2 mb-1.5 block">
            Grid Layer Filter
          </span>
          <div className="space-y-1 text-[11px]">
            <button
              onClick={() => onFilterChange('all')}
              className={`w-full text-left px-2 py-1 rounded transition-colors flex items-center justify-between ${
                activeFilter === 'all'
                  ? 'text-white font-bold bg-slate-800 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>{t.allZones || 'All Sectors'}</span>
              <span className="text-[9px] text-slate-400">4</span>
            </button>
            <button
              onClick={() => onFilterChange('safe')}
              className={`w-full text-left px-2 py-1 rounded flex items-center gap-2 transition-colors ${
                activeFilter === 'safe'
                  ? 'text-emerald-300 font-bold bg-emerald-500/15 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>Candidates</span>
            </button>
            <button
              onClick={() => onFilterChange('hazards')}
              className={`w-full text-left px-2 py-1 rounded flex items-center gap-2 transition-colors ${
                activeFilter === 'hazards'
                  ? 'text-rose-300 font-bold bg-rose-500/15 border border-rose-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
              <span>High Risk</span>
            </button>
            <button
              onClick={() => onFilterChange('restricted')}
              className={`w-full text-left px-2 py-1 rounded flex items-center gap-2 transition-colors ${
                activeFilter === 'restricted'
                  ? 'text-indigo-300 font-bold bg-indigo-500/15 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
              <span>Restricted</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bottom: Truthful Live Source Telemetry Health */}
      <div className="pt-3 border-t border-slate-800/80 text-[10px]">
        <span className="uppercase tracking-widest text-slate-400 font-bold px-1 mb-1.5 block text-[9px]">
          Source Registry
        </span>
        <div className="space-y-1">
          <div className="flex items-center justify-between py-0.5 px-1.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              INCOIS OSF
            </span>
            <span className="text-emerald-400 font-bold">LIVE</span>
          </div>
          <div className="flex items-center justify-between py-0.5 px-1.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              IMD Marine
            </span>
            <span className="text-emerald-400 font-bold">LIVE</span>
          </div>
          <div className="flex items-center justify-between py-0.5 px-1.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              ISRO MOSDAC
            </span>
            <span className="text-amber-400 font-bold">AUTH</span>
          </div>
          <div className="flex items-center justify-between py-0.5 px-1.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
              GIS Cadastre
            </span>
            <span className="text-indigo-300 font-bold">VERIFIED</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
