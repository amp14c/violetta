import { getToken } from 'firebase/messaging';
import { getFirebaseMessaging } from './firebase';
import { setPrefs } from './storage';

const VAPID_KEY = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY;

export async function requestNotificationPermission(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return null;

  const messaging = getFirebaseMessaging();
  if (!messaging) return null;

  try {
    const token = await getToken(messaging, { vapidKey: VAPID_KEY });
    if (token) {
      localStorage.setItem('violetta_fcm_token', token);
      setPrefs({ notificationsEnabled: true });
    }
    return token;
  } catch (err) {
    console.error('FCM token error:', err);
    return null;
  }
}

export function getFCMToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('violetta_fcm_token');
}

export async function sendPushNotification(
  token: string,
  title: string,
  body: string,
  tag?: string
): Promise<void> {
  await fetch('/api/notify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, title, body, tag }),
  });
}
