importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

// Config is safe to include here — Firebase client config is public by design
firebase.initializeApp({
  apiKey: 'AIzaSyDiKIMszTeuKRU98OdZYn4OmpV29yKOX-8',
  authDomain: 'violetta-901df.firebaseapp.com',
  projectId: 'violetta-901df',
  storageBucket: 'violetta-901df.firebasestorage.app',
  messagingSenderId: '435688869568',
  appId: '1:435688869568:web:f8474a7f8b1ec1dceda725',
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const { title, body } = payload.notification ?? {};
  self.registration.showNotification(title ?? 'Violetta', {
    body: body ?? '',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    tag: payload.data?.tag ?? 'violetta',
  });
});
