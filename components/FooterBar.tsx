import React from 'react';

export const FooterBar: React.FC = () => {
  return (
    <footer className="w-full bg-[#0A1128] border-t border-slate-800/80 py-3.5 px-6 mt-8 text-[11px] font-mono text-slate-400">
      <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-2.5">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-white tracking-wider">ORCA v6.0.0</span>
          <span className="text-slate-600">·</span>
          <span className="text-slate-300">Marine EcOsystem Reasoning with Collaborative Agents</span>
        </div>

        <div className="flex items-center gap-3 text-[10px]">
          <span className="text-teal-400">Smart India Hackathon 2026</span>
          <span className="text-slate-600">·</span>
          <span className="text-slate-400">Autonomous Marine Decision Support System</span>
        </div>
      </div>
    </footer>
  );
};
