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

export interface MfaRequiredResult {
  mfa_required: true
  mfa_token: string
}

export class MfaRequiredError extends Error {
  mfa_required = true as const
  mfa_token: string

  constructor(mfa_token: string) {
    super('MFA verification required')
    this.name = 'MfaRequiredError'
    this.mfa_token = mfa_token
  }
}

export function isMfaRequiredError(err: unknown): err is MfaRequiredError {
  return err instanceof MfaRequiredError || (
    typeof err === 'object' &&
    err !== null &&
    (err as MfaRequiredError).mfa_required === true &&
    typeof (err as MfaRequiredError).mfa_token === 'string'
  )
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  loginWithMfa: (mfaToken: string, code: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

async function completeLogin(access_token: string, set: (partial: Partial<AuthState>) => void) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
  const userResponse = await axios.get(`${API_URL}/auth/me`)
  const user = userResponse.data
  set({
    token: access_token,
    user,
    isAuthenticated: true,
  })
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
        const data = response.data

        if (data.mfa_required && data.mfa_token) {
          throw new MfaRequiredError(data.mfa_token)
        }

        const { access_token } = data
        if (!access_token) {
          throw new Error('Login failed: no access token received')
        }

        await completeLogin(access_token, set)
      },

      loginWithMfa: async (mfaToken: string, code: string) => {
        const response = await axios.post(`${API_URL}/auth/login/mfa`, {
          mfa_token: mfaToken,
          code,
        })
        const { access_token } = response.data
        if (!access_token) {
          throw new Error('MFA verification failed: no access token received')
        }
        await completeLogin(access_token, set)
      },

      logout: () => {
        delete axios.defaults.headers.common['Authorization']
        set({
          user: null,
          token: null,
          isAuthenticated: false,
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
