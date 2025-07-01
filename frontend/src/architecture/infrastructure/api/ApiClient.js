/**
 * API Client
 * 
 * Centralized HTTP client for backend communication
 */

import axios from 'axios';

export class ApiClient {
  constructor({ baseURL, timeout = 10000, retryAttempts = 3 }) {
    this.baseURL = baseURL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';
    this.timeout = timeout;
    this.retryAttempts = retryAttempts;
    
    this.client = this.createAxiosInstance();
    this.setupInterceptors();
  }

  createAxiosInstance() {
    return axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
  }

  setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response.data;
      },
      async (error) => {
        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error);
        
        // Handle specific error cases
        if (error.response?.status === 401) {
          await this.handleUnauthorized();
        }

        // Retry logic for network errors
        if (this.shouldRetry(error) && error.config && !error.config.__retryCount) {
          return this.retryRequest(error);
        }

        throw this.formatError(error);
      }
    );
  }

  // HTTP Methods
  async get(url, config = {}) {
    return this.client.get(url, config);
  }

  async post(url, data, config = {}) {
    return this.client.post(url, data, config);
  }

  async put(url, data, config = {}) {
    return this.client.put(url, data, config);
  }

  async patch(url, data, config = {}) {
    return this.client.patch(url, data, config);
  }

  async delete(url, config = {}) {
    return this.client.delete(url, config);
  }

  // Specialized methods
  async uploadFile(url, file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      }
    });
  }

  async downloadFile(url, filename) {
    const response = await this.client.get(url, {
      responseType: 'blob'
    });

    // Create download link
    const blob = new Blob([response], { type: response.type });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    return response;
  }

  // Authentication
  getAuthToken() {
    return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
  }

  setAuthToken(token, persistent = false) {
    if (persistent) {
      localStorage.setItem('auth_token', token);
    } else {
      sessionStorage.setItem('auth_token', token);
    }
  }

  clearAuthToken() {
    localStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_token');
  }

  async handleUnauthorized() {
    console.warn('🔐 Unauthorized access - clearing auth token');
    this.clearAuthToken();
    
    // Emit event for app to handle (redirect to login, etc.)
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
  }

  // Retry Logic
  shouldRetry(error) {
    // Only retry on network errors or 5xx server errors
    return !error.response || (error.response.status >= 500 && error.response.status < 600);
  }

  async retryRequest(error) {
    const config = error.config;
    config.__retryCount = config.__retryCount || 0;

    if (config.__retryCount >= this.retryAttempts) {
      throw error;
    }

    config.__retryCount++;
    
    // Exponential backoff
    const delay = Math.pow(2, config.__retryCount) * 1000;
    console.log(`🔄 Retrying request (${config.__retryCount}/${this.retryAttempts}) in ${delay}ms`);
    
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return this.client(config);
  }

  // Error Formatting
  formatError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        type: 'API_ERROR',
        status: error.response.status,
        message: error.response.data?.message || error.message,
        data: error.response.data,
        url: error.config?.url
      };
    } else if (error.request) {
      // Network error
      return {
        type: 'NETWORK_ERROR',
        message: 'Network connection failed',
        url: error.config?.url
      };
    } else {
      // Request setup error
      return {
        type: 'REQUEST_ERROR',
        message: error.message
      };
    }
  }

  // Utilities
  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Health Check
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return { status: 'healthy', ...response };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
} 