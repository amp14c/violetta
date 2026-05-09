import { getPrefs, setPrefs } from './storage';
import { getFCMToken, sendPushNotification } from './notifications';
import {
  isWithinQuietHours,
  uvCrossedThreshold,
  todayDateString,
  isAfterWakeTime,
} from './uvLogic';
import type { UVForecast } from './types';

const TWO_HOURS = 2 * 60 * 60 * 1000;

export async function runNotificationScheduler(forecast: UVForecast): Promise<void> {
  const prefs = getPrefs();
  if (!prefs.notificationsEnabled) return;

  const token = getFCMToken();
  if (!token) return;

  const { current, hourly, peakUV, peakTime } = forecast;
  const inQuietHours = isWithinQuietHours(prefs.quietHoursStart, prefs.quietHoursEnd);
  const now = Date.now();

  // ── Morning summary ──────────────────────────────────────────────────────
  const today = todayDateString();
  if (
    !inQuietHours &&
    isAfterWakeTime(prefs.quietHoursEnd) &&
    prefs.morningSummarySentDate !== today &&
    peakUV >= 3
  ) {
    const peakTimeStr = new Date(peakTime).toLocaleTimeString([], {
      hour: 'numeric',
      minute: '2-digit',
    });
    await sendPushNotification(
      token,
      '☀️ UV Forecast for Today',
      `Peak UV is ${peakUV} at ${peakTimeStr}. Sunscreen recommended.`,
      'morning-summary'
    );
    setPrefs({ morningSummarySentDate: today });
    return; // one notification per scheduler run
  }

  if (inQuietHours) return;

  // ── UV threshold trigger ─────────────────────────────────────────────────
  const crossedThreshold = uvCrossedThreshold(hourly);
  const cooldownExpired = !prefs.lastNotifiedAt || now - prefs.lastNotifiedAt >= TWO_HOURS;

  if (crossedThreshold && cooldownExpired && !prefs.indoorMode) {
    await sendPushNotification(
      token,
      '🧴 UV is now harmful',
      `UV index is ${current}. Apply sunscreen now and wear sunglasses.`,
      'uv-alert'
    );
    setPrefs({ lastNotifiedAt: now });
    return;
  }

  // ── Reapplication reminder ────────────────────────────────────────────────
  if (
    current >= 3 &&
    !prefs.indoorMode &&
    prefs.lastNotifiedAt &&
    now - prefs.lastNotifiedAt >= TWO_HOURS &&
    (!prefs.lastReapplyNotifiedAt || now - prefs.lastReapplyNotifiedAt >= TWO_HOURS)
  ) {
    await sendPushNotification(
      token,
      '🧴 Time to reapply sunscreen',
      `UV is still ${current}. Reapply sunscreen to stay protected.`,
      'reapply'
    );
    setPrefs({ lastReapplyNotifiedAt: now });
  }
}
