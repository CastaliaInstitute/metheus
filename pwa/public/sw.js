const CACHE_NAME = 'metheus-circle-shell-v9';
const SHELL = ['/chat/', '/chat/manifest.webmanifest', '/chat/icon.svg', '/chat/gate-ai-affordances.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))),
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || !url.pathname.startsWith('/chat/')) return;
  // Only cache the static application shell. Matrix messages, API responses, keys,
  // and session data are never written to this cache.
  if (url.pathname.includes('/_matrix/')) return;
  event.respondWith(fetch(request).then((response) => {
    if (response.ok && (url.pathname === '/chat/' || url.pathname.endsWith('.webmanifest') || url.pathname.endsWith('.svg'))) {
      const copy = response.clone();
      caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
    }
    return response;
  }).catch(() => caches.match(request)));
});
