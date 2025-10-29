import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

/**
 * API Error Response Interface
 * 
 * Standardized error response structure from Django REST Framework
 */
interface ApiErrorResponse {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
  [key: string]: any
}

/**
 * API Client Configuration
 * 
 * Base configuration for the Axios instance
 */
const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
}

/**
 * Create Axios Instance
 * 
 * Creates a pre-configured Axios instance for API requests
 */
const apiClient: AxiosInstance = axios.create(API_CONFIG)

/**
 * Request Interceptor
 * 
 * Intercepts all outgoing requests to add authentication token
 * and perform any request transformations
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get auth token from localStorage (if exists)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }

    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      })
    }

    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor
 * 
 * Intercepts all incoming responses to handle errors globally
 * and perform any response transformations
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      })
    }

    return response
  },
  (error: AxiosError<ApiErrorResponse>) => {
    // Extract error message
    let errorMessage = 'An unexpected error occurred'

    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response

      // Handle specific status codes
      switch (status) {
        case 400:
          errorMessage = data.detail || data.message || 'Bad request'
          break
        case 401:
          errorMessage = 'Unauthorized. Please login again.'
          // Clear auth token on 401
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token')
          }
          // Optionally redirect to login
          // window.location.href = '/login'
          break
        case 403:
          errorMessage = 'Forbidden. You do not have permission.'
          break
        case 404:
          errorMessage = 'Resource not found'
          break
        case 500:
          errorMessage = 'Internal server error. Please try again later.'
          break
        default:
          errorMessage = data.detail || data.message || errorMessage
      }

      // Handle validation errors (DRF style)
      if (data.errors) {
        const validationErrors = Object.entries(data.errors)
          .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
          .join('; ')
        errorMessage = validationErrors
      }
    } else if (error.request) {
      // Request was made but no response received
      errorMessage = 'Network error. Please check your internet connection.'
    }

    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('[API Response Error]', {
        message: errorMessage,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url,
      })
    }

    // Create enhanced error with user-friendly message
    const enhancedError = {
      ...error,
      message: errorMessage,
      originalError: error,
    }

    return Promise.reject(enhancedError)
  }
)

/**
 * API Client Export
 * 
 * Use this client for all API requests in the application.
 * 
 * @example
 * ```typescript
 * import apiClient from '@/lib/api-client'
 * 
 * // GET request
 * const response = await apiClient.get('/api/countries/')
 * 
 * // POST request
 * const response = await apiClient.post('/api/countries/', { name: 'Turkey' })
 * 
 * // With query parameters
 * const response = await apiClient.get('/api/countries/', {
 *   params: { page: 1, page_size: 20 }
 * })
 * ```
 */
export default apiClient

/**
 * Type-safe API Client Methods
 * 
 * Wrapper functions for common HTTP methods with TypeScript support
 */
export const api = {
  /**
   * GET request
   */
  get: <T = any>(url: string, config?: any) => 
    apiClient.get<T>(url, config).then(res => res.data),

  /**
   * POST request
   */
  post: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.post<T>(url, data, config).then(res => res.data),

  /**
   * PUT request
   */
  put: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.put<T>(url, data, config).then(res => res.data),

  /**
   * PATCH request
   */
  patch: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.patch<T>(url, data, config).then(res => res.data),

  /**
   * DELETE request
   */
  delete: <T = any>(url: string, config?: any) => 
    apiClient.delete<T>(url, config).then(res => res.data),
}
