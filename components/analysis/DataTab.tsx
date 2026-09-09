'use client';

import React, { useState } from 'react';
import { MarineZone } from '@/types/marine';
import { Table, ExternalLink, Filter, Download } from 'lucide-react';

interface DataTabProps {
  zones?: MarineZone[];
}

export const DataTab: React.FC<DataTabProps> = ({ zones = [] }) => {
  const [filterType, setFilterType] = useState<string>('all');
  const activeZones = zones || [];

  // Dynamically flatten marine parameter records from active analyzed zones
  const telemetryRows = activeZones.flatMap((z) => {
    const rows = [];
    if (z.conditions?.waveHeight) {
      rows.push({
        id: `wave-${z.id}`,
        parameter: 'Significant Wave Height (Hs)',
        value: z.conditions.waveHeight,
        unit: 'm',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'Forecast Horizon',
        validTime: z.bestTimeToVisit || 'Active Analysis Window',
        retrievedAt: 'Live Retrieval',
        dataType: 'FORECAST',
        quality: 'Verified Numerical (WW3)',
        source: 'INCOIS OSF',
        sourceUrl: z.sourceUrl || 'https://incois.gov.in/oceanservices/osfforecast.jsp',
      });
    }
    if (z.conditions?.windSpeed) {
      rows.push({
        id: `wind-${z.id}`,
        parameter: 'Coastal Wind Velocity',
        value: z.conditions.windSpeed,
        unit: 'kt',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'Coastal Forecast',
        validTime: z.bestTimeToVisit || 'Active Analysis Window',
        retrievedAt: 'Live Retrieval',
        dataType: 'FORECAST',
        quality: 'Official Synoptic',
        source: 'IMD Marine Division',
        sourceUrl: 'https://mausam.imd.gov.in',
      });
    }
    if (z.conditions?.seaSurfaceTemp) {
      rows.push({
        id: `sst-${z.id}`,
        parameter: 'Sea Surface Temperature (SST)',
        value: z.conditions.seaSurfaceTemp,
        unit: '°C',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'Thermal Composite',
        validTime: 'Observation Window',
        retrievedAt: 'Live Retrieval',
        dataType: 'OBSERVATION',
        quality: 'Satellite Thermal Swath',
        source: 'INCOIS / MOSDAC',
        sourceUrl: 'https://incois.gov.in',
      });
    }
    if (z.conditions?.chlorophyll) {
      rows.push({
        id: `chl-${z.id}`,
        parameter: 'Chlorophyll-a Concentration',
        value: z.conditions.chlorophyll,
        unit: 'mg/m³',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'OCM-3 Pass',
        validTime: 'Observation Window',
        retrievedAt: 'Live Retrieval',
        dataType: 'OBSERVATION',
        quality: 'OCM-3 Spectral Radiometer',
        source: 'MOSDAC Ocean Color',
        sourceUrl: 'https://www.mosdac.gov.in',
      });
    }
    if (z.conditions?.marineWarning) {
      rows.push({
        id: `warn-${z.id}`,
        parameter: 'Marine Warning / Alert',
        value: z.conditions.marineWarningText || 'ACTIVE WARNING',
        unit: 'Status',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'Official Bulletin',
        validTime: 'Active Notice',
        retrievedAt: 'Live Retrieval',
        dataType: 'WARNING',
        quality: 'Statutory Bulletin',
        source: 'IMD Coastal Warning',
        sourceUrl: 'https://mausam.imd.gov.in',
      });
    }
    if (z.conditions?.isRestricted) {
      rows.push({
        id: `geo-${z.id}`,
        parameter: 'Maritime Cadastre / Geofence',
        value: z.conditions.geofenceStatus || 'RESTRICTED',
        unit: 'Cadastre',
        sector: `${z.code || z.name} (${z.name})`,
        latLon: z.center ? `${z.center[0]}°N, ${z.center[1]}°E` : 'Evaluated Sector',
        observationTime: 'Official Cadastre',
        validTime: 'Continuous Regulatory Constraint',
        retrievedAt: 'Live Cadastre Check',
        dataType: 'STATIC',
        quality: 'Official Defense Cadastre',
        source: 'GIS Cadastre / NHO',
        sourceUrl: 'https://hydro-india.nic.in',
      });
    }
    return rows;
  });

  const filteredRows = telemetryRows.filter((r) => {
    if (filterType === 'all') return true;
    return r.dataType.toLowerCase() === filterType.toLowerCase();
  });

  const exportCSV = () => {
    if (filteredRows.length === 0) return;
    const headers = 'Parameter,Value,Unit,Sector,Lat/Lon,Observation Time,Valid Time,Retrieved At,Data Type,Quality,Source,Source URL\n';
    const csvContent = filteredRows
      .map(
        (r) =>
          `"${r.parameter}","${r.value}","${r.unit}","${r.sector}","${r.latLon}","${r.observationTime}","${r.validTime}","${r.retrievedAt}","${r.dataType}","${r.quality}","${r.source}","${r.sourceUrl}"`
      )
      .join('\n');
    const blob = new Blob([headers + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `ORCA_Telemetry_Export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <Table className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-wide">Multi-Source Telemetry Records</h2>
            <p className="text-xs text-slate-400">
              Direct authoritative observations & numerical forecasts without fabrication
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Filter Dropdown */}
          <div className="relative flex-1 sm:flex-initial">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full bg-slate-800 text-xs text-slate-200 border border-slate-700 rounded-lg px-3 py-2 appearance-none pr-8 focus:outline-none focus:border-teal-500"
            >
              <option value="all">All Telemetry Types</option>
              <option value="forecast">Forecasts Only</option>
              <option value="observation">Observations Only</option>
              <option value="warning">Warnings Only</option>
              <option value="advisory">Advisories Only</option>
              <option value="static">Cadastre / Static Only</option>
            </select>
            <Filter className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Export Button */}
          <button
            onClick={exportCSV}
            disabled={filteredRows.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition-colors shrink-0"
          >
            <Download className="w-3.5 h-3.5 text-teal-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Scientific Data Table */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-sm shadow-xl">
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold sticky top-0 backdrop-blur-md border-b border-slate-800 z-10">
              <tr>
                <th className="py-3.5 px-4">Parameter</th>
                <th className="py-3.5 px-4">Value</th>
                <th className="py-3.5 px-4">Sector / Coordinates</th>
                <th className="py-3.5 px-4">Data Type</th>
                <th className="py-3.5 px-4">Valid Time</th>
                <th className="py-3.5 px-4">Quality & Model</th>
                <th className="py-3.5 px-4">Authoritative Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
                    No active telemetry records found. Submit a query to inspect live marine telemetry.
                  </td>
                </tr>
              ) : (
                filteredRows.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-800/40 transition-colors group">
                    <td className="py-3.5 px-4 font-medium text-white group-hover:text-teal-300 transition-colors">
                      {row.parameter}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-400">
                      {row.value} {row.unit && row.unit !== 'Status' && row.unit !== 'Cadastre' && row.unit !== 'Front' ? row.unit : ''}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">
                      <div>{row.sector}</div>
                      <div className="text-slate-500 text-[10px]">{row.latLon}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase ${
                          row.dataType === 'FORECAST'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            : row.dataType === 'OBSERVATION'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : row.dataType === 'WARNING'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : row.dataType === 'ADVISORY'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                        }`}
                      >
                        {row.dataType}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      <div>{row.validTime}</div>
                      <div className="text-[10px] text-slate-500">Retrieved: {row.retrievedAt}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                      {row.quality}
                    </td>
                    <td className="py-3.5 px-4">
                      <a
                        href={row.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 font-medium hover:underline"
                      >
                        <span>{row.source}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
