import { create } from 'zustand'

interface AuthState {
  token: string | null
  user: { id: string; email: string; nickname?: string } | null
  setAuth: (token: string, user: { id: string; email: string; nickname?: string }) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: (() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })(),
  setAuth: (token, user) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({ token, user })
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null })
  },
}))
