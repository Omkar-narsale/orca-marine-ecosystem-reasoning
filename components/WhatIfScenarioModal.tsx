'use client';

import React, { useState } from 'react';
import { runWhatIfScenario, resetScenario } from '@/lib/apiClient';

interface WhatIfScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScenarioApplied?: (result: any) => void;
}

export default function WhatIfScenarioModal({ isOpen, onClose, onScenarioApplied }: WhatIfScenarioModalProps) {
  const [waveDelta, setWaveDelta] = useState<number>(1.0);
  const [windDelta, setWindDelta] = useState<number>(5.0);
  const [targetZone, setTargetZone] = useState<string>('zone-c');
  const [geofenceOverride, setGeofenceOverride] = useState<string>('');
  const [timeShift, setTimeShift] = useState<string>('Tomorrow 18:00 IST');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [scenarioResult, setScenarioResult] = useState<any | null>(null);

  if (!isOpen) return null;

  const handleRunScenario = async () => {
    setIsSimulating(true);
    try {
      const result = await runWhatIfScenario({
        wave_delta_m: waveDelta,
        wind_delta_kt: windDelta,
        target_zone_id: targetZone,
        geofence_override_zone_id: geofenceOverride || undefined,
        scenario_time_label: timeShift
      });
      setScenarioResult(result);
      if (onScenarioApplied) onScenarioApplied(result);
    } catch (err) {
      console.error('Failed executing scenario:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = async () => {
    setIsSimulating(true);
    try {
      await resetScenario();
      setWaveDelta(0);
      setWindDelta(0);
      setGeofenceOverride('');
      setScenarioResult(null);
      if (onScenarioApplied) onScenarioApplied(null);
    } catch (err) {
      console.error('Failed resetting scenario:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="w-full max-w-2xl max-h-[90vh] bg-[#0c121e] border border-amber-500/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden relative z-[100000]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-amber-500/20 bg-[#090d16]/90">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </span>
            <div>
              <div className="text-[10px] font-mono tracking-widest uppercase text-amber-400 font-semibold">Hypothetical Simulation Engine</div>
              <h2 className="text-base font-bold text-white">What-If Scenario Reasoning</h2>
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

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Simulation Disclaimer Banner */}
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2.5">
            <svg className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <span className="font-semibold text-amber-200 uppercase tracking-wider text-[11px] block">Simulated Scenario — Mathematical Modeling Only</span>
              Controlled modifications do NOT alter raw authoritative forecast records. Reruns deterministic risk and suitability engines to evaluate operational sensitivity.
            </div>
          </div>

          {/* Sliders and Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Wave Height Delta */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium">Wave Height Modification</span>
                <span className="font-mono text-cyan-400 font-bold">{waveDelta > 0 ? `+${waveDelta}` : waveDelta} m</span>
              </div>
              <input
                type="range"
                min="-1.0"
                max="3.0"
                step="0.5"
                value={waveDelta}
                onChange={(e) => setWaveDelta(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>-1.0m (Calmer)</span>
                <span>0.0m</span>
                <span>+3.0m (Rough)</span>
              </div>
            </div>

            {/* Wind Speed Delta */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium">Wind Speed Modification</span>
                <span className="font-mono text-amber-400 font-bold">{windDelta > 0 ? `+${windDelta}` : windDelta} kt</span>
              </div>
              <input
                type="range"
                min="-5"
                max="20"
                step="2.5"
                value={windDelta}
                onChange={(e) => setWindDelta(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>-5kt</span>
                <span>0kt</span>
                <span>+20kt (Gale)</span>
              </div>
            </div>
          </div>

          {/* Additional Options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">Target Operational Sector</label>
              <select
                value={targetZone}
                onChange={(e) => setTargetZone(e.target.value)}
                className="w-full p-2 rounded-lg bg-slate-900 border border-slate-800 text-white font-mono"
              >
                <option value="zone-c">Zone C (South Sector)</option>
                <option value="zone-d">Zone D (Mid-Shelf Trench)</option>
                <option value="zone-a">Zone A (North Reach)</option>
                <option value="all">All Operational Zones</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400 text-[11px] block mb-1">Temporal Window Shift</label>
              <select
                value={timeShift}
                onChange={(e) => setTimeShift(e.target.value)}
                className="w-full p-2 rounded-lg bg-slate-900 border border-slate-800 text-white font-mono"
              >
                <option value="Tomorrow 06:00 IST">Tomorrow 06:00 IST (Dawn)</option>
                <option value="Tomorrow 12:00 IST">Tomorrow 12:00 IST (Noon)</option>
                <option value="Tomorrow 18:00 IST">Tomorrow 18:00 IST (Dusk)</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400 text-[11px] block mb-1">Simulate Geofence Restriction</label>
              <select
                value={geofenceOverride}
                onChange={(e) => setGeofenceOverride(e.target.value)}
                className="w-full p-2 rounded-lg bg-slate-900 border border-slate-800 text-white font-mono"
              >
                <option value="">None (Current Geofences)</option>
                <option value="zone-c">Restrict Zone C (Naval Buffer)</option>
                <option value="zone-d">Restrict Zone D (Fairway)</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleRunScenario}
              disabled={isSimulating}
              className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold text-xs tracking-wide shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center gap-2"
            >
              {isSimulating ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Recomputing Deterministic Risk...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Run What-If Scenario</span>
                </>
              )}
            </button>

            <button
              onClick={handleReset}
              className="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 transition-colors"
            >
              Reset to Baseline
            </button>
          </div>

          {/* Simulation Output Card */}
          {scenarioResult && (
            <div className="mt-4 p-5 rounded-xl bg-[#090d16] border border-amber-500/30 space-y-4 animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold">
                  {scenarioResult.scenario_label}
                </span>
                <span className="text-xs text-slate-400 font-mono">{scenarioResult.scenario_title}</span>
              </div>

              {/* Delta Comparison Matrix */}
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Operational Risk Shift</div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-lg font-bold text-slate-300">{scenarioResult.baseline_comparison.baseline_risk}</span>
                    <span className="text-xs text-slate-400">→</span>
                    <span className={`text-xl font-bold font-mono ${parseInt(scenarioResult.baseline_comparison.simulated_risk) >= 60 ? 'text-rose-400' : 'text-amber-400'}`}>
                      {scenarioResult.baseline_comparison.simulated_risk}
                    </span>
                    <span className="text-xs font-mono text-rose-400 font-semibold">({scenarioResult.baseline_comparison.risk_delta})</span>
                  </div>
                </div>

                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Suitability Score Shift</div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-lg font-bold text-slate-300">{scenarioResult.baseline_comparison.baseline_suitability}</span>
                    <span className="text-xs text-slate-400">→</span>
                    <span className="text-xl font-bold font-mono text-cyan-400">
                      {scenarioResult.baseline_comparison.simulated_suitability}
                    </span>
                    <span className="text-xs font-mono text-cyan-400 font-semibold">({scenarioResult.baseline_comparison.suitability_delta})</span>
                  </div>
                </div>
              </div>

              {/* Grounded Narrative Explanation */}
              <div className="text-xs text-slate-200 leading-relaxed bg-slate-900/40 p-3 rounded-lg border border-slate-800/80">
                <span className="font-semibold text-amber-300 block mb-1">Simulated Decision Rationale:</span>
                {scenarioResult.explanation}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
