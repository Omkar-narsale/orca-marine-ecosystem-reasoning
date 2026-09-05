'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Navbar } from '@/components/Navbar';
import { Sidebar, NavSection } from '@/components/Sidebar';
import { QueryPanel } from '@/components/QueryPanel';
import { ZoneDetails } from '@/components/ZoneDetails';
import { AnalysisPanel } from '@/components/AnalysisPanel';
import { EvidencePanel } from '@/components/EvidencePanel';
import { ConfidenceScore } from '@/components/ConfidenceScore';
import { DataFreshness } from '@/components/DataFreshness';
import { FooterBar } from '@/components/FooterBar';
import { ArchitectureModal } from '@/components/ArchitectureModal';
import { SystemStatusModal } from '@/components/SystemStatusModal';
import EvidenceDrawer from '@/components/EvidenceDrawer';
import MarineBriefModal from '@/components/MarineBriefModal';
import SafetyAlertsModal from '@/components/SafetyAlertsModal';
import WhatIfScenarioModal from '@/components/WhatIfScenarioModal';
import ConfidenceBreakdownModal from '@/components/ConfidenceBreakdownModal';
import ResearchEvaluationModal from '@/components/ResearchEvaluationModal';
import {
  MarineZone,
  ORCAAnalysisResult,
  EvidenceSource,
  DataFreshnessItem,
  MarineSafetyAlert,
  MarineBriefReport
} from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';
import { DEMO_EVIDENCE_SOURCES, DEMO_FRESHNESS_ITEMS } from '@/data/demoEvidence';
import { runDemoAnalysis } from '@/lib/demoAnalysis';
import {
  fetchMarineZones,
  fetchEvidenceSources,
  fetchDataFreshness,
  fetchSourcesHealth,
  fetchActiveAlerts,
  analyzeMarineQuery,
  generateMarineBrief,
  SourceHealthSummary
} from '@/lib/apiClient';
import { Loader2 } from 'lucide-react';

const MarineMap = dynamic(
  () => import('@/components/MarineMap').then((mod) => mod.MarineMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[520px] lg:h-[580px] rounded-2xl bg-slate-100 border border-slate-200/80 flex flex-col items-center justify-center p-6 text-slate-400">
        <Loader2 className="w-6 h-6 animate-spin text-slate-600 mb-2" />
        <span className="text-xs font-semibold text-slate-600">
          Loading Marine Map...
        </span>
      </div>
    ),
  }
);

