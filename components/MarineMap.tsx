'use client';

import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MarineZone } from '@/types/marine';
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
import { mapController } from '@/lib/mapController';

export interface MarineMapProps {
  zones?: MarineZone[];
  selectedZone: MarineZone | null;
  onSelectZone: (zone: MarineZone) => void;
  filterMode?: 'all' | 'safe' | 'hazards' | 'restricted';
  language?: string;
  mapConfig?: any;
  userLocation?: {
    latitude: number;
    longitude: number;
    accuracy_m?: number;
    timestamp?: number;
  } | null;
}

/**
 * Safely normalizes any coordinate format (GeoJSON [lon, lat], Leaflet [lat, lon], or {lat, lon} object)
 * into a valid Leaflet [latitude, longitude] pair.
 * In India / Maharashtra coastal grid: Latitudes are ~5°N to ~35°N, Longitudes are ~65°E to ~95°E.
 */
function normalizeLatLng(c: any): [number, number] | null {
  if (!c) return null;
  let lat: number | undefined;
  let lon: number | undefined;

  if (Array.isArray(c)) {
    if (c.length < 2) return null;
    const v1 = Number(c[0]);
    const v2 = Number(c[1]);
    if (isNaN(v1) || isNaN(v2)) return null;

    // Detect GeoJSON [lon, lat] vs Leaflet [lat, lon]
    if (v1 > 50 && v1 < 110 && v2 > -10 && v2 < 45) {
      // v1 is lon (65-95), v2 is lat (10-30)
      lat = v2;
      lon = v1;
    } else if (v2 > 50 && v2 < 110 && v1 > -10 && v1 < 45) {
      // v1 is lat (10-30), v2 is lon (65-95)
      lat = v1;
      lon = v2;
    } else {
      // Default to GeoJSON standard [lon, lat]
      lat = v2;
      lon = v1;
    }
  } else if (typeof c === 'object') {
    const rawLat = c.lat ?? c.latitude;
    const rawLon = c.lng ?? c.lon ?? c.longitude;
    if (rawLat != null && rawLon != null) {
      const vLat = Number(rawLat);
      const vLon = Number(rawLon);
      if (!isNaN(vLat) && !isNaN(vLon)) {
        lat = vLat;
        lon = vLon;
      }
    }
  }

  if (lat == null || lon == null || isNaN(lat) || isNaN(lon)) return null;
  return [lat, lon];
}

/**
 * Extracts a clean list of [lat, lon] points for a polygon from either
 * GeoJSON 3D array [[[lon, lat], ...]], 2D array [[lat, lon], ...], or object arrays.
 */
function extractPolygonPoints(coords: any): [number, number][] {
  if (!Array.isArray(coords) || coords.length === 0) return [];

  // Case 1: 3D GeoJSON: [[[lon, lat], ...], ...]
  if (Array.isArray(coords[0]) && Array.isArray(coords[0][0])) {
    const ring = coords[0];
    return ring.map(normalizeLatLng).filter((pt): pt is [number, number] => pt !== null);
  }

  // Case 2: 2D array: [[lat, lon], [lat, lon], ...]
  if (Array.isArray(coords[0])) {
    return coords.map(normalizeLatLng).filter((pt): pt is [number, number] => pt !== null);
  }

  return [];
}

/**
 * Extracts a clean list of [lat, lon] points for a LineString.
 */
function extractLineStringPoints(coords: any): [number, number][] {
  if (!Array.isArray(coords) || coords.length === 0) return [];
  return coords.map(normalizeLatLng).filter((pt): pt is [number, number] => pt !== null);
}

/**
 * Extracts a clean [lat, lon] point for a Point geometry or feature.
 */
function extractPointCoordinates(coords: any, feat?: any): [number, number] | null {
  if (coords) {
    const pt = normalizeLatLng(coords);
    if (pt) return pt;
  }
  if (feat) {
    const rawLat = feat.latitude ?? feat.lat ?? (Array.isArray(feat.center) ? feat.center[0] : feat.center?.lat);
    const rawLon = feat.longitude ?? feat.lon ?? (Array.isArray(feat.center) ? feat.center[1] : feat.center?.lng);
    if (rawLat != null && rawLon != null) {
      return normalizeLatLng([rawLat, rawLon]);
    }
  }
  return null;
}

