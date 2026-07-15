import { test, expect } from '@playwright/test'

/**
 * 认证流程E2E测试
 *
 * 覆盖：
 * - 首页访问
 * - 登录页面导航
 * - 注册/登录表单交互
 */

test.describe('认证流程', () => {
  test('首页应该正确加载', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/求职喵/)
    await expect(page.locator('text=AI面试教练')).toBeVisible()
  })

  test('应该能导航到登录页面', async ({ page }) => {
    await page.goto('/')
    await page.click('text=登录')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.locator('text=登录')).toBeVisible()
  })

  test('登录表单应该能输入', async ({ page }) => {
    await page.goto('/login')

    // 输入邮箱和密码
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'TestPass123')

    // 验证输入值
    await expect(page.locator('input[type="email"]')).toHaveValue('test@example.com')
    await expect(page.locator('input[type="password"]')).toHaveValue('TestPass123')
  })

  test('登录表单应该验证必填字段', async ({ page }) => {
    await page.goto('/login')

    // 不输入任何内容直接提交
    await page.click('button[type="submit"]')

    // 应该仍然在当前页面（验证阻止了提交）
    await expect(page).toHaveURL(/.*login/)
  })

  test('注册和登录切换应该正常工作', async ({ page }) => {
    await page.goto('/login')

    // 切换到注册
    await page.click('text=注册')
    await expect(page.locator('text=创建账号')).toBeVisible()

    // 切回登录
    await page.click('text=登录')
    await expect(page.locator('text=欢迎回来')).toBeVisible()
  })
})

test.describe('页面导航', () => {
  test('未登录访问受保护页面应重定向到登录', async ({ page }) => {
    await page.goto('/diagnosis')
    // 应该被重定向到登录页
    await expect(page).toHaveURL(/.*login/)
  })

  test('导航栏应该在所有页面显示', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('nav')).toBeVisible()

    await page.goto('/login')
    await expect(page.locator('nav')).toBeVisible()
  })
})