export default function DashboardPage() {
  const [activeSection, setActiveSection] = useState<NavSection>('ask-orca');
  const [activeFilter, setActiveFilter] = useState<'all' | 'safe' | 'hazards' | 'restricted'>('all');
  const [zones, setZones] = useState<MarineZone[]>(DEMO_ZONES);
  const [selectedZone, setSelectedZone] = useState<MarineZone | null>(DEMO_ZONES[0]);
  const [evidenceSources, setEvidenceSources] = useState<EvidenceSource[]>(DEMO_EVIDENCE_SOURCES);
  const [freshnessItems, setFreshnessItems] = useState<DataFreshnessItem[]>(DEMO_FRESHNESS_ITEMS);
  const [sourceHealth, setSourceHealth] = useState<SourceHealthSummary | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<ORCAAnalysisResult | null>(null);
  const [currentQuery, setCurrentQuery] = useState<string>('Which fishing zones should be avoided tomorrow?');
  const [sessionId] = useState<string>(() => `orca_session_${Date.now()}`);
  const [language, setLanguage] = useState<string>('en');
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  // Modal & Drawer State
  const [isArchModalOpen, setIsArchModalOpen] = useState<boolean>(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState<boolean>(false);
  const [isEvidenceDrawerOpen, setIsEvidenceDrawerOpen] = useState<boolean>(false);
  const [activeEvidenceItem, setActiveEvidenceItem] = useState<any>(null);
  const [isAlertsModalOpen, setIsAlertsModalOpen] = useState<boolean>(false);
  const [activeAlerts, setActiveAlerts] = useState<MarineSafetyAlert[]>([]);
  const [unreadAlertCount, setUnreadAlertCount] = useState<number>(0);
  const [isBriefModalOpen, setIsBriefModalOpen] = useState<boolean>(false);
  const [marineBrief, setMarineBrief] = useState<MarineBriefReport | null>(null);
  const [isGeneratingBrief, setIsGeneratingBrief] = useState<boolean>(false);

  // Phase 5 & 6 Decision, Observability & Simulation Modals
  const [isWhatIfModalOpen, setIsWhatIfModalOpen] = useState<boolean>(false);
  const [isConfidenceModalOpen, setIsConfidenceModalOpen] = useState<boolean>(false);
  const [isResearchModalOpen, setIsResearchModalOpen] = useState<boolean>(false);

  // Load initial data and alerts
  useEffect(() => {
    async function loadBackendData() {
      try {
        const [loadedZones, loadedSources, loadedFreshness, loadedHealth, loadedAlerts] = await Promise.all([
          fetchMarineZones(),
          fetchEvidenceSources(),
          fetchDataFreshness(),
          fetchSourcesHealth(),
          fetchActiveAlerts()
        ]);

        if (loadedZones && loadedZones.length > 0) {
          setZones(loadedZones);
          setSelectedZone(loadedZones[0]);
        }
        if (loadedSources && loadedSources.length > 0) {
          setEvidenceSources(loadedSources);
        }
        if (loadedFreshness && loadedFreshness.length > 0) {
          setFreshnessItems(loadedFreshness);
        }
        if (loadedHealth) {
          setSourceHealth(loadedHealth);
        }
        if (loadedAlerts) {
          setActiveAlerts(loadedAlerts.alerts || []);
          setUnreadAlertCount(loadedAlerts.unread_count || 0);
        }
      } catch (e) {
        setIsDemoMode(true);
      }
    }

    loadBackendData();
    const defaultResult = runDemoAnalysis(currentQuery);
    setAnalysisResult(defaultResult);
  }, []);

  const handleAnalyze = async (query: string, targetLang?: string) => {
    setCurrentQuery(query);
    setIsAnalyzing(true);
    const activeLang = targetLang || language;

    try {
      const result = await analyzeMarineQuery(query, sessionId, activeLang, undefined, isDemoMode);
      setAnalysisResult(result);

      if (result.all_zones && result.all_zones.length > 0) {
        setZones(result.all_zones);
      }

      if (result.focusedZoneId) {
        const currentZoneList = result.all_zones || zones;
        const found = currentZoneList.find((z) => z.id === result.focusedZoneId);
        if (found) setSelectedZone(found);
      }
      if (result.filterMode) {
        setActiveFilter(result.filterMode as any);
      }
    } catch (err) {
      console.error('Error during query analysis:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    const langKey = (newLang as 'en' | 'hi' | 'mr') || 'en';
    const localizedDefault =
      langKey === 'mr'
        ? 'उद्या सकाळी कोणते मासेमारी क्षेत्र टाळावे?'
        : langKey === 'hi'
        ? 'कल सुबह कौन से मछली पकड़ने के क्षेत्र से बचना चाहिए?'
        : 'Which fishing zones should be avoided tomorrow?';
    setCurrentQuery(localizedDefault);
    handleAnalyze(localizedDefault, newLang);
  };

  const handleSelectZone = (zone: MarineZone) => {
    setSelectedZone(zone);
  };

  const handleInspectEvidence = (evidence: any) => {
    setActiveEvidenceItem(evidence);
    setIsEvidenceDrawerOpen(true);
  };

  const handleGenerateBrief = async () => {
    setIsGeneratingBrief(true);
    setIsBriefModalOpen(true);
    try {
      const report = await generateMarineBrief(currentQuery);
      setMarineBrief(report);
    } catch (err) {
      console.error('Failed generating marine brief:', err);
    } finally {
      setIsGeneratingBrief(false);
    }
  };

  const handleAlertZoneSelect = (zoneId: string) => {
    const found = zones.find((z) => z.id === zoneId);
    if (found) {
      setSelectedZone(found);
      setIsAlertsModalOpen(false);
    }
  };

  const handleAlertAcknowledged = (alertId: string) => {
    setActiveAlerts((prev) =>
      prev.map((a) => (a.alert_id === alertId ? { ...a, acknowledged: true } : a))
    );
    setUnreadAlertCount((prev) => Math.max(0, prev - 1));
  };

  const handleNavSectionSelect = (section: NavSection) => {
    setActiveSection(section);
    if (section === 'safety') {
      setActiveFilter('hazards');
      const zoneA = zones.find((z) => z.id === 'zone-a');
      if (zoneA) setSelectedZone(zoneA);
    } else if (section === 'zones') {
      setActiveFilter('all');
    } else if (section === 'evidence') {
      const el = document.getElementById('evidence-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F9FAFB] text-slate-900 font-sans selection:bg-teal-100 selection:text-teal-900">
      {/* Top Navbar */}
      <Navbar
        onOpenArchitectureModal={() => setIsArchModalOpen(true)}
        language={language}
        onLanguageChange={handleLanguageChange}
        unreadAlertCount={unreadAlertCount}
        onOpenAlerts={() => setIsAlertsModalOpen(true)}
        onOpenMarineBrief={handleGenerateBrief}
        onOpenWhatIf={() => setIsWhatIfModalOpen(true)}
        onOpenResearch={() => setIsResearchModalOpen(true)}
        onOpenSystemStatus={() => setIsStatusModalOpen(true)}
        isDemoMode={isDemoMode}
      />

      {/* Main Layout Container */}
      <div className="flex-1 flex flex-col lg:flex-row w-full max-w-[1520px] mx-auto">
        {/* Left Sidebar */}
        <Sidebar
          activeSection={activeSection}
          onSelectSection={handleNavSectionSelect}
          onFilterChange={(filter) => setActiveFilter(filter)}
          activeFilter={activeFilter}
          sourceHealth={sourceHealth}
          language={language}
        />

        {/* Main Workspace (Map-First, High Information Density without Clutter) */}
        <main className="flex-1 p-6 lg:p-8 space-y-8 min-w-0">
          {/* Query Header */}
          <section id="query-section">
            <QueryPanel
              onAnalyze={(q) => handleAnalyze(q)}
              isAnalyzing={isAnalyzing}
              currentQuery={currentQuery}
              language={language}
            />
          </section>

          {/* Map-First Workspace: 68% Map + 32% Zone Inspector */}
          <section id="map-section" className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-8">
              <MarineMap
                zones={zones}
                selectedZone={selectedZone}
                onSelectZone={handleSelectZone}
                filterMode={activeFilter}
                language={language}
              />
            </div>

            <div className="lg:col-span-4">
              <ZoneDetails
                zone={selectedZone}
                onHighlightOnMap={(zone) => setSelectedZone(zone)}
                onViewSource={() => {
                  const el = document.getElementById('evidence-section');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }}
                language={language}
              />
            </div>
          </section>

          {/* Decision & Analysis Workspace */}
          {analysisResult && (
            <section id="analysis-section">
              <AnalysisPanel
                analysis={analysisResult}
                onSelectZone={handleSelectZone}
                selectedZoneId={selectedZone?.id}
                onInspectEvidence={handleInspectEvidence}
                onAskFollowUp={(q) => handleAnalyze(q)}
                onOpenConfidenceModal={() => setIsConfidenceModalOpen(true)}
                onOpenWhatIfModal={() => setIsWhatIfModalOpen(true)}
                language={language}
              />
            </section>
          )}

          {/* Evidence, Freshness & Confidence Rows */}
          <section id="evidence-section" className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7">
              <EvidencePanel
                sources={evidenceSources}
                onInspectEvidence={handleInspectEvidence}
              />
            </div>

            <div className="lg:col-span-5 space-y-6">
              {analysisResult && (
                <ConfidenceScore
                  level={analysisResult.confidenceLevel}
                  score={analysisResult.confidenceScore}
                  explanation={analysisResult.confidenceExplanation}
                  onViewMethodology={() => setIsConfidenceModalOpen(true)}
                />
              )}
              <DataFreshness items={freshnessItems} />
            </div>
          </section>
        </main>
      </div>

      {/* Footer */}
      <FooterBar />

      {/* SIH Specification Modal */}
      <ArchitectureModal
        isOpen={isArchModalOpen}
        onClose={() => setIsArchModalOpen(false)}
      />

      {/* System Status Observability Modal (Phase 6) */}
      <SystemStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
      />

      {/* Evidence Graph Node Drawer */}
      <EvidenceDrawer
        isOpen={isEvidenceDrawerOpen}
        onClose={() => setIsEvidenceDrawerOpen(false)}
        evidence={activeEvidenceItem}
      />

      {/* Safety Alerts Modal */}
      <SafetyAlertsModal
        isOpen={isAlertsModalOpen}
        onClose={() => setIsAlertsModalOpen(false)}
        alerts={activeAlerts}
        onSelectZone={handleAlertZoneSelect}
        onAlertAcknowledged={handleAlertAcknowledged}
      />

      {/* Operational Marine Brief Modal */}
      <MarineBriefModal
        isOpen={isBriefModalOpen}
        onClose={() => setIsBriefModalOpen(false)}
        report={marineBrief}
        isLoading={isGeneratingBrief}
      />

      {/* What-If Scenario Modal */}
      <WhatIfScenarioModal
        isOpen={isWhatIfModalOpen}
        onClose={() => setIsWhatIfModalOpen(false)}
      />

      {/* Decomposed Confidence & Uncertainty Breakdown Modal */}
      <ConfidenceBreakdownModal
        isOpen={isConfidenceModalOpen}
        onClose={() => setIsConfidenceModalOpen(false)}
        zoneId={selectedZone?.id || 'zone-c'}
      />

      {/* SIH Research & Benchmark Evaluation Modal */}
      <ResearchEvaluationModal
        isOpen={isResearchModalOpen}
        onClose={() => setIsResearchModalOpen(false)}
      />
    </div>
  );
}
