import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

const API_URL = '/api/v1'

interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)

        const response = await axios.post(`${API_URL}/auth/login`, formData)
        const { access_token } = response.data

        // Set token in axios defaults
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        // Get user info
        const userResponse = await axios.get(`${API_URL}/auth/me`)
        const user = userResponse.data

        set({ 
          token: access_token, 
          user, 
          isAuthenticated: true 
        })
      },

      logout: () => {
        delete axios.defaults.headers.common['Authorization']
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false 
        })
      },

      setUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

// Set token from storage on app load
const token = useAuthStore.getState().token
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

