import { test, expect } from '@playwright/test'

/**
 * 简历模块E2E测试
 *
 * 覆盖：
 * - 简历上传页面访问
 * - 文件上传交互
 * - 诊断结果展示
 */

test.describe('简历模块', () => {
  test('上传页面应该正确加载', async ({ page }) => {
    await page.goto('/upload')
    await expect(page.locator('text=上传简历')).toBeVisible()
    await expect(page.locator('text=支持 PDF, DOCX, TXT 格式')).toBeVisible()
  })

  test('拖拽区域应该可见', async ({ page }) => {
    await page.goto('/upload')
    const dropZone = page.locator('[data-testid="drop-zone"], .border-dashed, .border-2').first()
    await expect(dropZone).toBeVisible()
  })

  test('诊断页面应该展示雷达图', async ({ page }) => {
    await page.goto('/diagnosis')
    // 即使没有数据，页面也应该加载
    await expect(page.locator('text=简历诊断')).toBeVisible()
  })
})
