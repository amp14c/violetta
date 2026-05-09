import type { HourlyUV } from './types';

export function isWithinQuietHours(start: string, end: string): boolean {
  const now = new Date();
  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);
  const nowMins = now.getHours() * 60 + now.getMinutes();
  const startMins = sh * 60 + sm;
  const endMins = eh * 60 + em;

  // Handle overnight quiet hours (e.g. 22:00 → 07:00)
  if (startMins > endMins) {
    return nowMins >= startMins || nowMins < endMins;
  }
  return nowMins >= startMins && nowMins < endMins;
}

export function uvCrossedThreshold(hourly: HourlyUV[]): boolean {
  const now = Date.now();
  const nowHour = new Date(now);
  nowHour.setMinutes(0, 0, 0);
  const prevHourTs = nowHour.getTime() - 60 * 60 * 1000;

  const prev = hourly.find((h) => new Date(h.time).getTime() === prevHourTs);
  const curr = hourly.find((h) => new Date(h.time).getTime() === nowHour.getTime());

  if (!prev || !curr) return false;
  return prev.uv < 3 && curr.uv >= 3;
}

export function todayDateString(): string {
  return new Date().toISOString().slice(0, 10);
}

export function isAfterWakeTime(wakeTime: string): boolean {
  const [wh, wm] = wakeTime.split(':').map(Number);
  const now = new Date();
  const nowMins = now.getHours() * 60 + now.getMinutes();
  return nowMins >= wh * 60 + wm;
}
