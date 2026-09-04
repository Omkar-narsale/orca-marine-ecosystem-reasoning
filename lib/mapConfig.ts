export interface MapConfig {
  provider: string;
  tileUrl: string;
  attribution: string;
  maxZoom: number;
  minZoom: number;
  subdomains: string[];
  defaultCenter: [number, number]; // [lat, lng]
  defaultZoom: number;
}

export const MAP_CONFIG: MapConfig = {
  provider: 'OpenStreetMap',
  tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
  maxZoom: 18,
  minZoom: 6,
  subdomains: ['a', 'b', 'c'],
  defaultCenter: [18.96, 72.60], // Centered right off the coast of Mumbai
  defaultZoom: 9, // Optimal zoom showing Zone A, B, C, D and Maharashtra coastline
};
