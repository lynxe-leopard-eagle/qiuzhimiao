import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingSpinner } from '../StatusComponents'

describe('LoadingSpinner', () => {
  it('应该渲染加载文本', () => {
    render(<LoadingSpinner text="正在加载..." />)
    expect(screen.getByText('正在加载...')).toBeInTheDocument()
  })

  it('应该渲染默认加载文本', () => {
    render(<LoadingSpinner />)
    expect(screen.getByText('加载中...')).toBeInTheDocument()
  })

  it('应该包含动画元素', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })
})
