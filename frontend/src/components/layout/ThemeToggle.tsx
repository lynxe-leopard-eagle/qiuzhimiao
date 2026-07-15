import { useThemeStore, type ThemeName } from '../../stores/themeStore'

const options: { value: ThemeName; label: string }[] = [
  { value: 'anime', label: 'Anime' },
  { value: 'glass', label: 'Glass' },
]

export default function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()

  return (
    <div
      className="inline-flex items-center gap-1 p-1 rounded-full"
      style={{
        background: 'var(--paper-strong)',
        border: '1px solid var(--nav-border)',
      }}
    >
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => setTheme(opt.value)}
          className="px-3 py-1.5 rounded-full text-xs font-bold transition-all"
          style={
            theme === opt.value
              ? {
                  color: '#fff',
                  background: 'var(--btn-active-bg)',
                }
              : {
                  color: 'var(--muted)',
                  background: 'transparent',
                }
          }
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
