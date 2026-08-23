const CACHE_NAME = "lofi-radio-cache-v7";
const ASSETS_TO_CACHE = [
    "/app.css",
    "/favicon.svg",
    "/favicon.png",
    "/icon-192.png",
    "/manifest.json",
    "/js/lofiPlayer.js"
];

self.addEventListener("install", event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE))
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        Promise.all([
            self.clients.claim(),
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cache => {
                        if (cache !== CACHE_NAME) {
                            return caches.delete(cache);
                        }
                    })
                );
            })
        ])
    );
});

self.addEventListener("fetch", event => {
    const url = new URL(event.request.url);
    
    // Bypass Service Worker completely for media streams, API endpoints, and GCS signed URL files
    // to allow native browser HTTP Range Requests and correct OS media session controls (play/pause/volume) inside the PWA!
    if (url.pathname.includes("/api/stream/") || url.pathname.endsWith(".mp3") || url.host.includes("googleapis.com")) {
        return; // Letting the browser handle the fetch natively with full range support
    }

    event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
    );
});
