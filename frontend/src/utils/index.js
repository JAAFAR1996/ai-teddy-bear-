/**
 * Utility Functions for AI Teddy Bear Frontend
 * Collection of reusable helper functions for common operations
 */

// Date and Time Utilities
export const formatDate = (date, locale = 'ar-SA') => {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  return dateObj.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatTime = (date, locale = 'ar-SA') => {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  return dateObj.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDateTime = (date, locale = 'ar-SA') => {
  return `${formatDate(date, locale)} ${formatTime(date, locale)}`;
};

export const getRelativeTime = (date, locale = 'ar-SA') => {
  if (!date) return '';
  
  const now = new Date();
  const dateObj = date instanceof Date ? date : new Date(date);
  const diffInSeconds = Math.floor((now - dateObj) / 1000);
  
  if (diffInSeconds < 60) {
    return locale === 'ar-SA' ? 'الآن' : 'now';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return locale === 'ar-SA' 
      ? `منذ ${diffInMinutes} ${diffInMinutes === 1 ? 'دقيقة' : 'دقائق'}`
      : `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return locale === 'ar-SA' 
      ? `منذ ${diffInHours} ${diffInHours === 1 ? 'ساعة' : 'ساعات'}`
      : `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  return locale === 'ar-SA' 
    ? `منذ ${diffInDays} ${diffInDays === 1 ? 'يوم' : 'أيام'}`
    : `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
};

// Audio and Media Utilities
export const formatDuration = (seconds) => {
  if (!seconds || seconds < 0) return '0:00';
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const isAudioSupported = (format) => {
  const audio = document.createElement('audio');
  return audio.canPlayType(`audio/${format}`) !== '';
};

export const getMimeType = (extension) => {
  const mimeTypes = {
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'ogg': 'audio/ogg',
    'webm': 'audio/webm',
    'm4a': 'audio/mp4'
  };
  return mimeTypes[extension.toLowerCase()] || 'audio/mpeg';
};

// Data Validation
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhoneNumber = (phone) => {
  // Support both Arabic and international formats
  const phoneRegex = /^[\+]?[0-9\-\(\)\s]{7,20}$/;
  return phoneRegex.test(phone);
};

export const validateChildAge = (age) => {
  const ageNum = parseInt(age);
  return ageNum >= 2 && ageNum <= 12;
};

export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return '';
  return input.trim().replace(/[<>]/g, '');
};

// Storage Utilities
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error getting from localStorage:', error);
      return defaultValue;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error setting to localStorage:', error);
      return false;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      return false;
    }
  }
};

// Network and API Utilities
export const isOnline = () => navigator.onLine;

export const detectNetworkSpeed = () => {
  return new Promise((resolve) => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      const speed = connection.effectiveType;
      resolve(speed);
    } else {
      // Fallback: simple speed test
      const startTime = performance.now();
      fetch('/manifest.json', { cache: 'no-store' })
        .then(() => {
          const endTime = performance.now();
          const duration = endTime - startTime;
          const speed = duration < 100 ? 'fast' : duration < 300 ? 'medium' : 'slow';
          resolve(speed);
        })
        .catch(() => resolve('unknown'));
    }
  });
};

export const retryOperation = async (operation, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

// UI Utilities
export const generateUniqueId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return true;
  }
};

export const downloadData = (data, filename, type = 'application/json') => {
  const blob = new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// Color and Theme Utilities
export const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

export const rgbToHex = (r, g, b) => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};

export const lightenColor = (hex, percent) => {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  const factor = (100 + percent) / 100;
  return rgbToHex(
    Math.min(255, Math.round(rgb.r * factor)),
    Math.min(255, Math.round(rgb.g * factor)),
    Math.min(255, Math.round(rgb.b * factor))
  );
};

export const darkenColor = (hex, percent) => {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  const factor = (100 - percent) / 100;
  return rgbToHex(
    Math.round(rgb.r * factor),
    Math.round(rgb.g * factor),
    Math.round(rgb.b * factor)
  );
};

// Performance Utilities
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Device and Browser Detection
export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

export const isIOS = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
};

export const isAndroid = () => {
  return /Android/.test(navigator.userAgent);
};

export const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  let browser = 'Unknown';
  
  if (ua.indexOf('Chrome') > -1) browser = 'Chrome';
  else if (ua.indexOf('Firefox') > -1) browser = 'Firefox';
  else if (ua.indexOf('Safari') > -1) browser = 'Safari';
  else if (ua.indexOf('Edge') > -1) browser = 'Edge';
  
  return {
    name: browser,
    userAgent: ua,
    language: navigator.language,
    platform: navigator.platform
  };
};

// Analytics and Tracking
export const trackEvent = (eventName, properties = {}) => {
  // This would integrate with your analytics service
  console.log('📊 Event tracked:', eventName, properties);
  
  // Example: Send to analytics service
  if (window.gtag) {
    window.gtag('event', eventName, properties);
  }
};

export const trackPageView = (pageName) => {
  trackEvent('page_view', { page: pageName });
};

export const trackUserInteraction = (action, element) => {
  trackEvent('user_interaction', { action, element });
};

// Error Handling
export const reportError = (error, context = {}) => {
  console.error('🚨 Error reported:', error, context);
  
  // In production, you would send this to an error tracking service
  // Example: Sentry, LogRocket, etc.
  
  return {
    timestamp: new Date().toISOString(),
    error: error.message || error,
    stack: error.stack,
    context
  };
};

// Constants
export const EMOTION_COLORS = {
  happiness: '#FFD700',
  sadness: '#4169E1',
  anger: '#DC143C',
  fear: '#8A2BE2',
  surprise: '#FF6347',
  neutral: '#808080'
};

export const CHILD_AGE_GROUPS = {
  toddler: { min: 2, max: 3, label: 'طفل صغير' },
  preschool: { min: 4, max: 5, label: 'ما قبل المدرسة' },
  early_elementary: { min: 6, max: 8, label: 'المرحلة الابتدائية المبكرة' },
  late_elementary: { min: 9, max: 12, label: 'المرحلة الابتدائية المتأخرة' }
};

export const DEFAULT_SETTINGS = {
  language: 'ar-SA',
  theme: 'light',
  soundEnabled: true,
  notificationsEnabled: true,
  autoPlayResponses: true,
  parentalControlsEnabled: true
}; 