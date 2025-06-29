import axios from 'axios';
import toast from 'react-hot-toast';

// Base API configuration
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}:`, response.status);
    }
    return response;
  },
  (error) => {
    const { response, request, config } = error;
    
    // Network error
    if (!response) {
      toast.error('خطأ في الاتصال بالشبكة. تأكد من اتصال الإنترنت.');
      console.error('Network error:', error.message);
      return Promise.reject(new Error('NETWORK_ERROR'));
    }
    
    // HTTP errors
    const status = response.status;
    const errorMessage = response.data?.message || response.data?.error || 'حدث خطأ غير متوقع';
    
    switch (status) {
      case 401:
        toast.error('انتهت صلاحية جلسة المستخدم. يرجى تسجيل الدخول مرة أخرى.');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        break;
        
      case 403:
        toast.error('غير مسموح لك بالوصول إلى هذه البيانات.');
        break;
        
      case 404:
        toast.error('البيانات المطلوبة غير موجودة.');
        break;
        
      case 422:
        toast.error('بيانات غير صحيحة. يرجى مراجعة المدخلات.');
        break;
        
      case 429:
        toast.error('تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.');
        break;
        
      case 500:
        toast.error('خطأ داخلي في الخادم. يرجى المحاولة لاحقاً.');
        break;
        
      default:
        toast.error(errorMessage);
    }
    
    // Log error details
    console.error(`❌ ${config?.method?.toUpperCase()} ${config?.url}:`, {
      status,
      message: errorMessage,
      data: response.data
    });
    
    return Promise.reject(error);
  }
);

// ===== AUTHENTICATION API =====
export const authAPI = {
  // Login parent
  login: async (credentials) => {
    const { data } = await api.post('/auth/login', credentials);
    
    // Store auth data
    if (data.token) {
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('userData', JSON.stringify(data.user));
    }
    
    return data;
  },
  
  // Register new parent
  register: async (userData) => {
    const { data } = await api.post('/auth/register', userData);
    return data;
  },
  
  // Logout
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    }
  },
  
  // Get current user info
  getCurrentUser: async () => {
    const { data } = await api.get('/auth/me');
    return data;
  },
  
  // Refresh token
  refreshToken: async () => {
    const { data } = await api.post('/auth/refresh');
    localStorage.setItem('authToken', data.token);
    return data;
  }
};

// ===== DASHBOARD API =====
export const dashboardAPI = {
  // Get dashboard data for specific child
  getDashboard: async (childId) => {
    const { data } = await api.get(`/dashboard/${childId}`);
    return data;
  },
  
  // Get all children for parent
  getChildren: async () => {
    const { data } = await api.get('/dashboard/children');
    return data;
  },
  
  // Export child data
  exportData: async (childId, format = 'json') => {
    const { data } = await api.post(`/dashboard/${childId}/export`, { format });
    return data;
  },
  
  // Get dashboard summary
  getSummary: async () => {
    const { data } = await api.get('/dashboard/summary');
    return data;
  }
};

// ===== CHILD MANAGEMENT API =====
export const childAPI = {
  // Get child details
  getChild: async (childId) => {
    const { data } = await api.get(`/children/${childId}`);
    return data;
  },
  
  // Update child information
  updateChild: async (childId, updates) => {
    const { data } = await api.put(`/children/${childId}`, updates);
    return data;
  },
  
  // Delete child (and all associated data)
  deleteChild: async (childId) => {
    const { data } = await api.delete(`/children/${childId}`);
    return data;
  },
  
  // Get child's conversation history
  getConversations: async (childId, page = 1, limit = 20) => {
    const { data } = await api.get(`/children/${childId}/conversations`, {
      params: { page, limit }
    });
    return data;
  },
  
  // Get child's emotional analysis
  getEmotionAnalysis: async (childId, dateRange = '7d') => {
    const { data } = await api.get(`/children/${childId}/emotions`, {
      params: { range: dateRange }
    });
    return data;
  }
};

// ===== NOTIFICATIONS API =====
export const notificationAPI = {
  // Get notifications for parent
  getNotifications: async (page = 1, limit = 10) => {
    const { data } = await api.get('/notifications', {
      params: { page, limit }
    });
    return data;
  },
  
  // Mark notification as read
  markAsRead: async (notificationId) => {
    const { data } = await api.put(`/notifications/${notificationId}/read`);
    return data;
  },
  
  // Mark all notifications as read
  markAllAsRead: async () => {
    const { data } = await api.put('/notifications/read-all');
    return data;
  },
  
  // Get notification preferences
  getPreferences: async () => {
    const { data } = await api.get('/notifications/preferences');
    return data;
  },
  
  // Update notification preferences
  updatePreferences: async (preferences) => {
    const { data } = await api.put('/notifications/preferences', preferences);
    return data;
  },
  
  // Subscribe to push notifications
  subscribePush: async (subscription) => {
    const { data } = await api.post('/notifications/push/subscribe', subscription);
    return data;
  }
};

// ===== ADMIN API =====
export const adminAPI = {
  // Trigger manual notification
  triggerNotification: async (payload) => {
    const { data } = await api.post('/admin/notifications/trigger', payload);
    return data;
  },
  
  // Get system health
  getSystemHealth: async () => {
    const { data } = await api.get('/health');
    return data;
  },
  
  // Get rate monitor stats
  getRateStats: async () => {
    const { data } = await api.get('/admin/rate-monitor/stats');
    return data;
  },
  
  // Get issue tracker stats
  getIssueStats: async () => {
    const { data } = await api.get('/admin/issues/stats');
    return data;
  },
  
  // Get scheduler status
  getSchedulerStatus: async () => {
    const { data } = await api.get('/admin/scheduler/status');
    return data;
  }
};

// ===== ANALYTICS API =====
export const analyticsAPI = {
  // Get usage analytics
  getUsageStats: async (childId, period = '30d') => {
    const { data } = await api.get(`/analytics/usage/${childId}`, {
      params: { period }
    });
    return data;
  },
  
  // Get emotional trends
  getEmotionTrends: async (childId, period = '30d') => {
    const { data } = await api.get(`/analytics/emotions/${childId}`, {
      params: { period }
    });
    return data;
  },
  
  // Get interaction patterns
  getInteractionPatterns: async (childId) => {
    const { data } = await api.get(`/analytics/interactions/${childId}`);
    return data;
  }
};

// ===== UTILITY FUNCTIONS =====
export const apiUtils = {
  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('authToken');
    return !!token;
  },
  
  // Get stored user data
  getUserData: () => {
    const userData = localStorage.getItem('userData');
    return userData ? JSON.parse(userData) : null;
  },
  
  // Clear auth data
  clearAuthData: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
  },
  
  // Format API error for display
  formatError: (error) => {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message === 'NETWORK_ERROR') {
      return 'خطأ في الاتصال بالشبكة';
    }
    return 'حدث خطأ غير متوقع';
  }
};

// Export default api instance for custom requests
export default api;

// Legacy exports (for backward compatibility)
export const fetchDashboard = dashboardAPI.getDashboard;
export const exportData = dashboardAPI.exportData; 