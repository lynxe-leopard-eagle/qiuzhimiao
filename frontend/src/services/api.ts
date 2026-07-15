import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: (process.env as any).VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

export const authApi = {
  register: (email: string, password: string, nickname?: string) =>
    api.post('/auth/register', { email, password, nickname }),
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
}

export const resumeApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => api.get('/resumes'),
  diagnose: (resume_id: string, job_description?: string) =>
    api.post('/resumes/diagnose', { resume_id, job_description }),
  get: (id: string) => api.get(`/resumes/${id}`),
  poll: (id: string) => api.get(`/resumes/${id}/poll`),
}

export const jobApi = {
  create: (data: { title: string; company?: string; description?: string }) =>
    api.post('/jobs', data),
  list: () => api.get('/jobs'),
  get: (id: string) => api.get(`/jobs/${id}`),
  analyze: (job_description: string, title?: string, company?: string) =>
    api.post('/jobs/analyze', { job_description, title, company }),
  match: (resume_id: string, job_description?: string, job_id?: string) =>
    api.post('/jobs/matching', { resume_id, job_description, job_id }),
}

export const interviewApi = {
  list: () => api.get('/interviews'),
  start: (round: string, resume_id?: string, job_id?: string, interviewer_style?: string) =>
    api.post('/interviews/start', { round, resume_id, job_id, interviewer_style }),
  answer: (interview_id: string, answer: string) =>
    api.post('/interviews/answer', { interview_id, answer }, {
      responseType: 'text',
    }),
  end: (interview_id: string) => api.post(`/interviews/end?interview_id=${interview_id}`),
  messages: (interview_id: string) => api.get(`/interviews/${interview_id}/messages`),
}

export const reviewApi = {
  list: () => api.get('/reviews'),
  get: (id: string) => api.get(`/reviews/${id}`),
  generate: (interview_id: string) => api.post(`/reviews/generate/${interview_id}`),
}

export const growthApi = {
  radar: () => api.get('/growth/radar'),
  trend: () => api.get('/growth/trend'),
}

export const applicationApi = {
  create: (data: { company: string; position: string; stage?: string; city?: string; salary_range?: string; notes?: string; contact_info?: string }) =>
    api.post('/applications', data),
  list: (stage?: string) => api.get('/applications', { params: stage ? { stage } : {} }),
  stats: () => api.get('/applications/stats'),
  get: (id: string) => api.get(`/applications/${id}`),
  update: (id: string, data: { stage?: string; salary_range?: string; notes?: string; contact_info?: string; feedback?: string }) =>
    api.put(`/applications/${id}`, data),
  delete: (id: string) => api.delete(`/applications/${id}`),
}

export const skillApi = {
  radar: (resume_id?: string, job_description?: string) =>
    api.get('/skills/radar', { params: { resume_id, job_description } }),
  tree: (domain?: string) => api.get('/skills/tree', { params: { domain } }),
  gap: (resume_id: string, job_description: string) =>
    api.post('/skills/gap', { resume_id, job_description }),
}

export const coachApi = {
  tools: () => api.get('/coach/tools'),
  chat: (data: { message: string; messages?: Array<{ role: string; content: string; tool_result?: any }>; job_description?: string }) =>
    api.post('/coach/chat', data),
  report: () => api.get('/coach/report'),
}
