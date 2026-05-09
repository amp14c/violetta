import { NextRequest, NextResponse } from 'next/server';
import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getMessaging } from 'firebase-admin/messaging';

function getAdminApp() {
  if (getApps().length) return getApps()[0];
  return initializeApp({
    credential: cert({
      projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
      clientEmail: process.env.FIREBASE_ADMIN_CLIENT_EMAIL,
      // Vercel stores the private key with literal \n — replace them
      privateKey: process.env.FIREBASE_ADMIN_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    }),
  });
}

export async function POST(req: NextRequest) {
  const { token, title, body, tag } = await req.json();
  if (!token || !title) {
    return NextResponse.json({ error: 'token and title required' }, { status: 400 });
  }

  try {
    getAdminApp();
    await getMessaging().send({
      token,
      webpush: {
        notification: {
          title,
          body: body ?? '',
          icon: '/icons/icon-192.png',
          badge: '/icons/icon-192.png',
          tag: tag ?? 'violetta',
        },
        fcmOptions: { link: '/' },
      },
    });
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error('FCM send error:', err);
    return NextResponse.json({ error: 'Failed to send notification' }, { status: 500 });
  }
}
