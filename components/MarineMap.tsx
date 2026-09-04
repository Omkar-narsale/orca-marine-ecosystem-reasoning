'use client';

import React, { useEffect, useRef, useState } from 'react';
import { MarineZone } from '@/types/marine';
import { DEMO_ZONES } from '@/data/demoZones';
import { MAP_CONFIG } from '@/lib/mapConfig';
import { MapLegend } from './MapLegend';
import {
  RotateCcw,
  ZoomIn,
  ZoomOut,
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
  const mapInstanceRef = useRef<any>(null);
  const layersRef = useRef<{ [key: string]: any }>({});
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
    en: { hazards: 'Hazards', suitable: 'Suitable', restricted: 'Geofences' },
    hi: { hazards: 'खतरे', suitable: 'अनुकूल', restricted: 'भू-बाड़' },
    mr: { hazards: 'धोके', suitable: 'अनुकूल', restricted: 'भू-सीमा' },
  }[language as 'en' | 'hi' | 'mr'] || { hazards: 'Hazards', suitable: 'Suitable', restricted: 'Geofences' };

  // Initialize Leaflet Map
  useEffect(() => {
    let isMounted = true;

    const initMap = async () => {
      if (typeof window === 'undefined' || !mapContainerRef.current) return;

      const L = (await import('leaflet')).default;

      if (!isMounted) return;

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

        // Required OpenStreetMap Attribution
        L.control
          .attribution({
            position: 'bottomright',
            prefix: `<span class="text-[9px] text-slate-500 font-sans">${MAP_CONFIG.attribution}</span>`,
          })
          .addTo(map);

        mapInstanceRef.current = map;
        setMapLoaded(true);
      }
    };

    initMap();

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Layers & Polygons
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;

    const renderLayers = async () => {
      const L = (await import('leaflet')).default;
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
        let strokeColor = '#059669';
        let badgeBg = 'bg-emerald-600';

        if (statusKey === 'high_risk') {
          fillColor = '#EF4444';
          strokeColor = '#DC2626';
          badgeBg = 'bg-rose-600';
        } else if (statusKey === 'caution') {
          fillColor = '#F59E0B';
          strokeColor = '#D97706';
          badgeBg = 'bg-amber-600';
        } else if (statusKey === 'restricted') {
          fillColor = '#6366F1';
          strokeColor = '#4F46E5';
          badgeBg = 'bg-indigo-600';
        } else if (statusKey === 'insufficient_data') {
          fillColor = '#94A3B8';
          strokeColor = '#64748B';
          badgeBg = 'bg-slate-500';
        }

        const isCurrentSelected = selectedZone?.id === zone.id;

        const polygon = L.polygon(zone.coordinates, {
          color: strokeColor,
          weight: isCurrentSelected ? 2.5 : 1.5,
          opacity: 0.9,
          fillColor: fillColor,
          fillOpacity: isCurrentSelected ? 0.32 : 0.20,
          dashArray: statusKey === 'restricted' ? '5, 5' : undefined,
        });

        polygon.on('click', () => {
          onSelectZone(zone);
        });

        // Clean Minimal Center Badge with Dynamic Spacing (Prevents Text Overlap)
        const statusShort = (zone.statusLabel || 'ZONE').split(' ')[0];
        const markerIcon = L.divIcon({
          className: 'bg-transparent border-0',
          html: `
            <div class="cursor-pointer flex flex-col items-center justify-center pointer-events-auto select-none" style="width: 120px;">
              <div class="inline-flex items-center justify-center gap-1.5 px-2.5 py-1 rounded-md ${badgeBg} text-white font-mono text-[11px] font-bold shadow-md whitespace-nowrap leading-tight transition-transform ${
            isCurrentSelected ? 'ring-2 ring-slate-900 ring-offset-1 scale-110 shadow-lg' : 'hover:scale-105'
          }">
                <span class="tracking-wide">${zone.code}</span>
                <span class="opacity-60 text-[9px]">•</span>
                <span class="text-[10px] font-semibold opacity-95 uppercase tracking-wider">${statusShort}</span>
              </div>
              <span class="inline-block text-[9px] font-mono font-bold text-slate-800 bg-white/95 px-1.5 py-0.5 rounded shadow-sm mt-1 border border-slate-300/80 whitespace-nowrap leading-none">
                Risk ${zone.riskScore}
              </span>
            </div>
          `,
          iconSize: [120, 48],
          iconAnchor: [60, 24],
        });

        const marker = L.marker(zone.center, { icon: markerIcon });
        marker.on('click', () => {
          onSelectZone(zone);
        });

        polygon.addTo(layerGroup);
        marker.addTo(layerGroup);
      });

      layerGroup.addTo(map);
      layersRef.current['main'] = layerGroup;
    };

    renderLayers();
  }, [mapLoaded, zones, selectedZone, filterMode, layerVisibility, onSelectZone]);

  useEffect(() => {
    if (selectedZone && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(selectedZone.center, 10, { duration: 0.8 });
    }
  }, [selectedZone]);

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
    <div className="relative w-full h-[520px] lg:h-[580px] rounded-2xl overflow-hidden border border-slate-200/80 bg-slate-100 shadow-sm">
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Top Left: Region Title & Prototype Geometry Label */}
      <div className="absolute top-3.5 left-3.5 z-[400] flex flex-col gap-1 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-slate-200/70 text-xs shadow-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-teal-500"></span>
          <span className="font-semibold text-slate-900">Maharashtra Coastal Region</span>
          <span className="text-slate-400 font-mono text-[10px] hidden sm:inline">18.2°N – 19.5°N</span>
        </div>
        <span className="text-[9px] text-slate-400 font-mono">Prototype / Demonstration Geometry</span>
      </div>

      {/* Top Right: Layer Toggles */}
      <div className="absolute top-3.5 right-3.5 z-[400] flex items-center gap-1 bg-white/90 backdrop-blur-sm p-1 rounded-lg border border-slate-200/70 text-xs shadow-xs">
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, hazards: !prev.hazards }))
          }
          className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
            layerVisibility.hazards
              ? 'bg-rose-50 text-rose-800 font-semibold'
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          {layerLabels.hazards}
        </button>
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, suitable: !prev.suitable }))
          }
          className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
            layerVisibility.suitable
              ? 'bg-emerald-50 text-emerald-800 font-semibold'
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          {layerLabels.suitable}
        </button>
        <button
          onClick={() =>
            setLayerVisibility((prev) => ({ ...prev, restricted: !prev.restricted }))
          }
          className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
            layerVisibility.restricted
              ? 'bg-indigo-50 text-indigo-800 font-semibold'
              : 'text-slate-400 hover:text-slate-600'
          }`}
        >
          {layerLabels.restricted}
        </button>
      </div>

      {/* Bottom Left: Map Legend */}
      <div className="absolute bottom-3.5 left-3.5 z-[400]">
        <MapLegend language={language} />
      </div>

      {/* Bottom Right: Zoom & Reset */}
      <div className="absolute bottom-3.5 right-3.5 z-[400] flex items-center gap-1 bg-white/95 backdrop-blur-sm p-1 rounded-lg border border-slate-200/70 shadow-xs">
        <button
          onClick={handleZoomIn}
          className="p-1.5 text-slate-600 hover:text-slate-900 rounded hover:bg-slate-100 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-1.5 text-slate-600 hover:text-slate-900 rounded hover:bg-slate-100 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <div className="w-px h-4 bg-slate-200 mx-0.5"></div>
        <button
          onClick={handleResetView}
          className="p-1.5 text-slate-600 hover:text-slate-900 rounded hover:bg-slate-100 transition-colors"
          title="Reset Map View to Mumbai Coast"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
