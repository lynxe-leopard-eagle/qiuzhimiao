import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from '../authStore'

describe('authStore', () => {
  beforeEach(() => {
    // 重置store状态
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
    localStorage.clear()
  })

  it('初始状态应该是未登录', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
    expect(state.isLoading).toBe(false)
  })

  it('setUser应该更新用户状态', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      name: '测试用户',
      avatar: null,
    }

    useAuthStore.getState().setUser(mockUser)

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockUser)
    expect(state.isAuthenticated).toBe(true)
  })

  it('logout应该清除用户状态', () => {
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      name: '测试用户',
      avatar: null,
    }

    useAuthStore.getState().setUser(mockUser)
    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('setLoading应该更新加载状态', () => {
    useAuthStore.getState().setLoading(true)
    expect(useAuthStore.getState().isLoading).toBe(true)

    useAuthStore.getState().setLoading(false)
    expect(useAuthStore.getState().isLoading).toBe(false)
  })
})
