'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '@/components/Navbar';
import { Sidebar, NavSection, ChatSessionMeta } from '@/components/Sidebar';
import { QueryPanel, ChatMessage } from '@/components/QueryPanel';
import { AnalysisWorkspace } from '@/components/analysis/AnalysisWorkspace';
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
  fetchConversationSessions,
  fetchSessionHistory,
  clearSessionHistory,
  SourceHealthSummary
} from '@/lib/apiClient';

export default function DashboardPage() {
  const [activeSection, setActiveSection] = useState<NavSection>('ask-orca');
  const [viewMode, setViewMode] = useState<'ask' | 'analysis'>('ask');
  const [activeFilter, setActiveFilter] = useState<'all' | 'safe' | 'hazards' | 'restricted'>('all');
  const [zones, setZones] = useState<MarineZone[]>(DEMO_ZONES);
  const [selectedZone, setSelectedZone] = useState<MarineZone | null>(DEMO_ZONES[0]);
  const [evidenceSources, setEvidenceSources] = useState<EvidenceSource[]>(DEMO_EVIDENCE_SOURCES);
  const [freshnessItems, setFreshnessItems] = useState<DataFreshnessItem[]>(DEMO_FRESHNESS_ITEMS);
  const [sourceHealth, setSourceHealth] = useState<SourceHealthSummary | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<ORCAAnalysisResult | null>(null);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  
  // Conversational State & Multi-turn Session Management
  const [sessionId, setSessionId] = useState<string>(() => `orca_session_${Date.now()}`);
  const [sessions, setSessions] = useState<ChatSessionMeta[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
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

  // Decision, Observability & Simulation Modals
  const [isWhatIfModalOpen, setIsWhatIfModalOpen] = useState<boolean>(false);
  const [isConfidenceModalOpen, setIsConfidenceModalOpen] = useState<boolean>(false);
  const [isResearchModalOpen, setIsResearchModalOpen] = useState<boolean>(false);

  // Refresh Session List from Backend
  const refreshSessions = useCallback(async () => {
    try {
      const sessList = await fetchConversationSessions();
      if (sessList && sessList.length > 0) {
        setSessions(sessList);
      }
    } catch (e) {
      console.warn('Could not load session list:', e);
    }
  }, []);

  // Load initial authoritative backend data and alerts
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
    refreshSessions();
  }, [refreshSessions]);

  // Start a fresh new chat session
  const handleNewChat = () => {
    const newSid = `orca_session_${Date.now()}`;
    setSessionId(newSid);
    setMessages([]);
    setCurrentQuery('');
    setAnalysisResult(null);
    setSelectedZone(zones.length > 0 ? zones[0] : null);
    setActiveFilter('all');
    setViewMode('ask');
    setActiveSection('ask-orca');
  };

  // Restore an existing session from history
  const handleSelectSession = async (targetSessionId: string) => {
    try {
      setSessionId(targetSessionId);
      const hist = await fetchSessionHistory(targetSessionId);
      if (hist && hist.messages && hist.messages.length > 0) {
        const formatted: ChatMessage[] = hist.messages.map((m: any) => ({
          id: m.id || `msg_${Math.random()}`,
          role: m.role,
          content: m.content || m.summary || '',
          timestamp: m.timestamp,
          decision: m.decision,
          focused_zone_id: m.focused_zone_id,
          zonesToAvoid: m.zonesToAvoid,
          potentialZones: m.potentialZones,
          all_zones: m.all_zones,
          confidenceScore: m.confidenceScore,
          confidenceLevel: m.confidenceLevel,
          language: m.language,
          follow_up_suggestions: m.follow_up_suggestions
        }));
        setMessages(formatted);

        // Restore latest assistant analysis state
        const lastAssistant = [...formatted].reverse().find(m => m.role === 'assistant');
        if (lastAssistant && lastAssistant.all_zones && lastAssistant.all_zones.length > 0) {
          setZones(lastAssistant.all_zones);
          if (lastAssistant.focused_zone_id) {
            const found = lastAssistant.all_zones.find(z => z.id === lastAssistant.focused_zone_id);
            if (found) setSelectedZone(found);
          }
        }
      }
      setViewMode('ask');
      setActiveSection('ask-orca');
    } catch (e) {
      console.warn('Failed restoring session:', e);
    }
  };

  // Primary Conversational Analysis Handler
  const handleAnalyze = async (query: string, targetLang?: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;

    setCurrentQuery(trimmed);
    setIsAnalyzing(true);
    const activeLang = targetLang || language;

    // Immediately push User message into thread
    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      language: activeLang
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const result = await analyzeMarineQuery(trimmed, sessionId, activeLang, undefined, isDemoMode);
      setAnalysisResult(result);

      // Extract dynamic zones returned for this specific query
      if (result.all_zones && result.all_zones.length > 0) {
        setZones(result.all_zones);
      }

      // Auto-focus selected zone
      if (result.focusedZoneId) {
        const currentZoneList = result.all_zones || zones;
        const found = currentZoneList.find((z) => z.id === result.focusedZoneId);
        if (found) setSelectedZone(found);
      } else if (result.potentialZones && result.potentialZones.length > 0) {
        const firstCandidate = result.potentialZones[0] as any;
        const candidateId = firstCandidate.id || firstCandidate.zone_id;
        const currentZoneList = result.all_zones || zones;
        const found = currentZoneList.find((z) => z.id === candidateId);
        if (found) setSelectedZone(found);
      }

      if (result.filterMode) {
        setActiveFilter(result.filterMode as any);
      }

      // Push ORCA assistant message into thread
      const assistantMsg: ChatMessage = {
        id: `msg_a_${Date.now()}`,
        role: 'assistant',
        content: result.summary,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        decision: result.decision,
        focused_zone_id: result.focusedZoneId,
        zonesToAvoid: result.zonesToAvoid,
        potentialZones: result.potentialZones,
        all_zones: result.all_zones,
        confidenceScore: result.confidenceScore,
        confidenceLevel: result.confidenceLevel,
        language: activeLang,
        response_type: (result as any).response_type,
        data: (result as any).data,
        results: (result as any).results,
        why_reasons: (result as any).why_reasons,
        sources: (result as any).sources,
        map: (result as any).map,
        follow_up_suggestions: (result as any).follow_up_suggestions
      };
      setMessages(prev => [...prev, assistantMsg]);
      refreshSessions();
    } catch (err) {
      console.error('Error during query analysis:', err);
      const fallbackResult = runDemoAnalysis(trimmed);
      setAnalysisResult(fallbackResult);
      const fallbackMsg: ChatMessage = {
        id: `msg_a_${Date.now()}`,
        role: 'assistant',
        content: fallbackResult.summary,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        decision: fallbackResult.decision,
        zonesToAvoid: fallbackResult.zonesToAvoid,
        potentialZones: fallbackResult.potentialZones,
        all_zones: zones,
        confidenceScore: fallbackResult.confidenceScore,
        language: activeLang,
        response_type: (fallbackResult as any).response_type,
        data: (fallbackResult as any).data,
        results: (fallbackResult as any).results,
        why_reasons: (fallbackResult as any).why_reasons,
        sources: (fallbackResult as any).sources
      };
      setMessages(prev => [...prev, fallbackMsg]);
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
        : 'Which fishing zones should be avoided tomorrow morning?';
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
      const q = currentQuery || 'Which fishing zones should be avoided tomorrow morning?';
      const report = await generateMarineBrief(q);
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
      setViewMode('ask');
      setActiveSection('ask-orca');
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
    if (section === 'ask-orca') {
      setViewMode('ask');
    } else if (section === 'analysis') {
      setViewMode('analysis');
    } else if (section === 'safety') {
      setIsAlertsModalOpen(true);
    } else if (section === 'research') {
      setIsResearchModalOpen(true);
    } else if (section === 'brief') {
      handleGenerateBrief();
    } else if (section === 'settings') {
      setIsStatusModalOpen(true);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0B1120] text-slate-100 font-sans selection:bg-teal-900 selection:text-teal-200">
      {/* Top Navigation & Command Center Header */}
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

      {/* Main Workstation Layout Container */}
      <div className="flex-1 flex flex-col lg:flex-row w-full mx-auto">
        {/* Left Navigation Rail & Conversation History */}
        <Sidebar
          activeSection={activeSection}
          onSelectSection={handleNavSectionSelect}
          onFilterChange={(filter) => setActiveFilter(filter)}
          activeFilter={activeFilter}
          sourceHealth={sourceHealth}
          language={language}
          unreadAlertCount={unreadAlertCount}
          onOpenAlerts={() => setIsAlertsModalOpen(true)}
          onOpenResearch={() => setIsResearchModalOpen(true)}
          onOpenMarineBrief={handleGenerateBrief}
          onOpenSystemStatus={() => setIsStatusModalOpen(true)}
          onNewChat={handleNewChat}
          sessions={sessions}
          activeSessionId={sessionId}
          onSelectSession={handleSelectSession}
        />

        {/* Primary Workspace View Switcher */}
        <main className="flex-1 p-3 sm:p-4 lg:p-6 min-w-0 max-w-[1680px] mx-auto w-full">
          {/* VIEW 1: ASK ORCA (Primary Multi-Turn Conversational Interface with Dynamic Integrated Map) */}
          {viewMode === 'ask' && (
            <div className="animate-in fade-in duration-200">
              <QueryPanel
                messages={messages}
                onAnalyze={(q) => handleAnalyze(q)}
                isAnalyzing={isAnalyzing}
                currentQuery={currentQuery}
                language={language}
                activeZones={zones}
                selectedZone={selectedZone}
                onSelectZone={handleSelectZone}
                onOpenReasoningTab={() => {
                  setViewMode('analysis');
                  setActiveSection('analysis');
                }}
                onOpenEvidenceTab={() => setIsEvidenceDrawerOpen(true)}
                onOpenWhatIfModal={() => setIsWhatIfModalOpen(true)}
                onOpenConfidenceModal={() => setIsConfidenceModalOpen(true)}
                onNewChat={handleNewChat}
              />
            </div>
          )}

          {/* VIEW 2: TECHNICAL ANALYSIS TABS (Deep Inspection: MAP | REASONING | EVIDENCE | DATA) */}
          {viewMode === 'analysis' && (
            <div className="animate-in fade-in duration-200">
              <AnalysisWorkspace
                analysis={analysisResult || runDemoAnalysis(currentQuery || 'Avoidance analysis')}
                zones={zones}
                selectedZone={selectedZone}
                onSelectZone={handleSelectZone}
                activeFilter={activeFilter}
                evidenceSources={evidenceSources}
                onInspectEvidence={handleInspectEvidence}
                onAskFollowUp={(q) => handleAnalyze(q)}
                onOpenWhatIfModal={() => setIsWhatIfModalOpen(true)}
                onOpenConfidenceModal={() => setIsConfidenceModalOpen(true)}
                onOpenMarineBrief={handleGenerateBrief}
                onBackToAsk={() => {
                  setViewMode('ask');
                  setActiveSection('ask-orca');
                }}
                language={language}
              />
            </div>
          )}
        </main>
      </div>

      {/* Footer Bar */}
      <FooterBar />

      {/* Auxiliary Modals & Drawers */}
      <ArchitectureModal
        isOpen={isArchModalOpen}
        onClose={() => setIsArchModalOpen(false)}
      />

      <SystemStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
      />

      <EvidenceDrawer
        isOpen={isEvidenceDrawerOpen}
        onClose={() => setIsEvidenceDrawerOpen(false)}
        evidence={activeEvidenceItem}
      />

      <SafetyAlertsModal
        isOpen={isAlertsModalOpen}
        onClose={() => setIsAlertsModalOpen(false)}
        alerts={activeAlerts}
        onSelectZone={handleAlertZoneSelect}
        onAlertAcknowledged={handleAlertAcknowledged}
      />

      <MarineBriefModal
        isOpen={isBriefModalOpen}
        onClose={() => setIsBriefModalOpen(false)}
        report={marineBrief}
        isLoading={isGeneratingBrief}
      />

      <WhatIfScenarioModal
        isOpen={isWhatIfModalOpen}
        onClose={() => setIsWhatIfModalOpen(false)}
      />

      <ConfidenceBreakdownModal
        isOpen={isConfidenceModalOpen}
        onClose={() => setIsConfidenceModalOpen(false)}
        zoneId={selectedZone?.id || 'zone-c'}
      />

      <ResearchEvaluationModal
        isOpen={isResearchModalOpen}
        onClose={() => setIsResearchModalOpen(false)}
      />
    </div>
  );
}
