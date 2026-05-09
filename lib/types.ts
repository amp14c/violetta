export interface UserLocation {
  lat: number;
  lon: number;
  label: string; // "New York, NY" or "10001" or "Current Location"
}

export interface HourlyUV {
  time: string;   // ISO string "2026-05-09T14:00"
  uv: number;
}

export interface UVForecast {
  current: number;
  hourly: HourlyUV[];
  peakUV: number;
  peakTime: string; // ISO string
  fetchedAt: number; // Date.now()
}

export interface UserPreferences {
  location: UserLocation | null;
  indoorMode: boolean;
  quietHoursStart: string; // "22:00"
  quietHoursEnd: string;   // "07:00"
  notificationsEnabled: boolean;
  lastNotifiedAt: number | null;    // Date.now() of last UV alert
  lastReapplyNotifiedAt: number | null;
  morningSummarySentDate: string | null; // "2026-05-09"
}
