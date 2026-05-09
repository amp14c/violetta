import type { UVForecast, HourlyUV } from './types';

export async function fetchUVForecast(lat: number, lon: number): Promise<UVForecast> {
  const url =
    `https://api.open-meteo.com/v1/forecast` +
    `?latitude=${lat}&longitude=${lon}` +
    `&hourly=uv_index&timezone=auto&forecast_days=2`;

  const res = await fetch(url);
  if (!res.ok) throw new Error('UV forecast request failed');
  const data = await res.json();

  const times: string[] = data.hourly.time;
  const uvValues: number[] = data.hourly.uv_index;

  const now = Date.now();
  const nowHour = new Date(now);
  nowHour.setMinutes(0, 0, 0);

  const hourly: HourlyUV[] = times.map((time, i) => ({
    time,
    uv: Math.round(uvValues[i] * 10) / 10,
  }));

  // Current UV = the hour slot closest to now
  const currentIndex = times.findIndex((t) => new Date(t) >= nowHour);
  const current = uvValues[currentIndex >= 0 ? currentIndex : 0] ?? 0;

  // Today only (next 24 hours from now) for peak
  const todaySlots = hourly.filter((h) => {
    const t = new Date(h.time).getTime();
    return t >= now && t <= now + 24 * 60 * 60 * 1000;
  });

  const peak = todaySlots.reduce(
    (max, h) => (h.uv > max.uv ? h : max),
    todaySlots[0] ?? { uv: 0, time: times[0] }
  );

  return {
    current: Math.round(current * 10) / 10,
    hourly,
    peakUV: peak.uv,
    peakTime: peak.time,
    fetchedAt: now,
  };
}

export function uvLabel(uv: number): string {
  if (uv < 3) return 'Low';
  if (uv < 6) return 'Moderate';
  if (uv < 8) return 'High';
  if (uv < 11) return 'Very High';
  return 'Extreme';
}

export function uvColor(uv: number): string {
  if (uv < 3) return '#22c55e';  // green
  if (uv < 6) return '#eab308';  // yellow
  if (uv < 8) return '#f97316';  // orange
  if (uv < 11) return '#ef4444'; // red
  return '#a855f7';              // violet
}
