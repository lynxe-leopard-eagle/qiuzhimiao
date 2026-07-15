import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, FileText, BarChart3, Briefcase, MessageSquare, Sparkles, TrendingUp, RefreshCw } from 'lucide-react'
import { coachApi } from '../services/api'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface CoachReport {
  status: string
  resume_count: number
  interview_count: number
  application_count: number
  avg_interview_score: number
  stage_stats: Record<string, number>
  recent_resumes: Array<{ id: string; filename: string; created_at: string }>
  recent_applications: Array<{ id: string; company: string; position: string; stage: string }>
  recent_interviews: Array<{ id: string; round: string; status: string; score: number }>
  recommendations: string[]
}

const STATUS_COLORS = {
  '起步阶段': 'bg-blue-100 text-blue-700',
  '积极投递阶段': 'bg-green-100 text-green-700',
  '面试冲刺阶段': 'bg-amber-100 text-amber-700',
  '收获阶段': 'bg-purple-100 text-purple-700',
}

const STAGE_LABELS = {
  applied: '已投递',
  interview: '面试中',
  offer: '已获得Offer',
  rejected: '已拒绝',
  pending: '待回复',
}

export default function CoachPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<CoachReport | null>(null)
  const [activeTab, setActiveTab] = useState<'chat' | 'report'>('chat')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchReport()
    const welcomeMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: '你好！我是你的求职教练。我可以帮你：\n\n1. **简历诊断与优化**：ATS兼容性分析、关键词优化、量化建议\n2. **岗位匹配分析**：技能差距分析、匹配度评估、补强路线\n3. **模拟面试**：多轮面试练习、实时反馈、语音分析\n4. **投递追踪**：看板管理、跟进建议、薪资评估\n5. **求职作战报告**：汇总数据、阶段性复盘、下一步计划\n\n请问你想从哪个方面开始？',
      timestamp: new Date(),
    }
    setMessages([welcomeMessage])
  }, [])

  const fetchReport = async () => {
    try {
      const res = await coachApi.report()
      setReport(res.data)
    } catch (err) {
      console.error('Failed to fetch report:', err)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const res = await coachApi.chat({
        message: inputValue,
        job_description: jobDescription,
      })

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.data.response,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，我现在无法回答你的问题，请稍后再试。',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Sparkles className="w-4 h-4" />
            AI 求职教练
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-3">你的智能求职伙伴</h1>
          <p className="text-gray-600">基于 ReAct 框架的 AI 教练，自主分析你的求职数据，给出针对性建议</p>
        </motion.div>

        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-white rounded-xl shadow-sm border border-gray-100 p-1">
            {[
              { key: 'chat', label: '对话', icon: MessageSquare },
              { key: 'report', label: '作战报告', icon: FileText },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => {
                  setActiveTab(tab.key as typeof activeTab)
                  if (tab.key === 'report') fetchReport()
                }}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.key
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {activeTab === 'chat' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
          >
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-white font-bold">AI 求职教练</h2>
                    <p className="text-white/70 text-sm">基于 ReAct 框架的智能分析</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-white/70 text-sm">在线</span>
                </div>
              </div>
            </div>

            {jobDescription && (
              <div className="px-6 py-3 bg-amber-50 border-b border-amber-100">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-amber-700">已设置目标岗位 JD</span>
                  <button
                    onClick={() => setJobDescription('')}
                    className="text-xs text-amber-600 hover:text-amber-800"
                  >
                    清除
                  </button>
                </div>
              </div>
            )}

            <div className="h-96 overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                        message.role === 'user' ? 'bg-primary-600' : 'bg-gray-200'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <span className="text-white text-xs">我</span>
                      ) : (
                        <Bot className="w-4 h-4 text-gray-600" />
                      )}
                    </div>
                    <div
                      className={`max-w-[70%] ${
                        message.role === 'user'
                          ? 'bg-primary-600 text-white rounded-2xl rounded-tr-sm'
                          : 'bg-gray-100 text-gray-800 rounded-2xl rounded-tl-sm'
                      }`}
                    >
                      <div className="p-4 whitespace-pre-wrap" style={{ whiteSpace: 'pre-line' }}>
                        {message.content}
                      </div>
                      <div
                        className={`px-4 pb-2 text-xs ${
                          message.role === 'user' ? 'text-white/60' : 'text-gray-400'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString('zh-CN', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-gray-600" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-4">
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
              <div className="mb-3">
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="可选：粘贴目标岗位JD，我会结合你的简历分析技能差距..."
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                />
              </div>
              <div className="flex items-end gap-3">
                <div className="flex-1">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="输入你的问题，例如：帮我生成求职报告、分析技能差距、简历优化建议..."
                    rows={2}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                  />
                </div>
                <button
                  onClick={handleSend}
                  disabled={loading || !inputValue.trim()}
                  className="bg-primary-600 text-white p-3 rounded-xl hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'report' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {report ? (
              <>
                <div className="grid md:grid-cols-4 gap-4">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <span className="text-gray-600 text-sm">简历数量</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{report.resume_count}</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <MessageSquare className="w-5 h-5 text-green-600" />
                      </div>
                      <span className="text-gray-600 text-sm">面试次数</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{report.interview_count}</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                        <Briefcase className="w-5 h-5 text-amber-600" />
                      </div>
                      <span className="text-gray-600 text-sm">投递数量</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{report.application_count}</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-purple-600" />
                      </div>
                      <span className="text-gray-600 text-sm">平均评分</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{report.avg_interview_score}</div>
                  </motion.div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2 text-primary-600" />
                      当前状态
                    </h2>
                    <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${STATUS_COLORS[report.status as keyof typeof STATUS_COLORS] || 'bg-gray-100 text-gray-700'}`}>
                      {report.status}
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                  >
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2 text-primary-600" />
                      投递阶段分布
                    </h2>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(report.stage_stats).map(([stage, count]) => (
                        <span
                          key={stage}
                          className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                        >
                          {STAGE_LABELS[stage as keyof typeof STAGE_LABELS] || stage}: {count}
                        </span>
                      ))}
                      {Object.keys(report.stage_stats).length === 0 && (
                        <span className="text-gray-400 text-sm">暂无投递记录</span>
                      )}
                    </div>
                  </motion.div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                  {report.recent_resumes.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                    >
                      <h2 className="text-lg font-bold text-gray-900 mb-4">最近简历</h2>
                      <ul className="space-y-2">
                        {report.recent_resumes.map((resume) => (
                          <li key={resume.id} className="text-sm text-gray-700">
                            <span className="font-medium">{resume.filename}</span>
                            <span className="text-gray-400 ml-2">{resume.created_at}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {report.recent_applications.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                    >
                      <h2 className="text-lg font-bold text-gray-900 mb-4">最近投递</h2>
                      <ul className="space-y-2">
                        {report.recent_applications.map((app) => (
                          <li key={app.id} className="text-sm">
                            <span className="font-medium text-gray-700">{app.company}</span>
                            <span className="text-gray-400"> - {app.position}</span>
                            <span className="text-gray-500 ml-2">({STAGE_LABELS[app.stage as keyof typeof STAGE_LABELS] || app.stage})</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}

                  {report.recent_interviews.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                    >
                      <h2 className="text-lg font-bold text-gray-900 mb-4">最近面试</h2>
                      <ul className="space-y-2">
                        {report.recent_interviews.map((interview) => (
                          <li key={interview.id} className="text-sm">
                            <span className="font-medium text-gray-700">{interview.round}面试</span>
                            <span className="text-gray-400"> - {interview.status}</span>
                            {interview.score && (
                              <span className="text-primary-600 ml-2">评分: {interview.score}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )}
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl p-6 text-white"
                >
                  <h2 className="text-lg font-bold mb-4">下一步建议</h2>
                  <ul className="space-y-2">
                    {report.recommendations.map((recommendation, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs font-medium">
                          {i + 1}
                        </span>
                        {recommendation}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-100">
                <RefreshCw className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500">正在获取求职报告...</p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}
