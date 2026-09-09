'use client';

import React, { useState } from 'react';
import { MarineZone, EvidenceSource } from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';
import { Table, ExternalLink, Filter, Download } from 'lucide-react';

interface DataTabProps {
  zones?: MarineZone[];
}

export const DataTab: React.FC<DataTabProps> = ({ zones = DEMO_ZONES }) => {
  const [filterType, setFilterType] = useState<string>('all');
  const activeZones = zones && zones.length > 0 ? zones : DEMO_ZONES;

  // Flatten marine parameter records into scientific tabular rows
  const telemetryRows = [
    {
      id: 'row-1',
      parameter: 'Significant Wave Height (Hs)',
      value: '4.1',
      unit: 'm',
      sector: 'ZONE A (North Offshore)',
      latLon: '19.30°N, 72.53°E',
      observationTime: '08 Sep 18:00 IST',
      validTime: 'Tomorrow 06:00 IST',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'FORECAST',
      quality: 'Verified Numerical (WW3)',
      source: 'INCOIS OSF',
      sourceUrl: 'https://incois.gov.in/oceanservices/osfforecast.jsp',
    },
    {
      id: 'row-2',
      parameter: 'Coastal Wind Velocity',
      value: '31.0',
      unit: 'kt',
      sector: 'ZONE A (North Offshore)',
      latLon: '19.30°N, 72.53°E',
      observationTime: '08 Sep 21:00 IST',
      validTime: 'Tomorrow 06:00 IST',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'FORECAST',
      quality: 'Official Synoptic',
      source: 'IMD Marine Division',
      sourceUrl: 'https://api.imd.gov.in/public/index.php',
    },
    {
      id: 'row-3',
      parameter: 'Marine Squall Line Alert',
      value: 'ACTIVE',
      unit: 'Status',
      sector: 'ZONE A (North Offshore)',
      latLon: '19.30°N, 72.53°E',
      observationTime: '08 Sep 23:00 IST',
      validTime: 'Next 24 Hours',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'WARNING',
      quality: 'Statutory Bulletin',
      source: 'IMD Coastal Warning',
      sourceUrl: 'https://api.imd.gov.in/public/index.php',
    },
    {
      id: 'row-4',
      parameter: 'Maritime Fairway & Anchorage Corridor',
      value: 'RESTRICTED',
      unit: 'Cadastre',
      sector: 'ZONE B (Mumbai Harbor)',
      latLon: '18.97°N, 72.64°E',
      observationTime: 'Permanent Baseline',
      validTime: 'Continuous (2026.1)',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'STATIC',
      quality: 'Naval Cadastre Verified',
      source: 'GIS Cadastre / NHO',
      sourceUrl: 'https://hydro-india.nic.in',
    },
    {
      id: 'row-5',
      parameter: 'Significant Wave Height (Hs)',
      value: '1.0',
      unit: 'm',
      sector: 'ZONE C (South Shelf)',
      latLon: '18.58°N, 72.70°E',
      observationTime: '08 Sep 18:00 IST',
      validTime: 'Tomorrow 06:00 IST',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'FORECAST',
      quality: 'Verified Numerical (WW3)',
      source: 'INCOIS OSF',
      sourceUrl: 'https://incois.gov.in/oceanservices/osfforecast.jsp',
    },
    {
      id: 'row-6',
      parameter: 'Sea Surface Temperature (SST)',
      value: '28.2',
      unit: '°C',
      sector: 'ZONE C (South Shelf)',
      latLon: '18.58°N, 72.70°E',
      observationTime: '08 Sep 14:30 IST',
      validTime: 'Observation Window',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'OBSERVATION',
      quality: 'Satellite Thermal Swath',
      source: 'MOSDAC / ISRO',
      sourceUrl: 'https://www.mosdac.gov.in',
    },
    {
      id: 'row-7',
      parameter: 'Chlorophyll-a Concentration',
      value: '3.4',
      unit: 'mg/m³',
      sector: 'ZONE C (South Shelf)',
      latLon: '18.58°N, 72.70°E',
      observationTime: '08 Sep 11:30 IST',
      validTime: 'Observation Window',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'OBSERVATION',
      quality: 'OCM-3 Spectral Radiometer',
      source: 'MOSDAC Ocean Color',
      sourceUrl: 'https://www.mosdac.gov.in',
    },
    {
      id: 'row-8',
      parameter: 'Potential Fishing Zone (PFZ) Vector',
      value: 'ACTIVE GRADIENT',
      unit: 'Front',
      sector: 'ZONE C (South Shelf)',
      latLon: '18.58°N, 72.70°E',
      observationTime: '08 Sep 16:00 IST',
      validTime: 'Tomorrow 14:00 IST',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'ADVISORY',
      quality: 'Composite Advisory',
      source: 'INCOIS PFZ',
      sourceUrl: 'https://incois.gov.in/MarineFisheries/PfzAdvisory',
    },
    {
      id: 'row-9',
      parameter: 'Significant Wave Height (Hs)',
      value: '2.1',
      unit: 'm',
      sector: 'ZONE D (Mid-Shelf)',
      latLon: '18.84°N, 72.31°E',
      observationTime: '08 Sep 18:00 IST',
      validTime: 'Tomorrow 06:00 IST',
      retrievedAt: '09 Sep 10:35 IST',
      dataType: 'FORECAST',
      quality: 'Verified Numerical (WW3)',
      source: 'INCOIS OSF',
      sourceUrl: 'https://incois.gov.in/oceanservices/osfforecast.jsp',
    },
  ];

  const filteredRows = telemetryRows.filter((r) => {
    if (filterType === 'all') return true;
    return r.dataType.toLowerCase() === filterType.toLowerCase();
  });

  const exportCSV = () => {
    const headers = ['Parameter', 'Value', 'Unit', 'Sector', 'LatLon', 'ObservationTime', 'ValidTime', 'RetrievedAt', 'DataType', 'Quality', 'Source'];
    const rows = filteredRows.map(r => [r.parameter, r.value, r.unit, `"${r.sector}"`, `"${r.latLon}"`, `"${r.observationTime}"`, `"${r.validTime}"`, `"${r.retrievedAt}"`, r.dataType, `"${r.quality}"`, `"${r.source}"`]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `orca_marine_telemetry_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4 font-mono text-xs text-slate-200">
      {/* 1. Header & Controls */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 p-4 shadow-md flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-teal-400" />
          <span className="font-bold text-white text-xs uppercase tracking-wider">
            Normalized Scientific Marine Telemetry Table
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Data Type Filter */}
          <div className="flex items-center gap-1 bg-slate-900 px-2 py-1 rounded border border-slate-800 text-[11px]">
            <Filter className="w-3 h-3 text-slate-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-transparent text-slate-300 font-bold focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-slate-900">ALL TYPES ({telemetryRows.length})</option>
              <option value="forecast" className="bg-slate-900">FORECAST</option>
              <option value="observation" className="bg-slate-900">OBSERVATION</option>
              <option value="advisory" className="bg-slate-900">ADVISORY</option>
              <option value="warning" className="bg-slate-900">WARNING</option>
              <option value="static" className="bg-slate-900">STATIC</option>
            </select>
          </div>

          <button
            onClick={exportCSV}
            className="flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 text-[11px] font-bold transition-colors"
          >
            <Download className="w-3 h-3 text-teal-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* 2. Scientific Data Table */}
      <div className="bg-[#0F172A] rounded-xl border border-slate-800 shadow-md overflow-x-auto">
        <table className="w-full text-left border-collapse text-[11px]">
          <thead>
            <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400 uppercase text-[9px] tracking-wider">
              <th className="py-2.5 px-3">Parameter</th>
              <th className="py-2.5 px-3">Value</th>
              <th className="py-2.5 px-3">Sector</th>
              <th className="py-2.5 px-3">Coordinates</th>
              <th className="py-2.5 px-3">Data Nature</th>
              <th className="py-2.5 px-3">Valid Window</th>
              <th className="py-2.5 px-3">Retrieved</th>
              <th className="py-2.5 px-3">Quality & Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredRows.map((row) => {
              const isWarning = row.dataType === 'WARNING';
              const isForecast = row.dataType === 'FORECAST';
              const isObservation = row.dataType === 'OBSERVATION';
              const isAdvisory = row.dataType === 'ADVISORY';

              return (
                <tr key={row.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-white whitespace-nowrap">
                    {row.parameter}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-teal-300 whitespace-nowrap">
                    {row.value} <span className="text-[9px] text-slate-400 font-normal">{row.unit}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 whitespace-nowrap">
                    {row.sector}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap text-[10px]">
                    {row.latLon}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span
                      className={`px-1.5 py-0.2 rounded text-[8px] font-bold border ${
                        isWarning
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                          : isForecast
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                          : isObservation
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : isAdvisory
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                          : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                      }`}
                    >
                      {row.dataType}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 whitespace-nowrap text-[10px]">
                    {row.validTime}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap text-[10px]">
                    {row.retrievedAt}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap text-[10px]">
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-300">{row.source}</span>
                      <a
                        href={row.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-teal-400 hover:text-teal-300"
                        title={`Open official ${row.source}`}
                      >
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
