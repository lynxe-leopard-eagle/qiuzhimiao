interface KittyLogoProps {
  size?: number
  className?: string
}

export default function KittyLogo({ size = 40, className = '' }: KittyLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#A78BFA" />
          <stop offset="100%" stopColor="#7C3AED" />
        </linearGradient>
        <linearGradient id="faceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FDF4FF" />
          <stop offset="100%" stopColor="#F3E8FF" />
        </linearGradient>
        <linearGradient id="earGradient" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stopColor="#F472B6" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
        <radialGradient id="eyeShine" cx="30%" cy="30%" r="50%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="1" />
          <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="noseGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#F472B6" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="softShadow">
          <feDropShadow dx="0" dy="3" stdDeviation="3" floodColor="#7C3AED" floodOpacity="0.3" />
        </filter>
      </defs>

      <g filter="url(#softShadow)">
        <path
          d="M18 52 C18 52 10 35 22 22 L38 38 L60 28 L82 38 L98 22 C110 35 102 52 102 52 L102 72 C102 88 88 98 60 98 C32 98 18 88 18 72 Z"
          fill="url(#bodyGradient)"
        />
      </g>

      <ellipse cx="60" cy="68" rx="34" ry="30" fill="url(#faceGradient)" />

      <path d="M28 42 L40 26 L50 44 Z" fill="url(#bodyGradient)" />
      <path d="M92 42 L80 26 L70 44 Z" fill="url(#bodyGradient)" />

      <path d="M33 40 L40 30 L47 42 Z" fill="url(#earGradient)" />
      <path d="M87 40 L80 30 L73 42 Z" fill="url(#earGradient)" />

      <ellipse cx="45" cy="62" rx="9" ry="12" fill="#1F2937" />
      <ellipse cx="75" cy="62" rx="9" ry="12" fill="#1F2937" />

      <ellipse cx="48" cy="58" rx="4" ry="5" fill="url(#eyeShine)" />
      <ellipse cx="78" cy="58" rx="4" ry="5" fill="url(#eyeShine)" />

      <ellipse cx="43" cy="66" rx="2" ry="2.5" fill="#9CA3AF" opacity="0.6" />
      <ellipse cx="73" cy="66" rx="2" ry="2.5" fill="#9CA3AF" opacity="0.6" />

      <ellipse cx="32" cy="72" rx="6" ry="4" fill="#F9A8D4" opacity="0.5" />
      <ellipse cx="88" cy="72" rx="6" ry="4" fill="#F9A8D4" opacity="0.5" />

      <path d="M55 74 Q60 79 65 74 Q60 77 55 74 Z" fill="url(#noseGradient)" />

      <path
        d="M60 77 Q56 82 52 80"
        stroke="#6B7280"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M60 77 Q64 82 68 80"
        stroke="#6B7280"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />

      <line x1="28" y1="70" x2="42" y2="72" stroke="#9CA3AF" strokeWidth="1" strokeLinecap="round" />
      <line x1="28" y1="76" x2="42" y2="76" stroke="#9CA3AF" strokeWidth="1" strokeLinecap="round" />
      <line x1="78" y1="72" x2="92" y2="70" stroke="#9CA3AF" strokeWidth="1" strokeLinecap="round" />
      <line x1="78" y1="76" x2="92" y2="76" stroke="#9CA3AF" strokeWidth="1" strokeLinecap="round" />

      <path
        d="M22 58 L12 56 L14 62 L18 64 Z"
        fill="#FBBF24"
        transform="rotate(-20 18 60)"
      />
      <path
        d="M98 58 L108 56 L106 62 L102 64 Z"
        fill="#FBBF24"
        transform="rotate(20 102 60)"
      />

      <ellipse cx="60" cy="100" rx="10" ry="3" fill="#7C3AED" opacity="0.2" />
    </svg>
  )
}