export const MarineMap: React.FC<MarineMapProps> = ({
  zones = [],
  selectedZone,
  onSelectZone,
  filterMode = 'all',
  language = 'en',
  mapConfig,
  userLocation,
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
    const activeZoneList = zones && zones.length > 0 ? zones : [];

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

  // Subscribe to MapController action commands
  useEffect(() => {
    const unsubscribe = mapController.subscribe((command) => {
      const map = mapInstanceRef.current;
      if (!map) return;

      if (command.action === 'SELECT' || command.action === 'HIGHLIGHT') {
        if (command.center) {
          map.flyTo([command.center.lat, command.center.lng], command.zoom || 11, { duration: 1.0 });
        } else if (command.target_id) {
          const foundZone = zones.find((z) => z.id === command.target_id);
          if (foundZone && foundZone.center) {
            map.flyTo(foundZone.center as [number, number], 11, { duration: 1.0 });
            onSelectZone(foundZone);
          }
        }
      } else if (command.action === 'CENTER' && command.center) {
        map.flyTo([command.center.lat, command.center.lng], command.zoom || 10, { duration: 0.8 });
      } else if (command.action === 'FIT_BOUNDS' && command.geometry) {
        try {
          if (Array.isArray(command.geometry)) {
            map.flyToBounds(command.geometry, { padding: [40, 40], duration: 0.8 });
          }
        } catch (e) {}
      }
    });

    return () => {
      unsubscribe();
    };
  }, [zones, onSelectZone]);

  // Actual Browser User Location Layer (Pulsing marker + Accuracy Circle)
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    if (layersRef.current['user_loc']) {
      map.removeLayer(layersRef.current['user_loc']);
      delete layersRef.current['user_loc'];
    }

    if (!userLocation || userLocation.latitude == null || userLocation.longitude == null) return;

    const userGroup = L.layerGroup();
    const lat = userLocation.latitude;
    const lon = userLocation.longitude;
    const accuracy = userLocation.accuracy_m || 30;

    // Accuracy Circle
    const accCircle = L.circle([lat, lon], {
      radius: Math.max(accuracy, 20),
      color: '#06B6D4',
      fillColor: '#06B6D4',
      fillOpacity: 0.14,
      weight: 1.5,
      dashArray: '4, 4',
    });
    accCircle.addTo(userGroup);

    // Pulsing Marker
    const userIcon = L.divIcon({
      className: 'bg-transparent border-0',
      html: `
        <div class="flex flex-col items-center justify-center select-none font-mono pointer-events-auto" style="width: 140px; margin-left: -70px; margin-top: -24px;">
          <div class="relative flex items-center justify-center">
            <div class="absolute w-6 h-6 rounded-full bg-cyan-400/30 animate-ping"></div>
            <div class="w-4 h-4 rounded-full bg-cyan-500 border-2 border-white shadow-lg shadow-cyan-500/50 flex items-center justify-center">
              <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
            </div>
          </div>
          <span class="inline-block mt-1 text-[10px] font-bold text-cyan-200 bg-[#0F172A]/90 px-2 py-0.5 rounded shadow-lg border border-cyan-500/50 whitespace-nowrap">
            📍 YOU ARE HERE
          </span>
        </div>
      `,
      iconSize: [0, 0],
      iconAnchor: [0, 0],
    });

    const userMarker = L.marker([lat, lon], { icon: userIcon });
    userMarker.addTo(userGroup);

    userGroup.addTo(map);
    layersRef.current['user_loc'] = userGroup;
  }, [mapLoaded, userLocation]);

  // Dynamic GeoJSON Features Layer (LineString routes, candidate points, hazard polygons)
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    if (layersRef.current['features']) {
      map.removeLayer(layersRef.current['features']);
      delete layersRef.current['features'];
    }

    const features = mapConfig?.features || [];
    if (!features || features.length === 0) return;

    const featureGroup = L.layerGroup();
    const allCoordsForBounds: [number, number][] = [];

    features.forEach((feat: any) => {
      if (!feat) return;
      const geom = feat.geometry || feat;
      const geomType =
        geom?.type ||
        (feat.waypoints ? 'LineString' : Array.isArray(feat.coordinates) ? 'Polygon' : feat.latitude != null ? 'Point' : null);
      const coords = geom?.coordinates || feat.waypoints || feat.coordinates;
      const props = feat.properties || feat;

      // 1. LineString (Vessel routes)
      if (geomType === 'LineString' && coords) {
        const latLngs = extractLineStringPoints(coords);
        if (latLngs.length < 2) return;

        latLngs.forEach((c) => allCoordsForBounds.push(c));

        const isRecommended =
          props.is_recommended !== false &&
          !props.id?.includes('alt') &&
          !props.name?.toLowerCase().includes('alternative');
        const color = isRecommended ? '#06B6D4' : '#94A3B8';
        const weight = isRecommended ? 4 : 2.5;

        const polyline = L.polyline(latLngs, {
          color: color,
          weight: weight,
          opacity: isRecommended ? 0.95 : 0.7,
          dashArray: isRecommended ? undefined : '6, 6',
        });

        const routeTitle = props.name || props.title || 'Vessel Route';
        const distanceStr = props.distance_nm ? `${props.distance_nm} NM` : props.distance_km ? `${props.distance_km} km` : '';
        const timeStr = props.estimated_hours ? `~${props.estimated_hours}h` : props.duration_hours ? `~${props.duration_hours}h` : '';

        polyline.bindTooltip(`
          <div class="font-mono text-xs p-1">
            <div class="font-bold ${isRecommended ? 'text-cyan-400' : 'text-slate-300'}">${routeTitle}</div>
            ${isRecommended ? '<span class="text-[9px] bg-cyan-500/20 text-cyan-300 px-1 py-0.5 rounded">RECOMMENDED</span>' : '<span class="text-[9px] text-slate-400">ALTERNATIVE</span>'}
            <div class="text-[10px] text-slate-300 mt-1">${distanceStr} ${timeStr}</div>
          </div>
        `, { sticky: true });

        polyline.addTo(featureGroup);

        // Origin marker
        if (latLngs.length > 0) {
          const originIcon = L.divIcon({
            className: 'bg-transparent border-0',
            html: `
              <div class="flex flex-col items-center select-none font-mono" style="width: 100px; margin-left: -50px; margin-top: -24px;">
                <div class="w-3 h-3 rounded-full bg-emerald-400 border-2 border-slate-900 shadow"></div>
                <span class="text-[9px] font-bold text-emerald-300 bg-[#0F172A]/90 px-1 rounded mt-0.5 border border-emerald-500/50">ORIGIN</span>
              </div>
            `,
            iconSize: [0, 0],
          });
          L.marker(latLngs[0], { icon: originIcon }).addTo(featureGroup);
        }

        // Destination marker
        if (latLngs.length > 1) {
          const destIcon = L.divIcon({
            className: 'bg-transparent border-0',
            html: `
              <div class="flex flex-col items-center select-none font-mono" style="width: 110px; margin-left: -55px; margin-top: -24px;">
                <div class="w-3 h-3 rounded-full bg-cyan-400 border-2 border-slate-900 shadow"></div>
                <span class="text-[9px] font-bold text-cyan-300 bg-[#0F172A]/90 px-1 rounded mt-0.5 border border-cyan-500/50">DESTINATION</span>
              </div>
            `,
            iconSize: [0, 0],
          });
          L.marker(latLngs[latLngs.length - 1], { icon: destIcon }).addTo(featureGroup);
        }
      }

      // 2. Point (Candidates / PFZs / Spot coordinates)
      else if (geomType === 'Point' || feat.type === 'PFZ_CANDIDATE' || feat.sst_celsius != null) {
        const pt = extractPointCoordinates(coords, feat);
        if (!pt) return;

        allCoordsForBounds.push(pt);

        const ptName = props.name || props.title || 'Marine Target';
        const ptScore = props.suitability_score != null ? `Score ${props.suitability_score}` : '';

        const ptIcon = L.divIcon({
          className: 'bg-transparent border-0',
          html: `
            <div class="flex flex-col items-center select-none font-mono cursor-pointer" style="width: 110px; margin-left: -55px; margin-top: -24px;">
              <div class="w-3.5 h-3.5 rounded-full bg-teal-400 border-2 border-white shadow-md shadow-teal-500/50"></div>
              <span class="text-[9px] font-bold text-teal-200 bg-[#0F172A]/90 px-1.5 py-0.5 rounded mt-0.5 border border-teal-500/50 whitespace-nowrap">
                ${ptName.split(' ')[0]} ${ptScore}
              </span>
            </div>
          `,
          iconSize: [0, 0],
        });

        const ptMarker = L.marker(pt, { icon: ptIcon });
        ptMarker.bindTooltip(`<div class="font-mono text-xs font-bold text-teal-300">${ptName}</div>`);
        ptMarker.addTo(featureGroup);
      }

      // 3. Polygon (Hazard, restricted geofence, or sector polygon)
      else if (geomType === 'Polygon' || (coords && Array.isArray(coords))) {
        const latLngs = extractPolygonPoints(coords);
        if (latLngs.length < 3) return;

        latLngs.forEach((c) => allCoordsForBounds.push(c));

        const isHazard =
          props.type === 'WAVE_ALERT' ||
          props.type === 'WIND_ALERT' ||
          props.severity === 'CRITICAL' ||
          props.status === 'restricted' ||
          props.status === 'critical_risk';
        const polyColor = isHazard ? '#EF4444' : '#6366F1';

        const poly = L.polygon(latLngs, {
          color: polyColor,
          weight: 2,
          fillColor: polyColor,
          fillOpacity: 0.25,
          dashArray: isHazard ? undefined : '5, 5',
        });

        poly.bindTooltip(
          `<div class="font-mono text-xs font-bold text-slate-200">${props.title || props.name || 'Advisory Sector'}</div>`
        );
        poly.addTo(featureGroup);
      }
    });

    try {
      featureGroup.addTo(map);
      layersRef.current['features'] = featureGroup;
    } catch (err) {
      console.warn('Could not add dynamic feature group to Leaflet map:', err);
    }

    // Auto-fit bounds for features
    if (allCoordsForBounds.length > 1) {
      try {
        map.flyToBounds(allCoordsForBounds, { padding: [50, 50], maxZoom: 11, duration: 1.0 });
      } catch (e) {}
    }
  }, [mapLoaded, mapConfig]);

  // Auto-focus and fit bounds when active zones or selected zone changes
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    const activeZoneList = zones && zones.length > 0 ? zones : [];

    if (selectedZone) {
      map.flyTo(selectedZone.center as [number, number], 10, { duration: 0.8 });
    } else if (activeZoneList.length === 1) {
      map.flyTo(activeZoneList[0].center as [number, number], 10, { duration: 0.8 });
    } else if (activeZoneList.length > 1) {
      try {
        const bounds = activeZoneList.map((z) => z.center as [number, number]);
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
