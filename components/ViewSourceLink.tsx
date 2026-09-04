'use client';

import React from 'react';
import { ArrowUpRight } from 'lucide-react';

interface ViewSourceLinkProps {
  sourceUrl?: string;
  label?: string;
  className?: string;
}

export const ViewSourceLink: React.FC<ViewSourceLinkProps> = ({
  sourceUrl,
  label = 'View Source',
  className = '',
}) => {
  if (!sourceUrl || !sourceUrl.trim()) {
    return (
      <span className="text-[11px] text-slate-400 italic">
        Source link unavailable
      </span>
    );
  }

  return (
    <a
      href={sourceUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`text-teal-700 hover:text-teal-900 font-medium inline-flex items-center gap-0.5 hover:underline cursor-pointer transition-colors text-xs ${className}`}
      title={`Open official source in new tab (${sourceUrl})`}
    >
      <span>{label}</span>
      <ArrowUpRight className="w-3 h-3 shrink-0" />
    </a>
  );
};
