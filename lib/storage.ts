import type { UserPreferences } from './types';

const KEY = 'violetta_prefs';

const defaults: UserPreferences = {
  location: null,
  indoorMode: false,
  quietHoursStart: '22:00',
  quietHoursEnd: '07:00',
  notificationsEnabled: false,
  lastNotifiedAt: null,
  lastReapplyNotifiedAt: null,
  morningSummarySentDate: null,
};

export function getPrefs(): UserPreferences {
  if (typeof window === 'undefined') return defaults;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? { ...defaults, ...JSON.parse(raw) } : defaults;
  } catch {
    return defaults;
  }
}

export function setPrefs(updates: Partial<UserPreferences>): UserPreferences {
  const next = { ...getPrefs(), ...updates };
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}
