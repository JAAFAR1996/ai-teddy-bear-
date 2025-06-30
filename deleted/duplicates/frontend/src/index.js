import React from 'react';
import { createRoot } from 'react-dom/client';
import { StyleSheetManager } from 'styled-components';
import rtlPlugin from 'stylis-plugin-rtl';
import App from './App';

// Performance monitoring
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

// RTL configuration
const isRTL = document.documentElement.dir === 'rtl' || 
             document.documentElement.lang === 'ar' ||
             localStorage.getItem('language') === 'ar';

// Service Worker registration
const registerSW = () => {
  if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('🧸 SW registered successfully');
          
          // Handle updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker?.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // Show update notification
                showUpdateNotification();
              }
            });
          });
        })
        .catch((error) => {
          console.error('🧸 SW registration failed:', error);
        });
    });
  }
};

// Update notification
const showUpdateNotification = () => {
  const updateDiv = document.createElement('div');
  updateDiv.innerHTML = `
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
    ">
      <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 2rem;">🧸</div>
        <div>
          <div style="font-weight: bold; margin-bottom: 0.5rem;">تحديث جديد متاح!</div>
          <div style="font-size: 0.9rem; opacity: 0.9;">إصدار محسن من دب تيدي</div>
        </div>
      </div>
      <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
        <button onclick="window.location.reload()" style="
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-family: inherit;
          flex: 1;
        ">تحديث الآن</button>
        <button onclick="this.parentElement.parentElement.parentElement.remove()" style="
          background: transparent;
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-family: inherit;
        ">لاحقاً</button>
      </div>
    </div>
  `;
  document.body.appendChild(updateDiv);
  
  setTimeout(() => updateDiv.remove(), 10000);
};

// Network status tracking
const trackNetworkStatus = () => {
  const updateOnlineStatus = () => {
    const status = navigator.onLine ? 'متصل' : 'غير متصل';
    console.log(`🧸 Network status: ${status}`);
    
    if (navigator.onLine && 'serviceWorker' in navigator) {
      // Trigger background sync when back online
      navigator.serviceWorker.ready.then((registration) => {
        if ('sync' in window.ServiceWorkerRegistration.prototype) {
          registration.sync.register('background-sync').catch(console.warn);
        }
      });
    }
  };
  
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();
};

// Performance optimization - Resource hints
const addResourceHints = () => {
  const head = document.head;
  
  // DNS prefetch for external resources
  const dnsPrefetch = ['//fonts.googleapis.com', '//fonts.gstatic.com'];
  dnsPrefetch.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'dns-prefetch';
    link.href = domain;
    head.appendChild(link);
  });
  
  // Preconnect to API
  const preconnect = document.createElement('link');
  preconnect.rel = 'preconnect';
  preconnect.href = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  head.appendChild(preconnect);
};

// Initialize app
const initializeApp = () => {
  // Add resource hints
  addResourceHints();
  
  // Register service worker
  registerSW();
  
  // Track network status
  trackNetworkStatus();
  
  // Get root element
  const container = document.getElementById('root');
  if (!container) {
    console.error('🧸 Root container not found');
    return;
  }
  
  const root = createRoot(container);
  
  // Configure styled-components with RTL support
  const StyledApp = () => (
    <StyleSheetManager
      stylisPlugins={isRTL ? [rtlPlugin] : []}
      enableVendorPrefixes={true}
    >
      <App />
    </StyleSheetManager>
  );
  
  // Render app with error boundary
  root.render(
    <React.StrictMode>
      <StyledApp />
    </React.StrictMode>
  );
  
  // Performance monitoring
  reportWebVitals((metric) => {
    if (process.env.NODE_ENV === 'production') {
      console.log(`🧸 Performance metric: ${metric.name}`, metric.value);
      
      // Send to analytics service
      if (window.gtag) {
        window.gtag('event', metric.name, {
          value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
          event_category: 'Web Vitals',
          event_label: metric.id,
          non_interaction: true,
        });
      }
    }
  });
  
  console.log('🧸 AI Teddy Bear app initialized successfully');
};

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
} 