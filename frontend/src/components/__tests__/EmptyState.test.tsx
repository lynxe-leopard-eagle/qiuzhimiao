import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { EmptyState } from '../StatusComponents'

describe('EmptyState', () => {
  it('应该渲染标题和描述', () => {
    render(<EmptyState title="暂无数据" description="请先上传简历" />)
    expect(screen.getByText('暂无数据')).toBeInTheDocument()
    expect(screen.getByText('请先上传简历')).toBeInTheDocument()
  })

  it('应该渲染操作按钮', () => {
    const onAction = vi.fn()
    render(
      <EmptyState
        title="暂无数据"
        description="请先上传简历"
        actionText="去上传"
        onAction={onAction}
      />
    )

    const button = screen.getByText('去上传')
    expect(button).toBeInTheDocument()

    fireEvent.click(button)
    expect(onAction).toHaveBeenCalledTimes(1)
  })

  it('没有action时不渲染按钮', () => {
    render(<EmptyState title="空状态" description="描述文字" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
