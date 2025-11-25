import axios from 'axios'

// Configure axios base URL
// In development, proxy to backend if needed, or use full URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

axios.defaults.baseURL = API_BASE_URL
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add request interceptor for authentication and debugging
axios.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      // Clear auth tokens
      localStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_token')
      // Optionally redirect to login page
      // window.location.href = '/login'
    }
    console.error('[API Response Error]', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default axios

