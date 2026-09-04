import React from 'react';

export const FooterBar: React.FC = () => {
  return (
    <footer className="w-full bg-white border-t border-slate-200/70 py-4 px-6 mt-12 text-[11px] text-slate-500">
      <div className="max-w-[1520px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-900">ORCA</span>
          <span className="text-slate-300">·</span>
          <span>Marine EcOsystem Reasoning with Collaborative Agents</span>
        </div>

        <div className="flex items-center gap-3">
          <span>SIH 2026 Prototype</span>
          <span className="text-slate-300">·</span>
          <span className="font-mono text-slate-400">Desktop Command Console</span>
        </div>
      </div>
    </footer>
  );
};
