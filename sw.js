const CACHE = "predibol-v4";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./assets/icon.svg", "./preguntas_extra.json", "./noticias.json"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)));
  self.skipWaiting();
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))));
  self.clients.claim();
});
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  const isBank = url.pathname.endsWith("/preguntas_extra.json") || url.pathname === "/preguntas_extra.json";
  const isNews = url.pathname.endsWith("/noticias.json") || url.pathname === "/noticias.json";
  if (isBank || isNews) {
    const cacheKey = isBank ? "./preguntas_extra.json" : "./noticias.json";
    event.respondWith(fetch(event.request).then(async response => {
      if (response.ok) {
        await caches.open(CACHE).then(cache => cache.put(cacheKey, response.clone()));
      }
      return response;
    }).catch(async () => {
      const cached = await caches.match(cacheKey);
      return cached || new Response(JSON.stringify(isBank ? [] : {items:[],updated:null}), {
        headers: {"Content-Type":"application/json"}
      });
    }));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok) caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  }).catch(() => caches.match("./index.html"))));
});
