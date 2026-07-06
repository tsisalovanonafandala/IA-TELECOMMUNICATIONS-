/* ══════════════════════════════════════════════════════════
   SERVICE WORKER — IA Télécommunication
   Rend l'application réellement installable et utilisable hors-ligne.
   ══════════════════════════════════════════════════════════ */

// ⚠️ Change ce numéro à chaque mise à jour importante pour forcer
// tous les téléphones à récupérer la nouvelle version rapidement.
const CACHE = "ia-telecom-v2";

const ASSETS = [
  "/IA-TELECOMMUNICATIONS-/",
  "/IA-TELECOMMUNICATIONS-/index.html",
  "/IA-TELECOMMUNICATIONS-/manifest.json",
  "/IA-TELECOMMUNICATIONS-/icon-192.png",
  "/IA-TELECOMMUNICATIONS-/icon-512.png"
];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then((c) =>
      // Chaque fichier est mis en cache indépendamment : si l'un d'eux est
      // absent du dépôt, les autres sont quand même mis en cache normalement.
      Promise.all(ASSETS.map((url) => c.add(url).catch(() => {})))
    )
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  // On ne gère jamais les requêtes vers d'autres domaines (Groq, Firebase,
  // Gemini, CDN...) : elles passent directement au réseau, sans interception.
  if (url.origin !== self.location.origin) return;

  const isPage = req.mode === "navigate" || url.pathname.endsWith("index.html") || url.pathname.endsWith("/");

  if (isPage){
    // Page principale : réseau en priorité (toujours la dernière version),
    // avec repli automatique sur le cache si hors-ligne.
    e.respondWith(
      fetch(req)
        .then((res) => {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(req, clone));
          return res;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match("/IA-TELECOMMUNICATIONS-/index.html")))
    );
    return;
  }

  // Fichiers statiques (manifest, icônes) : cache en priorité pour un
  // chargement instantané, avec mise à jour silencieuse en arrière-plan.
  e.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req).then((res) => {
        const clone = res.clone();
        caches.open(CACHE).then((c) => c.put(req, clone));
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
