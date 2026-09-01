/**
 * Service Worker for Deep Learning Exam Course PWA.
 * Implements Network-First with Cache Fallback for local static assets and SWR for MathJax CDN.
 */

const CACHE_NAME = 'ai-course-v3';

const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './style.css',
  './icon.svg',
  './js/app.js',
  './js/lecture.js',
  './js/simulator.js',
  './js/tracker.js',
  './js/exam_data.js',
  './lectures/00-intro-ml.html',
  './lectures/01-fcnn.html',
  './lectures/02-autodiff-pinn.html',
  './lectures/03-losses-mle.html',
  './lectures/04-cnn-layers.html',
  './lectures/05-cnn-architectures.html',
  './lectures/06-optimizers.html',
  './lectures/07-hyperparams.html',
  './lectures/08-metric-learning.html',
  './lectures/09-contrastive-ssl.html',
  './lectures/10-vae.html',
  './lectures/11-gan.html',
  './lectures/12-diffusion.html',
  './lectures/13-cv-tasks.html',
  './lectures/14-rnn-lstm.html',
  './lectures/15-attention-seq2seq.html',
  './lectures/16-transformers.html',
  './lectures/17-self-attention.html',
  './lectures/18-lstm-vs-transformer.html',
  './lectures/19-text-word2vec.html',
  './lectures/20-mt-bleu.html',
  './lectures/21-enc-dec.html',
  './lectures/22-rl-intro.html',
  './lectures/23-bellman.html',
  './lectures/24-vi-pi-mc.html',
  './lectures/25-td-qlearning.html',
  './lectures/26-policy-gradient.html',
  './lectures/27-actor-critic.html'
];

// Install: pre-cache all core static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((err) => {
        console.warn('SW pre-cache warning:', err);
      })
  );
});

// Activate: clean up outdated cache stores and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Strategy dispatcher
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Only handle HTTP and HTTPS requests (ignore chrome-extension://, moz-extension://, etc.)
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    return;
  }

  // 1. External CDN assets (e.g. MathJax) -> Stale-While-Revalidate
  if (url.origin !== self.location.origin) {
    if (url.hostname.includes('cdnjs.cloudflare.com') || url.hostname.includes('jsdelivr')) {
      event.respondWith(
        caches.open(CACHE_NAME).then((cache) => {
          return cache.match(req).then((cachedResponse) => {
            const fetchPromise = fetch(req)
              .then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                  cache.put(req, networkResponse.clone()).catch((err) => {
                    console.warn('CDN cache.put warning:', err);
                  });
                }
                return networkResponse;
              })
              .catch(() => cachedResponse);

            return cachedResponse || fetchPromise;
          });
        })
      );
      return;
    }
    return;
  }

  // 2. Local Same-Origin assets -> Network-First with Cache Fallback
  event.respondWith(
    fetch(req)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, responseToCache).catch((err) => {
              console.warn('Local cache.put warning:', err);
            });
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Network failed or offline: fallback to cache
        return caches.match(req).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // Offline fallback for HTML navigation requests
          if (req.mode === 'navigate' || (req.headers.get('accept') && req.headers.get('accept').includes('text/html'))) {
            return caches.match('./index.html').then((indexFallback) => {
              if (indexFallback) return indexFallback;
              return caches.match('/index.html').then((rootFallback) => {
                return rootFallback || caches.match('index.html');
              });
            });
          }
        });
      })
  );
});
