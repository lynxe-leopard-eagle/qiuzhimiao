import { create } from 'zustand'

export type ThemeName = 'anime' | 'glass'

interface ThemeState {
  theme: ThemeName
  setTheme: (theme: ThemeName) => void
  toggleTheme: () => void
}

function applyTheme(theme: ThemeName) {
  const root = document.documentElement
  root.setAttribute('data-theme', theme)
}

function getInitialTheme(): ThemeName {
  const saved = localStorage.getItem('theme') as ThemeName | null
  if (saved === 'anime' || saved === 'glass') return saved
  return 'anime'
}

const initialTheme = getInitialTheme()
applyTheme(initialTheme)

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: initialTheme,
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    applyTheme(theme)
    set({ theme })
  },
  toggleTheme: () => {
    const next = get().theme === 'anime' ? 'glass' : 'anime'
    get().setTheme(next)
  },
}))
