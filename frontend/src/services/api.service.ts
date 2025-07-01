/**
 * API Service for AI Teddy Bear
 * Enterprise-grade HTTP client with interceptors
 */

import { ApiResponse, ApiError, PaginatedResponse } from '@types';

export interface RequestConfig extends RequestInit {
  params?: Record<string, any>;
  timeout?: number;
  retry?: number;
  skipAuth?: boolean;
}

export interface Interceptor {
  request?: (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
  response?: (response: Response) => Response | Promise<Response>;
  error?: (error: Error) => Error | Promise<Error>;
}

class ApiService {
  private baseURL: string;
  private defaultTimeout = 30000;
  private interceptors: Interceptor[] = [];
  private authToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null): void {
    this.authToken = token;
  }

  /**
   * Add interceptor
   */
  addInterceptor(interceptor: Interceptor): () => void {
    this.interceptors.push(interceptor);
    return () => {
      const index = this.interceptors.indexOf(interceptor);
      if (index > -1) {
        this.interceptors.splice(index, 1);
      }
    };
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, { ...config });
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, {
      ...config,
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, {
      ...config,
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', endpoint, {
      ...config,
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint, { ...config });
  }

  /**
   * Get paginated data
   */
  async getPaginated<T = any>(
    endpoint: string,
    page = 1,
    pageSize = 20,
    config?: RequestConfig
  ): Promise<PaginatedResponse<T>> {
    const response = await this.get<PaginatedResponse<T>>(endpoint, {
      ...config,
      params: {
        ...config?.params,
        page,
        pageSize,
      },
    });

    if (!response.success || !response.data) {
      throw new Error('Failed to fetch paginated data');
    }

    return response.data;
  }

  /**
   * Upload file
   */
  async uploadFile(
    endpoint: string,
    file: File,
    additionalData?: Record<string, any>,
    config?: RequestConfig
  ): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);

    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.request('POST', endpoint, {
      ...config,
      body: formData,
      headers: {
        ...config?.headers,
        // Don't set Content-Type, let browser set it with boundary
      },
    });
  }

  /**
   * Main request method
   */
  private async request<T = any>(
    method: string,
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    let requestConfig: RequestConfig = {
      method,
      ...config,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    };

    // Add auth token if available and not skipped
    if (this.authToken && !config.skipAuth) {
      requestConfig.headers = {
        ...requestConfig.headers,
        Authorization: `Bearer ${this.authToken}`,
      };
    }

    // Build URL with params
    const url = this.buildURL(endpoint, config.params);

    // Apply request interceptors
    for (const interceptor of this.interceptors) {
      if (interceptor.request) {
        requestConfig = await interceptor.request(requestConfig);
      }
    }

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeout = setTimeout(
      () => controller.abort(),
      config.timeout || this.defaultTimeout
    );

    requestConfig.signal = controller.signal;

    try {
      let response = await fetch(url, requestConfig);
      clearTimeout(timeout);

      // Apply response interceptors
      for (const interceptor of this.interceptors) {
        if (interceptor.response) {
          response = await interceptor.response(response);
        }
      }

      // Handle response
      if (response.ok) {
        const data = await this.parseResponse<T>(response);
        return {
          success: true,
          data,
          metadata: {
            timestamp: new Date(),
            requestId: response.headers.get('X-Request-Id') || '',
          },
        };
      } else {
        // Handle error response
        const errorData = await this.parseResponse<any>(response);
        const error: ApiError = {
          code: errorData?.code || response.status.toString(),
          message: errorData?.message || response.statusText,
          details: errorData?.details,
        };

        return {
          success: false,
          error,
          metadata: {
            timestamp: new Date(),
            requestId: response.headers.get('X-Request-Id') || '',
          },
        };
      }
    } catch (error: any) {
      clearTimeout(timeout);

      // Apply error interceptors
      let processedError = error;
      for (const interceptor of this.interceptors) {
        if (interceptor.error) {
          processedError = await interceptor.error(processedError);
        }
      }

      // Handle network errors
      if (processedError.name === 'AbortError') {
        return {
          success: false,
          error: {
            code: 'TIMEOUT',
            message: 'Request timeout',
          },
        };
      }

      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: processedError.message || 'Network error occurred',
        },
      };
    }
  }

  /**
   * Build URL with query parameters
   */
  private buildURL(endpoint: string, params?: Record<string, any>): string {
    const url = `${this.baseURL}${endpoint}`;
    
    if (!params) return url;

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `${url}?${queryString}` : url;
  }

  /**
   * Parse response based on content type
   */
  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      return response.json();
    } else if (contentType?.includes('text/')) {
      return response.text() as any;
    } else {
      return response.blob() as any;
    }
  }
}

// Create default instance
const apiService = new ApiService(
  (window as any).REACT_APP_API_URL || 'http://localhost:8000/api'
);

// Add default interceptors
apiService.addInterceptor({
  request: (config) => {
    // Add timestamp to requests
    if (!config.headers) config.headers = {};
    (config.headers as any)['X-Request-Time'] = new Date().toISOString();
    return config;
  },
  response: async (response) => {
    // Log response time
    const requestTime = response.headers.get('X-Request-Time');
    if (requestTime) {
      const duration = Date.now() - new Date(requestTime).getTime();
      console.log(`[API] ${response.url} - ${duration}ms`);
    }
    return response;
  },
  error: (error) => {
    // Log errors
    console.error('[API] Error:', error);
    return error;
  },
});

export default apiService;
export { ApiService }; 