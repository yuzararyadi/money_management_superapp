/* Service worker for the installed dashboard app.
   Network first: you always see the latest data when the PC is reachable;
   the last copy is shown when it isn't (e.g. no Tailscale connection).
   /api/ requests (Hermes, publish) are never cached. */
const CACHE = 'money-dash-v2';
const CORE = ['/', '/manifest.json', '/icons/icon-192.png?v=2', '/icons/icon-512.png?v=2'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok) {
        const copy = res.clone();
        const key = req.mode === 'navigate' ? '/' : req;  // one cached copy of the page, whatever the #tab
        caches.open(CACHE).then(c => c.put(key, copy));
      }
      return res;
    }).catch(() => caches.match(req.mode === 'navigate' ? '/' : req).then(r => r || caches.match('/')))
  );
});
