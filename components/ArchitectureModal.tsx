'use client';

import React from 'react';
import { X, Cpu, CheckCircle2, ArrowRight, FileCode } from 'lucide-react';

interface ArchitectureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ArchitectureModal: React.FC<ArchitectureModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-y-auto border border-slate-200 shadow-2xl relative z-[100000]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-marine-950 text-teal-400 flex items-center justify-center font-bold">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                ORCA System Architecture & Methodology
              </h2>
              <p className="text-[11px] text-slate-500">
                SIH 2026 Phase 1 Prototype & Phase 2 Roadmap
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-800 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6 text-xs text-slate-700">
          {/* Phase 1 vs Phase 2 Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-xs uppercase">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Phase 1 (Current Scope)</span>
              </div>
              <ul className="text-[11px] text-slate-600 space-y-1">
                <li>• Map-first desktop operations workspace</li>
                <li>• Interactive Leaflet map (Mumbai coastal reach)</li>
                <li>• Realistic GeoJSON sectors (Zone A, B, C, D)</li>
                <li>• Natural language spatial-temporal intent parser</li>
                <li>• Multi-agent reasoning trace visualization</li>
                <li>• Scientific Forecast vs Observation distinction</li>
                <li>• Authoritative source provenance metadata</li>
              </ul>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-xs uppercase">
                <ArrowRight className="w-3.5 h-3.5 text-teal-600" />
                <span>Phase 2 (Production Scope)</span>
              </div>
              <ul className="text-[11px] text-slate-600 space-y-1">
                <li>• INCOIS ERDDAP / OPeNDAP automated data pullers</li>
                <li>• IMD Coastal marine bulletin scraper & radar feed</li>
                <li>• MOSDAC ISRO OCM-3 Ocean Color raster pipeline</li>
                <li>• Agentic AI Orchestrator (LangGraph / AutoGen)</li>
                <li>• PostGIS real-time AIS vessel & geofence tracking</li>
                <li>• Vernacular voice/SMS engine for fishing communities</li>
              </ul>
            </div>
          </div>

          {/* JSON Schema */}
          <div className="p-4 bg-slate-950 text-slate-300 rounded-xl font-mono text-[10px] overflow-x-auto">
            <div className="flex items-center justify-between text-teal-400 font-bold mb-2 pb-1 border-b border-slate-800">
              <span className="flex items-center gap-1.5">
                <FileCode className="w-3 h-3" />
                <span>Phase 2 Agent Response Contract</span>
              </span>
              <span className="text-slate-500">JSON API</span>
            </div>
            <pre>{`{
  "query": "Which fishing zones should be avoided tomorrow?",
  "intent": "Fishing Safety",
  "location": "Mumbai Coastal Region",
  "time": "Tomorrow — 06:00 IST",
  "zones": [ ... ],
  "recommendations": { "avoid": ["Zone A", "Zone B"], "candidate": ["Zone C"] },
  "evidence": [ "INCOIS", "IMD", "MOSDAC", "GIS" ],
  "confidence": { "level": "High", "score": 88 }
}`}</pre>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-marine-950 hover:bg-marine-900 text-teal-400 rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
