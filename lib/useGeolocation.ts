'use client';

import { useState, useEffect, useCallback } from 'react';

export type GeolocationStatus = 'AVAILABLE' | 'DENIED' | 'UNAVAILABLE' | 'PROMPT';

export interface GeolocationState {
  status: GeolocationStatus;
  latitude: number | null;
  longitude: number | null;
  accuracy_m: number | null;
  timestamp: string | null;
  error: string | null;
  isSupported: boolean;
  requestLocation: () => void;
}

export function useGeolocation(): GeolocationState {
  const [status, setStatus] = useState<GeolocationStatus>('PROMPT');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [accuracy_m, setAccuracyM] = useState<number | null>(null);
  const [timestamp, setTimestamp] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState<boolean>(true);

  const requestLocation = useCallback(() => {
    if (typeof window === 'undefined' || !navigator.geolocation) {
      setIsSupported(false);
      setStatus('UNAVAILABLE');
      setError('Browser Geolocation is not supported by your device/browser.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(position.coords.latitude);
        setLongitude(position.coords.longitude);
        setAccuracyM(Math.round(position.coords.accuracy));
        setTimestamp(new Date(position.timestamp).toISOString());
        setStatus('AVAILABLE');
        setError(null);
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          setStatus('DENIED');
          setError('Location access was denied. Please allow location permissions in your browser settings.');
        } else if (err.code === err.POSITION_UNAVAILABLE) {
          setStatus('UNAVAILABLE');
          setError('Location information is currently unavailable from your device.');
        } else {
          setStatus('UNAVAILABLE');
          setError('Location request timed out.');
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  }, []);

  useEffect(() => {
    // Check permission status if navigator.permissions API is available
    if (typeof window !== 'undefined' && navigator.permissions && navigator.permissions.query) {
      navigator.permissions
        .query({ name: 'geolocation' as PermissionName })
        .then((perm) => {
          if (perm.state === 'granted') {
            requestLocation();
          } else if (perm.state === 'denied') {
            setStatus('DENIED');
          } else {
            setStatus('PROMPT');
          }

          perm.onchange = () => {
            if (perm.state === 'granted') {
              requestLocation();
            } else if (perm.state === 'denied') {
              setStatus('DENIED');
            } else {
              setStatus('PROMPT');
            }
          };
        })
        .catch(() => {
          // Fallback if permissions query fails
          requestLocation();
        });
    } else {
      requestLocation();
    }
  }, [requestLocation]);

  return {
    status,
    latitude,
    longitude,
    accuracy_m,
    timestamp,
    error,
    isSupported,
    requestLocation
  };
}
