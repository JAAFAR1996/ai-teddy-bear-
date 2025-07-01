import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { IApiService } from '../architecture/application/interfaces/IApiService';

// API configuration
const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// Response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/**
 * API Service Implementation
 * Follows Clean Architecture principles with proper error handling
 */
export class ApiService implements IApiService {
  private axios: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.axios = axios.create(API_CONFIG);
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axios.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle token refresh or logout
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  private handleUnauthorized(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  }

  // Generic HTTP methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axios.get<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axios.post<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axios.put<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axios.delete<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  // Domain-specific methods
  async getChildProfile(childId: string) {
    return this.get(`/api/children/${childId}`);
  }

  async updateChildProfile(childId: string, data: any) {
    return this.put(`/api/children/${childId}`, data);
  }

  async getConversations(childId: string, params?: any) {
    return this.get(`/api/conversations`, { params: { childId, ...params } });
  }

  async getEmotionAnalytics(childId: string, period: string) {
    return this.get(`/api/analytics/emotions`, { params: { childId, period } });
  }

  async getEmergencyAlerts(childId: string) {
    return this.get(`/api/alerts/emergency`, { params: { childId } });
  }

  async uploadAudio(audioBlob: Blob, metadata: any) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('metadata', JSON.stringify(metadata));
    
    return this.post('/api/audio/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService; 