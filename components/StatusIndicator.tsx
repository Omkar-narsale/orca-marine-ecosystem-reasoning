import React from 'react';

interface StatusIndicatorProps {
  label: string;
  status?: 'online' | 'active' | 'synced' | 'caution' | 'offline';
  subtext?: string;
  size?: 'sm' | 'md';
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  label,
  status = 'online',
  subtext,
  size = 'md',
}) => {
  const getColors = () => {
    switch (status) {
      case 'online':
      case 'active':
      case 'synced':
        return {
          dot: 'bg-emerald-500',
          text: 'text-slate-700 font-medium',
        };
      case 'caution':
        return {
          dot: 'bg-amber-500',
          text: 'text-slate-700 font-medium',
        };
      case 'offline':
      default:
        return {
          dot: 'bg-rose-500',
          text: 'text-slate-700 font-medium',
        };
    }
  };

  const colors = getColors();

  return (
    <div className="inline-flex items-center gap-2 text-xs">
      <span className="relative flex h-2 w-2">
        <span className={`relative inline-flex h-2 w-2 rounded-full ${colors.dot}`} />
      </span>
      <span className={colors.text}>{label}</span>
      {subtext && (
        <span className="text-[11px] text-slate-400 font-mono">({subtext})</span>
      )}
    </div>
  );
};
