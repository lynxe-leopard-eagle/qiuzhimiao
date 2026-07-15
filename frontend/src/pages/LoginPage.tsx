import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../services/api'
import { validateEmail, validatePassword } from '../utils/validation'
import { Cat, Loader2 } from 'lucide-react'

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [loading, setLoading] = useState(false)
  const [guestLoading, setGuestLoading] = useState(false)
  const [error, setError] = useState('')
  const [emailError, setEmailError] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const TEST_EMAIL = 'test@qiuzhimiao.com'
  const TEST_PASSWORD = 'test123456'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const emailErr = validateEmail(email)
    const passwordErr = validatePassword(password)
    setEmailError(emailErr)
    setPasswordError(passwordErr)
    if (emailErr || passwordErr) return

    setLoading(true)
    try {
      const res = isRegister
        ? await authApi.register(email, password, nickname || undefined)
        : await authApi.login(email, password)
      const { access_token, user } = res.data
      setAuth(access_token, user)
      navigate('/upload')
    } catch (err: any) {
      setError(err.response?.data?.detail || '请求失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGuestLogin = async () => {
    setError('')
    setGuestLoading(true)
    try {
      const res = await authApi.login(TEST_EMAIL, TEST_PASSWORD)
      const { access_token, user } = res.data
      setAuth(access_token, user)
      navigate('/upload')
    } catch (err: any) {
      setError(err.response?.data?.detail || '测试账号登录失败，请稍后重试')
    } finally {
      setGuestLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <div className="text-center mb-6">
          <Cat className="w-12 h-12 text-primary-600 mx-auto mb-2" />
          <h2 className="text-2xl font-bold text-gray-900">
            {isRegister ? '注册账号' : '欢迎回来'}
          </h2>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => { setEmail(e.target.value); setEmailError(null) }}
              className="input"
              placeholder="you@example.com"
            />
            {emailError && <p className="text-xs text-red-500 mt-1">{emailError}</p>}
          </div>
          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">昵称</label>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="input"
                placeholder="可选"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => { setPassword(e.target.value); setPasswordError(null) }}
              className="input"
              placeholder="至少 8 位，需含大小写字母和数字"
            />
            {passwordError && <p className="text-xs text-red-500 mt-1">{passwordError}</p>}
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary flex justify-center items-center space-x-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{isRegister ? '注册' : '登录'}</span>
          </button>
        </form>
        <div className="relative my-5">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-white px-3 text-gray-400">或</span>
          </div>
        </div>
        <button
          type="button"
          onClick={handleGuestLogin}
          disabled={guestLoading}
          className="w-full btn-secondary flex justify-center items-center space-x-2"
        >
          {guestLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Cat className="w-4 h-4" />
          )}
          <span>快速体验（测试账号）</span>
        </button>
        <p className="mt-3 text-center text-xs text-gray-400">
          测试账号无需注册，点击即可直接进入
        </p>
        <p className="mt-4 text-center text-sm text-gray-500">
          {isRegister ? '已有账号？' : '还没有账号？'}
          <button
            onClick={() => { setIsRegister(!isRegister); setEmailError(null); setPasswordError(null) }}
            className="text-primary-600 hover:underline ml-1"
          >
            {isRegister ? '去登录' : '去注册'}
          </button>
        </p>
      </div>
    </div>
  )
}
