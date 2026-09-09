'use client';

import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MarineZone } from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';
import { MAP_CONFIG } from '@/lib/mapConfig';
import { MapLegend } from './MapLegend';
import {
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Layers,
  Compass,
  Crosshair
} from 'lucide-react';

interface MarineMapProps {
  zones?: MarineZone[];
  selectedZone: MarineZone | null;
  onSelectZone: (zone: MarineZone) => void;
  filterMode?: 'all' | 'safe' | 'hazards' | 'restricted';
  language?: string;
}

export const MarineMap: React.FC<MarineMapProps> = ({
  zones = DEMO_ZONES,
  selectedZone,
  onSelectZone,
  filterMode = 'all',
  language = 'en',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layersRef = useRef<{ [key: string]: L.LayerGroup }>({});
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);
  const [layerVisibility, setLayerVisibility] = useState<{
    hazards: boolean;
    restricted: boolean;
    suitable: boolean;
    caution: boolean;
  }>({
    hazards: true,
    restricted: true,
    suitable: true,
    caution: true,
  });

  const layerLabels = {
    en: { hazards: 'Hazards', suitable: 'Candidates', restricted: 'Geofences' },
    hi: { hazards: 'खतरे', suitable: 'उम्मीदवार', restricted: 'भू-बाड़' },
    mr: { hazards: 'धोके', suitable: 'उमेदवार', restricted: 'भू-सीमा' },
  }[language as 'en' | 'hi' | 'mr'] || { hazards: 'Hazards', suitable: 'Candidates', restricted: 'Geofences' };

  // Initialize Leaflet Map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    if (!mapInstanceRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: MAP_CONFIG.defaultCenter,
        zoom: MAP_CONFIG.defaultZoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom,
        zoomControl: false,
        attributionControl: false,
      });

      // OpenStreetMap Tile Layer
      L.tileLayer(MAP_CONFIG.tileUrl, {
        maxZoom: MAP_CONFIG.maxZoom,
        subdomains: MAP_CONFIG.subdomains,
      }).addTo(map);

      // Attribution
      L.control
        .attribution({
          position: 'bottomright',
          prefix: `<span class="text-[9px] text-slate-400 font-mono">${MAP_CONFIG.attribution}</span>`,
        })
        .addTo(map);

      mapInstanceRef.current = map;
      setMapLoaded(true);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Layers & Polygons
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    Object.values(layersRef.current).forEach((layer) => {
      if (layer) map.removeLayer(layer);
    });
    layersRef.current = {};

    const layerGroup = L.layerGroup();
    const activeZoneList = zones && zones.length > 0 ? zones : DEMO_ZONES;

    activeZoneList.forEach((zone) => {
      let isVisible = true;
      const statusKey = zone.status.toLowerCase();

      if (statusKey === 'high_risk' && !layerVisibility.hazards) isVisible = false;
      if (statusKey === 'restricted' && !layerVisibility.restricted) isVisible = false;
      if ((statusKey === 'suitable' || statusKey === 'suitable_candidate') && !layerVisibility.suitable) isVisible = false;
      if (statusKey === 'caution' && !layerVisibility.caution) isVisible = false;

      if (filterMode === 'safe' && statusKey !== 'suitable' && statusKey !== 'suitable_candidate' && statusKey !== 'caution') {
        isVisible = false;
      } else if (filterMode === 'hazards' && statusKey !== 'high_risk') {
        isVisible = false;
      } else if (filterMode === 'restricted' && statusKey !== 'restricted') {
        isVisible = false;
      }

      if (!isVisible) return;

      let fillColor = '#10B981';
      let strokeColor = '#34D399';
      let badgeBg = 'bg-emerald-600/90 border-emerald-400 text-emerald-100';

      if (statusKey === 'high_risk') {
        fillColor = '#EF4444';
        strokeColor = '#F87171';
        badgeBg = 'bg-rose-600/90 border-rose-400 text-rose-100';
      } else if (statusKey === 'caution') {
        fillColor = '#F59E0B';
        strokeColor = '#FBBF24';
        badgeBg = 'bg-amber-600/90 border-amber-400 text-amber-100';
      } else if (statusKey === 'restricted') {
        fillColor = '#6366F1';
        strokeColor = '#818CF8';
        badgeBg = 'bg-indigo-600/90 border-indigo-400 text-indigo-100';
      } else if (statusKey === 'insufficient_data') {
        fillColor = '#64748B';
        strokeColor = '#94A3B8';
        badgeBg = 'bg-slate-700/90 border-slate-500 text-slate-200';
      }

      const isCurrentSelected = selectedZone?.id === zone.id;

      const polygon = L.polygon(zone.coordinates as [number, number][], {
        color: isCurrentSelected ? '#38BDF8' : strokeColor,
        weight: isCurrentSelected ? 3 : 1.5,
        opacity: isCurrentSelected ? 1 : 0.85,
        fillColor: fillColor,
        fillOpacity: isCurrentSelected ? 0.35 : 0.18,
        dashArray: statusKey === 'restricted' ? '6, 6' : undefined,
      });

      polygon.on('click', () => {
        onSelectZone(zone);
      });

      const statusShort = (zone.statusLabel || 'ZONE').split(' ')[0];
      const markerIcon = L.divIcon({
        className: 'bg-transparent border-0',
        html: `
          <div class="cursor-pointer flex flex-col items-center justify-center pointer-events-auto select-none font-mono" style="width: 130px;">
            <div class="inline-flex items-center justify-center gap-1 px-2 py-0.5 rounded-md ${badgeBg} border text-[10px] font-bold shadow-lg whitespace-nowrap transition-all ${
          isCurrentSelected ? 'ring-2 ring-cyan-400 scale-110 shadow-cyan-500/50' : 'hover:scale-105'
        }">
              <span class="tracking-wider">${zone.code}</span>
              <span class="opacity-60 text-[8px]">•</span>
              <span class="text-[9px] uppercase tracking-wider">${statusShort}</span>
            </div>
            <span class="inline-block text-[9px] font-bold text-slate-200 bg-[#0F172A]/90 px-1.5 py-0.5 rounded shadow-md mt-1 border border-slate-700/80 whitespace-nowrap">
              RISK ${zone.riskScore}
            </span>
          </div>
        `,
        iconSize: [130, 48],
        iconAnchor: [65, 24],
      });

      const marker = L.marker(zone.center as [number, number], { icon: markerIcon });
      marker.on('click', () => {
        onSelectZone(zone);
      });

      polygon.addTo(layerGroup);
      marker.addTo(layerGroup);
    });

    layerGroup.addTo(map);
    layersRef.current['main'] = layerGroup;
  }, [mapLoaded, zones, selectedZone, filterMode, layerVisibility, onSelectZone]);

  // Auto-focus and fit bounds when active zones or selected zone changes
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    const activeZoneList = zones && zones.length > 0 ? zones : DEMO_ZONES;

    if (selectedZone) {
      map.flyTo(selectedZone.center as [number, number], 10, { duration: 0.8 });
    } else if (activeZoneList.length === 1) {
      map.flyTo(activeZoneList[0].center as [number, number], 10, { duration: 0.8 });
    } else if (activeZoneList.length > 1) {
      try {
        const bounds = activeZoneList.map(z => z.center as [number, number]);
        map.flyToBounds(bounds, { padding: [50, 50], maxZoom: 10, duration: 0.8 });
      } catch (e) {
        map.flyTo(MAP_CONFIG.defaultCenter, MAP_CONFIG.defaultZoom, { duration: 0.6 });
      }
    }
  }, [mapLoaded, zones, selectedZone]);

  const handleResetView = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(MAP_CONFIG.defaultCenter, MAP_CONFIG.defaultZoom, { duration: 0.6 });
    }
  };

  const handleZoomIn = () => {
    if (mapInstanceRef.current) mapInstanceRef.current.zoomIn();
  };

  const handleZoomOut = () => {
    if (mapInstanceRef.current) mapInstanceRef.current.zoomOut();
  };

  return (
    <div className="relative w-full h-[520px] lg:h-[620px] rounded-xl overflow-hidden border border-slate-800 bg-[#0A1628] shadow-lg">
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Top Left: Operational Region Badge */}
      <div className="absolute top-3 left-3 z-[400] flex flex-col gap-0.5 bg-[#0F172A]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 text-xs font-mono shadow-md">
        <div className="flex items-center gap-2">
          <Crosshair className="w-3.5 h-3.5 text-teal-400" />
          <span className="font-bold text-white tracking-wide">Maharashtra Operational Grid</span>
          <span className="text-slate-400 text-[10px] hidden sm:inline">18.2°N – 19.5°N</span>
        </div>
        <span className="text-[9px] text-teal-400/80">INCOIS OSF / GIS Cadastre Ground Overlay</span>
      </div>

      {/* Top Right: Layer Toggles */}
      <div className="absolute top-3 right-3 z-[400] flex items-center gap-1 bg-[#0F172A]/90 backdrop-blur-md p-1 rounded-lg border border-slate-700/80 text-xs font-mono shadow-md">
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, hazards: !prev.hazards }))
          }
          className={`px-2 py-1 rounded text-[10px] font-bold transition-colors ${
            layerVisibility.hazards
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {layerLabels.hazards}
        </button>
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, suitable: !prev.suitable }))
          }
          className={`px-2 py-1 rounded text-[10px] font-bold transition-colors ${
            layerVisibility.suitable
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {layerLabels.suitable}
        </button>
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, restricted: !prev.restricted }))
          }
          className={`px-2 py-1 rounded text-[10px] font-bold transition-colors ${
            layerVisibility.restricted
              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {layerLabels.restricted}
        </button>
      </div>

      {/* Bottom Left: Map Legend */}
      <div className="absolute bottom-3 left-3 z-[400]">
        <MapLegend language={language} />
      </div>

      {/* Bottom Right: Zoom & Reset Controls */}
      <div className="absolute bottom-3 right-3 z-[400] flex items-center gap-1 bg-[#0F172A]/90 backdrop-blur-md p-1 rounded-lg border border-slate-700/80 shadow-md">
        <button
          onClick={handleZoomIn}
          className="p-1.5 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-1.5 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <div className="w-px h-3.5 bg-slate-700 mx-0.5"></div>
        <button
          onClick={handleResetView}
          className="p-1.5 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition-colors"
          title="Reset Map to Mumbai Coast"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
