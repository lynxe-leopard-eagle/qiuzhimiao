export default function Footer() {
  return (
    <footer
      className="border-t mt-auto"
      style={{
        background: 'var(--nav-bg)',
        backdropFilter: 'var(--nav-blur)',
        WebkitBackdropFilter: 'var(--nav-blur)',
        borderColor: 'var(--nav-border)',
      }}
    >
      <div
        className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center text-sm"
        style={{ color: 'var(--muted)' }}
      >
        <p className="font-bold">© 2026 Interview Coach</p>
      </div>
    </footer>
  )
}
