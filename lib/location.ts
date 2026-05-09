import type { UserLocation } from './types';

export function getBrowserLocation(): Promise<UserLocation> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        label: 'Current Location',
      }),
      (err) => reject(new Error(err.message)),
      { timeout: 10000 }
    );
  });
}

export async function geocodeQuery(query: string): Promise<UserLocation> {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=1&language=en&format=json`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Geocoding request failed');
  const data = await res.json();
  const result = data.results?.[0];
  if (!result) throw new Error(`No results found for "${query}"`);
  return {
    lat: result.latitude,
    lon: result.longitude,
    label: [result.name, result.admin1, result.country_code].filter(Boolean).join(', '),
  };
}
