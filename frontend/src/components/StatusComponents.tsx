import { ReactNode } from 'react'
import { Loader2, Inbox, AlertTriangle, RefreshCw } from 'lucide-react'

export function LoadingSpinner({ text = '加载中...' }: { text?: string }) {
  return (
    <div className="min-h-[40vh] flex flex-col items-center justify-center">
      <Loader2 className="w-8 h-8 text-primary-600 animate-spin mb-3" />
      <p className="text-gray-500 text-sm">{text}</p>
    </div>
  )
}

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="min-h-[40vh] flex flex-col items-center justify-center text-center px-4">
      <div className="mb-4 text-gray-300">
        {icon || <Inbox className="w-16 h-16" />}
      </div>
      <h3 className="text-lg font-semibold text-gray-700 mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-gray-400 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorState({ title = '出错了', message = '发生了意外错误，请稍后重试', onRetry }: ErrorStateProps) {
  return (
    <div className="min-h-[40vh] flex flex-col items-center justify-center text-center px-4">
      <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
      <h3 className="text-lg font-semibold text-gray-700 mb-1">{title}</h3>
      <p className="text-sm text-gray-400 max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-secondary inline-flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>重试</span>
        </button>
      )}
    </div>
  )
}
