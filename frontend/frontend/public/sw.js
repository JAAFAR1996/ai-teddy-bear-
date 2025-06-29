// AI Teddy Bear - Service Worker for PWA
// Advanced caching strategies for optimal offline experience

const CACHE_NAME = 'ai-teddy-v2.0.0';
const RUNTIME_CACHE = 'runtime-cache-v2.0.0';
const API_CACHE = 'api-cache-v2.0.0';

// Resources to cache on install
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/offline.html',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap'
];

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Install event - cache essential resources
self.addEventListener('install', (event) => {
  console.log('🧸 Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('🧸 Service Worker: Caching app shell');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => {
        console.log('🧸 Service Worker: Installation complete');
        self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🧸 Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE && cacheName !== API_CACHE) {
            console.log('🧸 Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('🧸 Service Worker: Activation complete');
      self.clients.claim();
    })
  );
});

// Fetch event - handle requests with different strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-HTTP requests
  if (!request.url.startsWith('http')) {
    return;
  }

  // API requests - Network First strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      networkFirstStrategy(request, API_CACHE)
    );
    return;
  }

  // App shell - Cache First strategy
  if (PRECACHE_URLS.includes(url.pathname) || url.pathname === '/') {
    event.respondWith(
      cacheFirstStrategy(request, CACHE_NAME)
    );
    return;
  }

  // Images and media - Stale While Revalidate
  if (request.destination === 'image' || request.destination === 'audio') {
    event.respondWith(
      staleWhileRevalidateStrategy(request, RUNTIME_CACHE)
    );
    return;
  }

  // Other resources - Network First with fallback
  event.respondWith(
    networkFirstWithFallback(request)
  );
});

// Cache First Strategy
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error('🧸 Cache First Strategy failed:', error);
    return await caches.match('/offline.html');
  }
}

// Network First Strategy
async function networkFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    
    try {
      const networkResponse = await fetch(request);
      
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      
      return networkResponse;
    } catch (networkError) {
      const cachedResponse = await cache.match(request);
      
      if (cachedResponse) {
        return cachedResponse;
      }
      
      throw networkError;
    }
  } catch (error) {
    console.error('🧸 Network First Strategy failed:', error);
    
    // Return a custom offline response for API calls
    return new Response(
      JSON.stringify({ 
        error: 'Network unavailable', 
        message: 'Unable to fetch data. Please check your connection.' 
      }),
      { 
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidateStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    // Fetch and update cache in background
    const fetchPromise = fetch(request).then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    });
    
    // Return cached version immediately if available, otherwise wait for network
    return cachedResponse || await fetchPromise;
  } catch (error) {
    console.error('🧸 Stale While Revalidate Strategy failed:', error);
    const cache = await caches.open(cacheName);
    return await cache.match(request);
  }
}

// Network First with Offline Fallback
async function networkFirstWithFallback(request) {
  try {
    const cache = await caches.open(RUNTIME_CACHE);
    
    try {
      const networkResponse = await fetch(request);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    } catch (networkError) {
      const cachedResponse = await cache.match(request);
      
      if (cachedResponse) {
        return cachedResponse;
      }
      
      // Return offline page for navigation requests
      if (request.mode === 'navigate') {
        return await caches.match('/offline.html');
      }
      
      throw networkError;
    }
  } catch (error) {
    console.error('🧸 Network First with Fallback failed:', error);
    return await caches.match('/offline.html');
  }
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('🧸 Service Worker: Background sync triggered');
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Handle background synchronization logic here
  console.log('🧸 Service Worker: Performing background sync');
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('🧸 Service Worker: Push received');
  
  const options = {
    body: event.data ? event.data.text() : 'إشعار جديد من دبدوب الذكي',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    dir: 'rtl',
    lang: 'ar',
    actions: [
      {
        action: 'open',
        title: 'فتح التطبيق',
        icon: '/icons/action-open.png'
      },
      {
        action: 'close',
        title: 'إغلاق',
        icon: '/icons/action-close.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('AI Teddy Bear', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Error handling
self.addEventListener('error', (event) => {
  console.error('🧸 Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('🧸 Service Worker unhandled rejection:', event.reason);
  event.preventDefault();
});

console.log('🧸 Service Worker: Loaded successfully'); 