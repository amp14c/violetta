'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { getPrefs, setPrefs } from '@/lib/storage';
import { fetchUVForecast } from '@/lib/uv';
import { getBrowserLocation } from '@/lib/location';
import { runNotificationScheduler } from '@/lib/notificationScheduler';
import type { UVForecast, UserPreferences } from '@/lib/types';
import UVStatusCard from '@/components/UVStatusCard';
import RecommendedActions from '@/components/RecommendedActions';
import NextReapplyBanner from '@/components/NextReapplyBanner';
import HourlyUVChart from '@/components/HourlyUVChart';
import IndoorOutdoorToggle from '@/components/IndoorOutdoorToggle';
import SunscreenGuidance from '@/components/SunscreenGuidance';
import EducationalTip from '@/components/EducationalTip';

export default function HomePage() {
  const [prefs, setLocalPrefs] = useState<UserPreferences | null>(null);
  const [forecast, setForecast] = useState<UVForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadForecast = useCallback(async (p: UserPreferences) => {
    setError(null);
    try {
      let loc = p.location;
      if (!loc) {
        loc = await getBrowserLocation();
        const updated = setPrefs({ location: loc });
        setLocalPrefs(updated);
      }
      const data = await fetchUVForecast(loc.lat, loc.lon);
      setForecast(data);
      runNotificationScheduler(data).catch(console.error);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const p = getPrefs();
    setLocalPrefs(p);
    loadForecast(p);
  }, [loadForecast]);

  function handleIndoorToggle(indoor: boolean) {
    const updated = setPrefs({ indoorMode: indoor });
    setLocalPrefs(updated);
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <div className="w-12 h-12 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
        <p className="text-white/40 text-sm">Checking UV levels…</p>
      </div>
    );
  }

  if (error || !forecast || !prefs) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 px-8 text-center">
        <span className="text-4xl">📍</span>
        <p className="text-white/70 text-sm">{error || 'Could not load UV data.'}</p>
        <Link href="/settings" className="text-violet-400 text-sm underline">
          Set location manually
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen max-w-md mx-auto pb-8">
      {/* Header */}
      <header className="flex items-center justify-between px-4 pt-12 pb-2">
        <h1 className="text-lg font-bold tracking-tight text-white">Violetta</h1>
        <Link
          href="/settings"
          className="w-10 h-10 flex items-center justify-center rounded-full bg-white/5 border border-white/10 text-white/60 hover:text-white transition-colors"
          aria-label="Settings"
        >
          ⚙️
        </Link>
      </header>

      {/* UV Status */}
      <UVStatusCard uv={forecast.current} location={prefs.location?.label ?? 'Current Location'} />

      {/* Indoor / Outdoor toggle */}
      <IndoorOutdoorToggle indoorMode={prefs.indoorMode} onChange={handleIndoorToggle} />

      {/* Reapply banner */}
      <NextReapplyBanner
        uv={forecast.current}
        indoorMode={prefs.indoorMode}
        lastAppliedAt={prefs.lastNotifiedAt}
      />

      {/* Recommended actions */}
      <RecommendedActions uv={forecast.current} indoorMode={prefs.indoorMode} />

      {/* Hourly chart */}
      <HourlyUVChart hourly={forecast.hourly} peakTime={forecast.peakTime} />

      {/* Sunscreen guidance */}
      <SunscreenGuidance />

      {/* Educational tip */}
      <EducationalTip />

      {/* Peak info */}
      {!prefs.indoorMode && (
        <div className="mx-4 mb-6 bg-white/5 rounded-2xl border border-white/10 px-4 py-3 flex items-center gap-3">
          <span className="text-xl">📊</span>
          <p className="text-sm text-white/70">
            Peak UV today is{' '}
            <span className="font-bold text-white">{forecast.peakUV}</span> at{' '}
            <span className="font-bold text-white">
              {new Date(forecast.peakTime).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}
