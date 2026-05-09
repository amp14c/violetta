'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getPrefs, setPrefs } from '@/lib/storage';
import { getBrowserLocation, geocodeQuery } from '@/lib/location';
import { requestNotificationPermission } from '@/lib/notifications';
import type { UserPreferences } from '@/lib/types';

export default function SettingsPage() {
  const router = useRouter();
  const [prefs, setLocalPrefs] = useState<UserPreferences | null>(null);
  const [locationQuery, setLocationQuery] = useState('');
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState('');

  useEffect(() => {
    setLocalPrefs(getPrefs());
  }, []);

  function update(changes: Partial<UserPreferences>) {
    const updated = setPrefs(changes);
    setLocalPrefs(updated);
  }

  async function handleUseGPS() {
    setLocationLoading(true);
    setLocationError('');
    try {
      const loc = await getBrowserLocation();
      update({ location: loc });
    } catch {
      setLocationError('Could not get GPS location. Try typing a city instead.');
    } finally {
      setLocationLoading(false);
    }
  }

  async function handleGeocode() {
    if (!locationQuery.trim()) return;
    setLocationLoading(true);
    setLocationError('');
    try {
      const loc = await geocodeQuery(locationQuery.trim());
      update({ location: loc });
      setLocationQuery('');
    } catch {
      setLocationError(`Could not find "${locationQuery}". Try a city name.`);
    } finally {
      setLocationLoading(false);
    }
  }

  if (!prefs) return null;

  return (
    <div className="flex flex-col min-h-screen max-w-md mx-auto pb-8">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 pt-12 pb-6">
        <button
          onClick={() => router.back()}
          className="w-10 h-10 flex items-center justify-center rounded-full bg-white/5 border border-white/10 text-white/60 hover:text-white transition-colors"
          aria-label="Back"
        >
          ←
        </button>
        <h1 className="text-lg font-bold text-white">Settings</h1>
      </header>

      <div className="flex flex-col gap-6 px-4">

        {/* Location */}
        <section>
          <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">Location</h2>
          <div className="bg-white/5 rounded-2xl border border-white/10 overflow-hidden">
            {prefs.location && (
              <div className="px-4 py-3 border-b border-white/10 flex items-center gap-2">
                <span className="text-sm text-white/50">📍</span>
                <span className="text-sm text-white/80 font-medium">{prefs.location.label}</span>
              </div>
            )}
            <button
              onClick={handleUseGPS}
              disabled={locationLoading}
              className="w-full flex items-center gap-3 px-4 py-3 border-b border-white/10 text-left hover:bg-white/5 transition-colors disabled:opacity-50"
            >
              <span className="text-lg">📡</span>
              <span className="text-sm text-white/80">Use current location</span>
            </button>
            <div className="flex items-center gap-2 px-4 py-3">
              <input
                type="text"
                value={locationQuery}
                onChange={(e) => setLocationQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGeocode()}
                placeholder="City or ZIP code…"
                className="flex-1 bg-transparent text-sm text-white placeholder-white/30 outline-none"
              />
              <button
                onClick={handleGeocode}
                disabled={locationLoading || !locationQuery.trim()}
                className="text-violet-400 text-sm font-semibold disabled:opacity-40 hover:text-violet-300 transition-colors"
              >
                {locationLoading ? '…' : 'Search'}
              </button>
            </div>
          </div>
          {locationError && (
            <p className="text-red-400 text-xs mt-2 px-1">{locationError}</p>
          )}
        </section>

        {/* Quiet Hours */}
        <section>
          <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">Quiet Hours</h2>
          <div className="bg-white/5 rounded-2xl border border-white/10 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
              <div className="flex items-center gap-3">
                <span className="text-lg">🌙</span>
                <span className="text-sm text-white/80">Sleep time</span>
              </div>
              <input
                type="time"
                value={prefs.quietHoursStart}
                onChange={(e) => update({ quietHoursStart: e.target.value })}
                className="bg-white/10 rounded-lg px-3 py-1.5 text-sm text-white border border-white/10 outline-none"
              />
            </div>
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-lg">☀️</span>
                <span className="text-sm text-white/80">Wake time</span>
              </div>
              <input
                type="time"
                value={prefs.quietHoursEnd}
                onChange={(e) => update({ quietHoursEnd: e.target.value })}
                className="bg-white/10 rounded-lg px-3 py-1.5 text-sm text-white border border-white/10 outline-none"
              />
            </div>
          </div>
          <p className="text-white/30 text-xs mt-2 px-1">No notifications between these times.</p>
        </section>

        {/* Notifications */}
        <section>
          <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">Notifications</h2>
          <div className="bg-white/5 rounded-2xl border border-white/10">
            <div className="flex items-center justify-between px-4 py-4">
              <div className="flex items-center gap-3">
                <span className="text-lg">🔔</span>
                <div>
                  <p className="text-sm text-white/80 font-medium">UV alerts &amp; reminders</p>
                  <p className="text-xs text-white/40 mt-0.5">Get notified when UV crosses 3</p>
                </div>
              </div>
              <button
                onClick={async () => {
                if (!prefs.notificationsEnabled) {
                  const token = await requestNotificationPermission();
                  if (!token) return; // permission denied — don't toggle on
                } else {
                  update({ notificationsEnabled: false });
                }
              }}
                className={`w-12 h-6 rounded-full transition-all duration-200 relative ${
                  prefs.notificationsEnabled ? 'bg-violet-600' : 'bg-white/20'
                }`}
              >
                <span
                  className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all duration-200 ${
                    prefs.notificationsEnabled ? 'left-6' : 'left-0.5'
                  }`}
                />
              </button>
            </div>
          </div>
        </section>

        {/* About */}
        <section>
          <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">About</h2>
          <div className="bg-white/5 rounded-2xl border border-white/10 px-4 py-4">
            <p className="text-sm text-white/50 leading-relaxed">
              UV data provided by{' '}
              <span className="text-white/70 font-medium">Open-Meteo</span> — free and open source.
              No account required. Your location is stored locally on your device only.
            </p>
          </div>
        </section>

      </div>
    </div>
  );
}
