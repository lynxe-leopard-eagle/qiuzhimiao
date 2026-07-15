import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { Menu, X, Cat } from 'lucide-react'
import { useState } from 'react'
import ThemeToggle from './ThemeToggle'

export default function Navbar() {
  const { token, logout } = useAuthStore()
  const [open, setOpen] = useState(false)
  const location = useLocation()

  const navs = [
    { to: '/dashboard', label: '求职中心' },
    { to: '/upload', label: '简历上传' },
    { to: '/diagnosis', label: '简历诊断' },
    { to: '/matching', label: '岗位分析' },
    { to: '/skills', label: '技能图谱' },
    { to: '/interview', label: 'AI 面试' },
    { to: '/review', label: '复盘报告' },
    { to: '/growth', label: '成长追踪' },
    { to: '/applications', label: '投递看板' },
    { to: '/coach', label: 'AI 教练' },
  ]

  return (
    <nav
      className="sticky top-0 z-50 border-b"
      style={{
        background: 'var(--nav-bg)',
        backdropFilter: 'var(--nav-blur)',
        WebkitBackdropFilter: 'var(--nav-blur)',
        borderColor: 'var(--nav-border)',
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center gap-2" style={{ color: 'var(--ink)' }}>
            <div
              className="w-9 h-9 rounded-2xl flex items-center justify-center"
              style={{
                background: 'var(--btn-active-bg)',
                boxShadow: '0 10px 22px rgba(167,139,250,0.24)',
              }}
            >
              <Cat className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-extrabold">求职<span style={{ color: 'var(--pink)' }}>喵</span></span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {token && navs.map((n) => {
              const isActive = location.pathname === n.to ||
                (n.to !== '/' && location.pathname.startsWith(n.to))
              return (
                <Link
                  key={n.to}
                  to={n.to}
                  className="px-3 py-2 rounded-2xl text-sm font-bold transition-all"
                  style={
                    isActive
                      ? {
                          color: '#fff',
                          background: 'var(--btn-active-bg)',
                        }
                      : {
                          color: 'var(--muted)',
                        }
                  }
                >
                  {n.label}
                </Link>
              )
            })}
            <div className="ml-2">
              <ThemeToggle />
            </div>
            {token ? (
              <button
                onClick={logout}
                className="ml-3 text-sm font-bold transition-colors"
                style={{ color: 'var(--muted)' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--muted)'}
              >
                退出
              </button>
            ) : (
              <Link to="/login" className="btn-primary text-sm ml-3">登录 / 注册</Link>
            )}
          </div>

          <div className="flex items-center gap-2 md:hidden">
            <ThemeToggle />
            <button onClick={() => setOpen(!open)} style={{ color: 'var(--ink)' }}>
              {open ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </div>

      {open && (
        <div className="md:hidden px-4 pb-4 space-y-1">
          {token && navs.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              onClick={() => setOpen(false)}
              className="block px-3 py-2 rounded-2xl text-base font-bold transition-colors"
              style={{ color: 'var(--ink)' }}
            >
              {n.label}
            </Link>
          ))}
          {token ? (
            <button onClick={logout} className="block w-full text-left px-3 py-2 font-bold" style={{ color: '#ef4444' }}>退出</button>
          ) : (
            <Link to="/login" onClick={() => setOpen(false)} className="block px-3 py-2 font-bold" style={{ color: 'var(--pink)' }}>登录 / 注册</Link>
          )}
        </div>
      )}
    </nav>
  )
}
