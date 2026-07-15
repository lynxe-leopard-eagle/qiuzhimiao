import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeApi, jobApi, interviewApi, applicationApi } from '../services/api'
import type { Resume, Job, Interview, Application } from '../types'
import {
  FileText, Briefcase, MessageSquare, Send,
  Eye, ArrowRight, Clock, MapPin, DollarSign,
  AlertCircle, Loader2, Sparkles,
  Star, Target, BarChart3, RefreshCw, ChevronRight,
  Building2, User, Calendar, Award
} from 'lucide-react'
import { motion } from 'framer-motion'

export default function DashboardPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'resumes' | 'jobs' | 'interviews' | 'applications'>('all')
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [resResumes, resJobs, resInterviews, resApplications] = await Promise.all([
        resumeApi.list(),
        jobApi.list(),
        interviewApi.list(),
        applicationApi.list(),
      ])
      setResumes(resResumes.data)
      setJobs(resJobs.data)
      setInterviews(resInterviews.data)
      setApplications(resApplications.data)
    } catch (err) {
      console.error('加载数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRoundLabel = (round: string) => {
    const labels: Record<string, string> = {
      hr: 'HR 面试',
      tech1: '技术一面',
      tech2: '技术二面',
      behavioral: '行为面试',
    }
    return labels[round] || round
  }

  const getRoundColor = (round: string) => {
    const colors: Record<string, string> = {
      hr: 'bg-green-100 text-green-700',
      tech1: 'bg-primary-100 text-primary-700',
      tech2: 'bg-purple-100 text-purple-700',
      behavioral: 'bg-blue-100 text-blue-700',
    }
    return colors[round] || 'bg-gray-100 text-gray-700'
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      ongoing: '进行中',
      ended: '已结束',
      completed: '已完成',
      pending: '待筛选',
      interviewing: '面试中',
      offer: '已获 Offer',
      rejected: '已拒绝',
      applied: '已投递',
    }
    return labels[status] || status
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      ongoing: 'bg-yellow-100 text-yellow-700',
      ended: 'bg-gray-100 text-gray-700',
      completed: 'bg-green-100 text-green-700',
      pending: 'bg-blue-100 text-blue-700',
      interviewing: 'bg-orange-100 text-orange-700',
      offer: 'bg-emerald-100 text-emerald-700',
      rejected: 'bg-red-100 text-red-700',
      applied: 'bg-indigo-100 text-indigo-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN')
  }

  const stats = [
    { label: '简历数量', value: resumes.length, icon: FileText, color: 'text-blue-600 bg-blue-50' },
    { label: '目标岗位', value: jobs.length, icon: Briefcase, color: 'text-primary-600 bg-primary-50' },
    { label: '面试记录', value: interviews.length, icon: MessageSquare, color: 'text-purple-600 bg-purple-50' },
    { label: '投递记录', value: applications.length, icon: Send, color: 'text-orange-600 bg-orange-50' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
            求职中心
          </h1>
          <p className="text-gray-500 text-sm mt-1">查看参考数据，体验完整功能</p>
        </div>
        <button onClick={loadData} disabled={loading} className="btn-secondary flex items-center">
          {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新数据
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">正在加载参考数据...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card bg-white"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-6 h-6" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {[
              { key: 'all', label: '全部', icon: Sparkles },
              { key: 'resumes', label: '简历', icon: FileText },
              { key: 'jobs', label: '岗位', icon: Briefcase },
              { key: 'interviews', label: '面试', icon: MessageSquare },
              { key: 'applications', label: '投递', icon: Send },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as typeof activeTab)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === tab.key
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {(activeTab === 'all' || activeTab === 'resumes') && (
            <section className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  参考简历
                </h2>
                <button
                  onClick={() => navigate('/upload')}
                  className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                >
                  上传新简历 <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {resumes.map((resume, i) => (
                  <motion.div
                    key={resume.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="card hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => navigate('/diagnosis', { state: { resumeId: resume.id } })}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <FileText className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{resume.original_filename}</h3>
                          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                            <span className={`px-2 py-0.5 rounded-full ${getStatusColor(resume.status)}`}>
                              {getStatusLabel(resume.status)}
                            </span>
                            {resume.confidence && (
                              <span className="flex items-center">
                                <Star className="w-3 h-3 text-yellow-500 fill-current" />
                                {Math.round(resume.confidence * 100)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                        <Eye className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                    {resume.extracted_name && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-4 text-sm">
                          <div className="flex items-center gap-1 text-gray-600">
                            <User className="w-4 h-4 text-gray-400" />
                            {resume.extracted_name}
                          </div>
                          {resume.extracted_email && (
                            <div className="flex items-center gap-1 text-gray-600">
                              <MailIcon className="w-4 h-4 text-gray-400" />
                              {resume.extracted_email}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
                {resumes.length === 0 && (
                  <div className="col-span-full text-center py-8 bg-gray-50 rounded-xl">
                    <FileText className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500">暂无简历数据</p>
                    <button onClick={() => navigate('/upload')} className="mt-3 text-primary-600 text-sm">
                      上传第一份简历
                    </button>
                  </div>
                )}
              </div>
            </section>
          )}

          {(activeTab === 'all' || activeTab === 'jobs') && (
            <section className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Briefcase className="w-5 h-5 mr-2 text-primary-600" />
                  参考岗位
                </h2>
                <button
                  onClick={() => navigate('/matching')}
                  className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                >
                  分析新岗位 <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {jobs.map((job, i) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="card hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => navigate('/matching')}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" />
                          {job.company}
                        </p>
                        <h3 className="font-semibold text-gray-900 mt-1">{job.title}</h3>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoundColor(job.category || 'tech1')}`}>
                        {job.category === 'frontend' ? '前端' : job.category === 'backend' ? '后端' : job.category === 'ai' ? 'AI' : '测试'}
                      </span>
                    </div>
                    {job.requirements && (
                      <div className="space-y-2 text-xs">
                        {job.requirements['education'] && (
                          <div className="flex items-center gap-1.5 text-gray-500">
                            <Award className="w-3.5 h-3.5" />
                            {job.requirements['education']}
                          </div>
                        )}
                        {job.requirements['experience'] && (
                          <div className="flex items-center gap-1.5 text-gray-500">
                            <Clock className="w-3.5 h-3.5" />
                            {job.requirements['experience']}
                          </div>
                        )}
                        {job.requirements['skills'] && Array.isArray(job.requirements['skills']) && (
                          <div>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {job.requirements['skills'].slice(0, 4).map((skill: string) => (
                                <span key={skill} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                                  {skill}
                                </span>
                              ))}
                              {job.requirements['skills'].length > 4 && (
                                <span className="px-2 py-0.5 bg-gray-50 text-gray-400 rounded text-xs">
                                  +{job.requirements['skills'].length - 4}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                ))}
                {jobs.length === 0 && (
                  <div className="col-span-full text-center py-8 bg-gray-50 rounded-xl">
                    <Briefcase className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500">暂无岗位数据</p>
                    <button onClick={() => navigate('/matching')} className="mt-3 text-primary-600 text-sm">
                      添加目标岗位
                    </button>
                  </div>
                )}
              </div>
            </section>
          )}

          {(activeTab === 'all' || activeTab === 'interviews') && (
            <section className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2 text-purple-600" />
                  面试记录
                </h2>
                <button
                  onClick={() => navigate('/interview')}
                  className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                >
                  开始新面试 <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {interviews.map((interview, i) => (
                  <motion.div
                    key={interview.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="card hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg ${getRoundColor(interview.round)} flex items-center justify-center`}>
                          <MessageSquare className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{getRoundLabel(interview.round)}</h3>
                          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                            <span className={`px-2 py-0.5 rounded-full ${getStatusColor(interview.status)}`}>
                              {getStatusLabel(interview.status)}
                            </span>
                            {interview.duration && (
                              <span className="flex items-center">
                                <Clock className="w-3 h-3" />
                                {interview.duration}分钟
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <span className="text-xs text-gray-400">{formatDate(interview.created_at)}</span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                      <span className="text-xs text-gray-500">点击查看详情</span>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </motion.div>
                ))}
                {interviews.length === 0 && (
                  <div className="col-span-full text-center py-8 bg-gray-50 rounded-xl">
                    <MessageSquare className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500">暂无面试记录</p>
                    <button onClick={() => navigate('/interview')} className="mt-3 text-primary-600 text-sm">
                      开始模拟面试
                    </button>
                  </div>
                )}
              </div>
            </section>
          )}

          {(activeTab === 'all' || activeTab === 'applications') && (
            <section className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Send className="w-5 h-5 mr-2 text-orange-600" />
                  投递记录
                </h2>
                <button
                  onClick={() => navigate('/applications')}
                  className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                >
                  查看全部 <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {applications.map((app, i) => (
                  <motion.div
                    key={app.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="card hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{app.company}</p>
                        <p className="text-sm text-gray-600 mt-0.5">{app.position}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(app.stage)}`}>
                        {getStatusLabel(app.stage)}
                      </span>
                    </div>
                    <div className="space-y-2 text-xs">
                      {app.city && (
                        <div className="flex items-center gap-1.5 text-gray-500">
                          <MapPin className="w-3.5 h-3.5" />
                          {app.city}
                        </div>
                      )}
                      {app.salary_range && (
                        <div className="flex items-center gap-1.5 text-gray-500">
                          <DollarSign className="w-3.5 h-3.5" />
                          {app.salary_range}
                        </div>
                      )}
                      {app.notes && (
                        <div className="flex items-start gap-1.5 text-gray-500">
                          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                          <span className="line-clamp-2">{app.notes}</span>
                        </div>
                      )}
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <span className="text-xs text-gray-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(app.created_at)}
                      </span>
                    </div>
                  </motion.div>
                ))}
                {applications.length === 0 && (
                  <div className="col-span-full text-center py-8 bg-gray-50 rounded-xl">
                    <Send className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500">暂无投递记录</p>
                    <button onClick={() => navigate('/applications')} className="mt-3 text-primary-600 text-sm">
                      添加投递记录
                    </button>
                  </div>
                )}
              </div>
            </section>
          )}

          {activeTab === 'all' && (
            <section className="mt-8">
              <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
                <div className="flex flex-col md:flex-row items-center justify-between gap-6 p-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <Sparkles className="w-5 h-5 mr-2 text-primary-600" />
                      体验完整求职流程
                    </h3>
                    <p className="text-sm text-gray-600 mt-2 max-w-md">
                      系统已预置参考简历、岗位、面试和投递数据，您可以直接体验所有功能模块。
                      点击下方按钮开始您的求职之旅！
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <button onClick={() => navigate('/diagnosis', { state: { resumeId: resumes[0]?.id } })} className="btn-primary flex items-center justify-center">
                      <FileText className="w-4 h-4 mr-2" />
                      诊断简历
                    </button>
                    <button onClick={() => navigate('/matching')} className="btn-secondary flex items-center justify-center">
                      <Target className="w-4 h-4 mr-2" />
                      岗位匹配
                    </button>
                    <button onClick={() => navigate('/interview')} className="btn-secondary flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      模拟面试
                    </button>
                  </div>
                </div>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

function MailIcon({ className }: { className?: string }) {
  return (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  )
}