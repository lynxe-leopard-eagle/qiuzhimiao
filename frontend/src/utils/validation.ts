export function validateEmail(email: string): string | null {
  if (!email.trim()) {
    return '邮箱不能为空'
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return '邮箱格式不正确'
  }
  return null
}

export function validatePassword(password: string): string | null {
  if (!password) {
    return '密码不能为空'
  }
  if (password.length < 8) {
    return '密码至少需要 8 位'
  }
  if (!/[a-z]/.test(password)) {
    return '密码需要包含小写字母'
  }
  if (!/[A-Z]/.test(password)) {
    return '密码需要包含大写字母'
  }
  if (!/[0-9]/.test(password)) {
    return '密码需要包含数字'
  }
  return null
}

export function validateResumeId(id: string): string | null {
  if (!id.trim()) {
    return '简历 ID 不能为空'
  }
  return null
}

export function validateJd(jd: string): string | null {
  if (!jd.trim()) {
    return '职位描述不能为空'
  }
  if (jd.trim().length < 50) {
    return '职位描述至少需要 50 个字符'
  }
  return null
}
