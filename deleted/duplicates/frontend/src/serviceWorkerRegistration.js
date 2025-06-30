// Service Worker Registration for AI Teddy Bear
// Advanced PWA functionality with background sync and notifications

const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
  window.location.hostname === '[::1]' ||
  window.location.hostname.match(
    /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
  )
);

export function register(config) {
  if ('serviceWorker' in navigator) {
    const publicUrl = new URL(process.env.PUBLIC_URL, window.location.href);
    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    window.addEventListener('load', () => {
      const swUrl = `${process.env.PUBLIC_URL}/sw.js`;

      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);
      } else {
        registerValidSW(swUrl, config);
      }
    });
  }
}

function registerValidSW(swUrl, config) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      console.log('🧸 SW registered successfully');
      
      if (config && config.onSuccess) {
        config.onSuccess(registration);
      }
    })
    .catch((error) => {
      console.error('🧸 SW registration failed:', error);
    });
}

function checkValidServiceWorker(swUrl, config) {
  fetch(swUrl, { headers: { 'Service-Worker': 'script' } })
    .then((response) => {
      const contentType = response.headers.get('content-type');
      if (response.status === 404 || (contentType != null && contentType.indexOf('javascript') === -1)) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload();
          });
        });
      } else {
        registerValidSW(swUrl, config);
      }
    })
    .catch(() => {
      console.log('🧸 No internet connection found. Running in offline mode.');
    });
}

function showUpdateNotification(registration) {
  // Create custom update notification
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      z-index: 10000;
      font-family: 'Tajawal', sans-serif;
      direction: rtl;
      max-width: 350px;
      animation: slideIn 0.3s ease-out;
    ">
      <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 2rem;">🧸</div>
        <div>
          <div style="font-weight: bold; margin-bottom: 0.5rem;">
            تحديث جديد متاح!
          </div>
          <div style="font-size: 0.9rem; opacity: 0.9;">
            إصدار محسن من دب تيدي جاهز للتثبيت
          </div>
        </div>
      </div>
      <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
        <button onclick="updateApp()" style="
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-family: inherit;
          flex: 1;
        ">
          تحديث الآن
        </button>
        <button onclick="this.parentElement.parentElement.parentElement.remove()" style="
          background: transparent;
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-family: inherit;
        ">
          لاحقاً
        </button>
      </div>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 10000);
  
  // Global update function
  window.updateApp = () => {
    registration.waiting?.postMessage({ type: 'SKIP_WAITING' });
    window.location.reload();
  };
}

function setupBackgroundSync(registration) {
  if ('sync' in window.ServiceWorkerRegistration.prototype) {
    console.log('🧸 Teddy Bear: Background Sync supported');
    
    // Register for background sync when offline
    window.addEventListener('offline', () => {
      console.log('🧸 Teddy Bear: Gone offline, registering background sync');
      registration.sync.register('background-sync');
    });
    
    // Listen for failed API requests to retry later
    window.addEventListener('beforeunload', () => {
      if (!navigator.onLine) {
        registration.sync.register('background-sync');
      }
    });
  }
}

function setupPushNotifications(registration) {
  if ('PushManager' in window) {
    console.log('🧸 Teddy Bear: Push notifications supported');
    
    // Request permission for notifications
    if (Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        console.log('🧸 Teddy Bear: Notification permission:', permission);
        
        if (permission === 'granted') {
          subscribeToPush(registration);
        }
      });
    } else if (Notification.permission === 'granted') {
      subscribeToPush(registration);
    }
  }
}

async function subscribeToPush(registration) {
  try {
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        // VAPID public key - replace with your actual key
        'BEl62iUYgUivxIkv69yViEuiBIa40HI80j4Vhv00dsw4-5FrKhI9C8_E7qzI7J_ZTgAcXhTkSI7bDgjPcBdHjWw'
      )
    });
    
    console.log('🧸 Teddy Bear: Push subscription successful');
    
    // Send subscription to server
    await fetch('/api/notifications/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subscription)
    });
    
  } catch (error) {
    console.warn('🧸 Teddy Bear: Push subscription failed:', error);
  }
}

function setupPeriodicSync(registration) {
  if ('periodicSync' in window.ServiceWorkerRegistration.prototype) {
    console.log('🧸 Teddy Bear: Periodic Background Sync supported');
    
    // Register periodic sync for data updates
    registration.periodicSync.register('periodic-background-sync', {
      minInterval: 24 * 60 * 60 * 1000, // 24 hours
    }).then(() => {
      console.log('🧸 Teddy Bear: Periodic sync registered');
    }).catch((error) => {
      console.log('🧸 Teddy Bear: Periodic sync registration failed:', error);
    });
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
      })
      .catch((error) => {
        console.error(error.message);
      });
  }
}

// Network status tracking
export function trackNetworkStatus() {
  let isOnline = navigator.onLine;
  
  const updateOnlineStatus = () => {
    const wasOnline = isOnline;
    isOnline = navigator.onLine;
    
    if (!wasOnline && isOnline) {
      console.log('🧸 Teddy Bear: Back online - syncing data');
      // Trigger sync when back online
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.sync.register('background-sync');
        });
      }
    }
  };
  
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  return () => {
    window.removeEventListener('online', updateOnlineStatus);
    window.removeEventListener('offline', updateOnlineStatus);
  };
} 