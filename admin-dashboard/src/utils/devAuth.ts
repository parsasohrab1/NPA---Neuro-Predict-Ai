/**
 * Development Authentication Utilities
 * WARNING: Only for development/testing — never auto-login in production builds.
 */

import axios from '../config/api'

export const getTestToken = async () => {
  if (import.meta.env.PROD) {
    throw new Error('Test token is disabled in production builds')
  }

  try {
    const response = await axios.get('/api/v1/auth/test-token')
    const { access_token } = response.data

    localStorage.setItem('auth_token', access_token)

    console.log('✅ Test token stored successfully!')
    console.log('🔄 Refreshing page...')

    window.location.reload()

    return access_token
  } catch (error: any) {
    console.error('❌ Failed to get test token:', error.response?.data?.detail || error.message)
    throw error
  }
}

/** Auto-authenticate in development only if no token exists. Disabled when `import.meta.env.PROD`. */
export const autoDevAuth = async () => {
  if (import.meta.env.PROD) {
    return
  }

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
