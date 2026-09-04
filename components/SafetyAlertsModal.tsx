'use client';

import React from 'react';
import { MarineSafetyAlert } from '@/types/marine';
import { acknowledgeAlert } from '@/lib/apiClient';

interface SafetyAlertsModalProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: MarineSafetyAlert[];
  onSelectZone: (zoneId: string) => void;
  onAlertAcknowledged?: (alertId: string) => void;
}

export default function SafetyAlertsModal({
  isOpen,
  onClose,
  alerts,
  onSelectZone,
  onAlertAcknowledged
}: SafetyAlertsModalProps) {
  if (!isOpen) return null;

  const handleAcknowledge = async (alertId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await acknowledgeAlert(alertId);
    if (onAlertAcknowledged) {
      onAlertAcknowledged(alertId);
    }
  };

  const handleAlertClick = (zoneId: string) => {
    onSelectZone(zoneId);
    onClose();
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-300 border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
      case 'WARNING':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
    }
  };

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className="w-full max-w-2xl max-h-[85vh] bg-[#0c121e] border border-cyan-500/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden relative z-[100000]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-cyan-500/20 bg-[#090d16]/90">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </span>
            <div>
              <div className="text-[10px] font-mono tracking-widest uppercase text-red-400 font-semibold">Deterministic Alert Center</div>
              <h2 className="text-base font-bold text-white">Active Marine Safety Alerts ({alerts.length})</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Alert List */}
        <div className="p-6 overflow-y-auto space-y-3.5">
          {alerts.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              ✓ No active hazard alerts detected in currently evaluated operational zones.
            </div>
          ) : (
            alerts.map((al) => (
              <div
                key={al.alert_id}
                onClick={() => handleAlertClick(al.zone_id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer hover:border-cyan-500/50 ${
                  al.severity === 'HIGH' || al.severity === 'CRITICAL'
                    ? 'bg-red-950/20 border-red-500/30'
                    : 'bg-slate-900/50 border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSeverityBadge(al.severity)}`}>
                        {al.severity}
                      </span>
                      <span className="text-xs font-bold text-white font-mono">{al.zone_code}</span>
                      <span className="text-[11px] text-slate-400">· {al.zone_name}</span>
                    </div>
                    <h3 className="text-sm font-semibold text-slate-200">{al.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{al.message}</p>
                    <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
                      <span>Source: <strong className="text-slate-300">{al.source_name}</strong></span>
                      <span>Validity: <strong className="text-amber-300">{al.valid_time}</strong></span>
                      {al.value && <span>Value: <strong className="text-cyan-300">{al.value}</strong></span>}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <button
                      onClick={(e) => handleAcknowledge(al.alert_id, e)}
                      className="px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-[11px] font-mono text-slate-300 hover:text-white border border-slate-700 transition-colors"
                      title="Mark alert as acknowledged"
                    >
                      {al.acknowledged ? '✓ Acknowledged' : 'Mark Viewed'}
                    </button>
                    <span className="text-[10px] text-cyan-400 flex items-center gap-1">
                      <span>Zoom Zone</span>
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-[#090d16]/95 flex items-center justify-between text-xs text-slate-400">
          <span>Clicking any alert automatically focuses the affected sector on the marine map.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium border border-slate-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
