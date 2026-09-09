'use client';

import React from 'react';
import { ExternalLink } from 'lucide-react';

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
      <span className="text-[10px] text-slate-500 italic font-mono">
        Source unavailable
      </span>
    );
  }

  return (
    <a
      href={sourceUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`text-teal-400 hover:text-teal-300 font-mono font-bold inline-flex items-center gap-1 cursor-pointer transition-colors text-xs ${className}`}
      title={`Open official source in new tab (${sourceUrl})`}
    >
      <span>{label}</span>
      <ExternalLink className="w-2.5 h-2.5 shrink-0" />
    </a>
  );
};
