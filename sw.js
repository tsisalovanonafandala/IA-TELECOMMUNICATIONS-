const CACHE = "ia-telecom-v1";
const ASSETS = ["/IA-TELECOMMUNICATIONS-/", "/IA-TELECOMMUNICATIONS-/index.html", "/IA-TELECOMMUNICATIONS-/manifest.json", "/IA-TELECOMMUNICATIONS-/icon-192.png", "/IA-TELECOMMUNICATIONS-/icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(()=>{}));
  self.skipWaiting();
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if(e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
