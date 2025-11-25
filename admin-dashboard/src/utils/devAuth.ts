/**
 * Development Authentication Utilities
 * WARNING: Only for development/testing!
 */

import axios from '../config/api'

export const getTestToken = async () => {
  try {
    const response = await axios.get('/api/v1/auth/test-token')
    const { access_token } = response.data
    
    // Store token
    localStorage.setItem('auth_token', access_token)
    
    console.log('✅ Test token stored successfully!')
    console.log('🔄 Refreshing page...')
    
    // Reload page to apply token
    window.location.reload()
    
    return access_token
  } catch (error: any) {
    console.error('❌ Failed to get test token:', error.response?.data?.detail || error.message)
    throw error
  }
}

// Auto-authenticate in development if no token exists
export const autoDevAuth = async () => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  
  if (!token && import.meta.env.DEV) {
    console.log('🔐 No auth token found. Getting test token...')
    try {
      await getTestToken()
    } catch (error) {
      console.error('Failed to auto-authenticate:', error)
    }
  }
}

