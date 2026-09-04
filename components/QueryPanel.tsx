'use client';

import React, { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { I18N_STRINGS, LanguageCode } from '@/lib/i18n';

interface QueryPanelProps {
  onAnalyze: (query: string) => void;
  isAnalyzing: boolean;
  currentQuery: string;
  language?: string;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({
  onAnalyze,
  isAnalyzing,
  currentQuery,
  language = 'en',
}) => {
  const langKey = (language as LanguageCode) || 'en';
  const t = I18N_STRINGS[langKey] || I18N_STRINGS.en;

  const [inputValue, setInputValue] = useState<string>(currentQuery || t.suggestedQueries[0].query);

  useEffect(() => {
    if (currentQuery) {
      setInputValue(currentQuery);
    }
  }, [currentQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isAnalyzing) return;
    onAnalyze(inputValue);
  };

  const handleChipClick = (queryText: string) => {
    setInputValue(queryText);
    onAnalyze(queryText);
  };

  return (
    <div className="space-y-4">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-950">
          {t.askOrca}
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          {t.askOrcaSubtitle}
        </p>
      </div>

      {/* Query Search Bar */}
      <form onSubmit={handleSubmit} className="relative max-w-4xl">
        <div className="relative flex items-center">
          <div className="absolute left-4 text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t.inputPlaceholder}
            disabled={isAnalyzing}
            className="w-full pl-11 pr-32 py-3 bg-white text-slate-900 placeholder:text-slate-400 text-sm font-normal rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-marine-900 focus:border-marine-900 transition-all shadow-sm"
          />
          <button
            type="submit"
            disabled={isAnalyzing || !inputValue.trim()}
            className="absolute right-1.5 px-4 py-2 bg-marine-950 hover:bg-marine-900 text-teal-400 rounded-lg text-xs font-semibold tracking-wide disabled:opacity-50 transition-all flex items-center gap-1.5"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-teal-400" />
                <span>{t.analyzingBtn}</span>
              </>
            ) : (
              <span>{t.analyzeBtn}</span>
            )}
          </button>
        </div>
      </form>

      {/* Suggested Queries in Selected Language */}
      <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span className="text-slate-400 text-[11px] font-medium mr-1">
          {t.suggestedLabel}
        </span>
        {t.suggestedQueries.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleChipClick(item.query)}
            disabled={isAnalyzing}
            className="px-3 py-1 bg-white hover:bg-slate-100/80 text-slate-700 text-xs rounded-full border border-slate-200 transition-colors shadow-2xs font-medium"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
};
