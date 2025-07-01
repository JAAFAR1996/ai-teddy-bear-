import { AxiosRequestConfig } from 'axios';

/**
 * API Service Interface
 * Defines the contract for all API service implementations
 */
export interface IApiService {
  // Authentication
  setAuthToken(token: string): void;
  
  // Generic HTTP methods
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  
  // Domain-specific methods
  getChildProfile(childId: string): Promise<any>;
  updateChildProfile(childId: string, data: any): Promise<any>;
  getConversations(childId: string, params?: any): Promise<any>;
  getEmotionAnalytics(childId: string, period: string): Promise<any>;
  getEmergencyAlerts(childId: string): Promise<any>;
  uploadAudio(audioBlob: Blob, metadata: any): Promise<any>;
} 