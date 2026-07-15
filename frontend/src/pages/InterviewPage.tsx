import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { interviewApi, reviewApi, resumeApi } from '../services/api'
import type { InterviewMessage, Evaluation, Interview } from '../types'
import { Loader2, Send, MessageSquare, User, Flag, Clock, BarChart3, Target, Mic, MicOff, Settings, Smile, Frown, Meh, Sparkles, CheckSquare, Square, Activity, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'

interface VoiceAnalysis {
  duration: number
  wordCount: number
  speed: number
  pauses: number
  fillerWords: string[]
  suggestions: string[]
}

export default function InterviewPage() {
  const [resumeId, setResumeId] = useState('')
  const [round, setRound] = useState('tech1')
  const [interviewId, setInterviewId] = useState('')
  const [messages, setMessages] = useState<InterviewMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [latestEval, setLatestEval] = useState<Evaluation | null>(null)
  const [ended, setEnded] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [interviewerStyle, setInterviewerStyle] = useState('friendly')
  const [showStyleSettings, setShowStyleSettings] = useState(false)
  const [checklist, setChecklist] = useState<boolean[]>([false, false, false, false, false])
  const [voiceAnalysis, setVoiceAnalysis] = useState<VoiceAnalysis | null>(null)
  const [showVoiceAnalysis, setShowVoiceAnalysis] = useState(false)
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [loadingPreset, setLoadingPreset] = useState(true)
  const navigate = useNavigate()
  const scrollRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const transcriptRef = useRef<string>('')

  useEffect(() => {
    if (!interviewId) {
      loadPresetData()
    }
  }, [interviewId])

  const loadPresetData = async () => {
    setLoadingPreset(true)
    try {
      const [resInterviews, resResumes] = await Promise.all([
        interviewApi.list(),
        resumeApi.list(),
      ])
      setInterviews(resInterviews.data)
      if (resResumes.data.length > 0) {
        setResumeId(resResumes.data[0].id)
      }
    } catch (err) {
      console.error('加载预置数据失败:', err)
    } finally {
      setLoadingPreset(false)
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

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      ongoing: '进行中',
      ended: '已结束',
      completed: '已完成',
    }
    return labels[status] || status
  }

  const loadInterviewMessages = async (interview: Interview) => {
    setLoading(true)
    try {
      const res = await interviewApi.messages(interview.id)
      setMessages(res.data)
      setInterviewId(interview.id)
      setRound(interview.round)
      setResumeId(interview.resume_id || '')
    } catch (err) {
      console.error('加载面试记录失败:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' }) }, [messages])

  useEffect(() => {
    if (!ended && interviewId) {
      const timer = setInterval(() => setTimeElapsed(t => t + 1), 1000)
      return () => clearInterval(timer)
    }
  }, [ended, interviewId])

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0')
    const s = (seconds % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  const start = async () => {
    setLoading(true)
    try {
      const res = await interviewApi.start(round, resumeId || undefined, undefined, interviewerStyle)
      setInterviewId(res.data.interview_id)
      setMessages([{ id: '1', role: 'interviewer', content: res.data.first_question, created_at: new Date().toISOString() }])
    } catch (err: any) {
      alert(err.response?.data?.detail || '启动失败')
    } finally { setLoading(false) }
  }

  const send = async () => {
    if (!input.trim() || !interviewId) return
    const text = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', content: text, created_at: new Date().toISOString() }])
    setEvaluating(true)

    try {
      const res = await interviewApi.answer(interviewId, text)
      const lines = (res.data as string).split('\n').filter(Boolean)
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = JSON.parse(line.slice(6))
        if (payload.type === 'evaluation') {
          setLatestEval(payload.payload as Evaluation)
        } else if (payload.type === 'question') {
          setMessages((prev) => [...prev, { id: Date.now().toString() + 'q', role: 'interviewer', content: payload.payload, created_at: new Date().toISOString() }])
        } else if (payload.type === 'end') {
          setEnded(true)
        }
      }
    } catch (err) {
      console.error(err)
    } finally { setEvaluating(false) }
  }

  const end = async () => {
    if (!interviewId) return
    await interviewApi.end(interviewId)
    setEnded(true)
    try {
      const res = await reviewApi.generate(interviewId)
      navigate(`/review/${res.data.id}`)
    } catch {
      navigate('/review')
    }
  }

  const INTERVIEWER_STYLES = [
    { key: 'friendly', label: '友好型', desc: '温和引导，鼓励表达', icon: Smile },
    { key: 'professional', label: '专业型', desc: '严谨认真，注重细节', icon: Meh },
    { key: 'strict', label: '严厉型', desc: '高压追问，挑战极限', icon: Frown },
  ]

  const CHECKLIST_ITEMS = [
    '准备好安静的环境',
    '准备纸笔记录关键问题',
    '回顾简历中的项目细节',
    '准备1-2个向面试官提问的问题',
    '调整心态，放松心情',
  ]

  const toggleChecklist = (idx: number) => {
    setChecklist(prev => prev.map((v, i) => i === idx ? !v : v))
  }

  // 语音录制和分析功能（参考职途AI）
  const startVoiceRecording = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('您的浏览器不支持语音识别，请使用 Chrome 浏览器')
      return
    }
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.continuous = true
    recognition.interimResults = true
    
    transcriptRef.current = ''
    let startTime = Date.now()
    
    recognition.onresult = (event: any) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      transcriptRef.current = transcript
      setInput(transcript)
    }
    
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsRecording(false)
    }
    
    recognition.onend = () => {
      setIsRecording(false)
      // 分析语音内容
      if (transcriptRef.current) {
        analyzeVoice(transcriptRef.current, (Date.now() - startTime) / 1000)
      }
    }
    
    recognitionRef.current = recognition
    recognition.start()
    setIsRecording(true)
  }

  const stopVoiceRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    setIsRecording(false)
  }

  const analyzeVoice = (text: string, durationSeconds: number) => {
    const words = text.trim().split(/\s+/).filter(w => w.length > 0)
    const wordCount = words.length
    
    // 计算语速（字/分钟）
    const speed = durationSeconds > 0 ? Math.round(wordCount / (durationSeconds / 60)) : 0
    
    // 检测停顿（通过标点符号估算）
    const pauses = (text.match(/[，。！？、；]/g) || []).length
    
    // 检测语气词/填充词
    const fillerWordsList = ['那个', '就是说', '然后呢', '其实', '怎么讲', '对吧', '是不是', '嗯', '啊', '呃', '这个', '那个']
    const detectedFiller: string[] = []
    fillerWordsList.forEach(filler => {
      const count = (text.match(new RegExp(filler, 'g')) || []).length
      if (count > 0) detectedFiller.push(`${filler}(${count}次)`)
    })
    
    // 生成建议
    const suggestions: string[] = []
    if (speed < 120) {
      suggestions.push('语速偏慢，可以适当加快节奏，增强表达自信')
    } else if (speed > 200) {
      suggestions.push('语速偏快，建议放慢节奏，让面试官有思考时间')
    }
    if (detectedFiller.length > 3) {
      suggestions.push('语气词较多，建议用停顿代替填充词，显得更专业')
    }
    if (wordCount < 30 && durationSeconds > 10) {
      suggestions.push('回答内容较少，建议展开说明，增加具体细节')
    }
    if (suggestions.length === 0) {
      suggestions.push('表达流畅，继续保持')
    }
    
    setVoiceAnalysis({
      duration: Math.round(durationSeconds),
      wordCount,
      speed,
      pauses,
      fillerWords: detectedFiller,
      suggestions
    })
    setShowVoiceAnalysis(true)
  }

  if (!interviewId) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <MessageSquare className="w-6 h-6 mr-2 text-primary-600" />
          AI 面试模拟
        </h1>
        
        {/* 面试说明 */}
        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-100 mb-6">
          <h3 className="font-semibold text-primary-800 mb-2">面试流程</h3>
          <div className="flex items-center gap-4 text-sm text-primary-700">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-primary-500" />
              <span>HR 面试（3-5 题）</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span>技术一面（5-8 题）</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-indigo-500" />
              <span>技术二面（5-8 题）</span>
            </div>
          </div>
        </div>

        <div className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">选择面试轮次</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { key: 'hr', label: 'HR 面试', desc: '沟通能力、职业规划', color: 'border-green-500 bg-green-50' },
                { key: 'tech1', label: '技术一面', desc: '基础技术、项目经验', color: 'border-primary-500 bg-primary-50' },
                { key: 'tech2', label: '技术二面', desc: '系统设计、深度追问', color: 'border-purple-500 bg-purple-50' },
              ].map((r) => (
                <button
                  key={r.key}
                  onClick={() => setRound(r.key)}
                  className={`p-4 rounded-xl border-2 text-sm transition-all text-left ${
                    round === r.key ? `${r.color} shadow-sm` : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className={`font-semibold ${round === r.key ? 'text-gray-900' : 'text-gray-700'}`}>{r.label}</div>
                  <div className={`text-xs mt-1 ${round === r.key ? 'text-gray-600' : 'text-gray-500'}`}>{r.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 面试官风格选择 */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">面试官风格</label>
              <button
                onClick={() => setShowStyleSettings(!showStyleSettings)}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <Settings className="w-4 h-4 text-gray-500" />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {INTERVIEWER_STYLES.map((style) => {
                const Icon = style.icon
                return (
                  <button
                    key={style.key}
                    onClick={() => setInterviewerStyle(style.key)}
                    className={`p-4 rounded-xl border-2 text-sm transition-all text-left ${
                      interviewerStyle === style.key ? 'border-primary-500 bg-primary-50 shadow-sm' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className={`w-4 h-4 ${interviewerStyle === style.key ? 'text-primary-600' : 'text-gray-400'}`} />
                      <span className={`font-semibold ${interviewerStyle === style.key ? 'text-primary-700' : 'text-gray-900'}`}>{style.label}</span>
                    </div>
                    <div className={`text-xs ${interviewerStyle === style.key ? 'text-primary-600' : 'text-gray-500'}`}>{style.desc}</div>
                  </button>
                )
              })}
            </div>
          </div>

          {!loadingPreset && interviews.length > 0 && (
          <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-100">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <MessageSquare className="w-4 h-4 inline mr-1.5 -mt-0.5 text-purple-600" />
              参考面试记录 <span className="text-gray-400 font-normal">（点击查看历史面试）</span>
            </label>
            <div className="space-y-2">
              {interviews.map((interview) => (
                <button
                  key={interview.id}
                  onClick={() => loadInterviewMessages(interview)}
                  className={`w-full text-left p-3 rounded-xl transition-colors text-sm ${
                    interview.status === 'ongoing'
                      ? 'bg-white border-2 border-purple-500 shadow-sm'
                      : 'bg-white/50 border border-transparent hover:bg-white hover:border-purple-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{getRoundLabel(interview.round)}</div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {interview.duration && `${interview.duration}分钟 | `}
                        {getStatusLabel(interview.status)}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      interview.status === 'ongoing' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {getStatusLabel(interview.status)}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {loadingPreset && (
          <div className="card text-center py-4">
            <Loader2 className="w-5 h-5 text-primary-600 animate-spin mx-auto" />
            <p className="text-sm text-gray-500 mt-2">加载参考数据...</p>
          </div>
        )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">简历 ID（可选）</label>
            <input value={resumeId} onChange={(e) => setResumeId(e.target.value)} className="input" placeholder="输入简历 ID 以基于简历内容提问" />
          </div>

          {/* 面试小贴士 */}
          <div className="p-4 bg-gray-50 rounded-xl">
            <div className="flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-gray-700">面试小贴士</p>
                <p className="text-xs text-gray-500 mt-1">
                  {interviewerStyle === 'friendly' && '友好型面试官注重你的表达能力和团队协作精神，请放松心态，展现真实的自己。'}
                  {interviewerStyle === 'professional' && '专业型面试官注重技术深度和细节，请准备具体的技术案例和数据支撑。'}
                  {interviewerStyle === 'strict' && '严厉型面试官会不断追问，请保持冷静，结构化地回答问题，不要被压力打乱节奏。'}
                </p>
              </div>
            </div>
          </div>

          {/* 面试准备清单 */}
          <div className="p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center gap-2 mb-3">
              <CheckSquare className="w-4 h-4 text-primary-600 flex-shrink-0" />
              <p className="text-sm font-medium text-gray-700">面试准备清单</p>
              <span className="ml-auto text-xs text-gray-400">
                {checklist.filter(Boolean).length}/{CHECKLIST_ITEMS.length}
              </span>
            </div>
            <div className="space-y-2">
              {CHECKLIST_ITEMS.map((item, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => toggleChecklist(i)}
                  className="flex items-center gap-2 w-full text-left group"
                >
                  {checklist[i] ? (
                    <CheckSquare className="w-4 h-4 text-primary-600 flex-shrink-0" />
                  ) : (
                    <Square className="w-4 h-4 text-gray-400 flex-shrink-0 group-hover:text-gray-500" />
                  )}
                  <span className={`text-sm ${checklist[i] ? 'text-gray-400 line-through' : 'text-gray-700'}`}>
                    {item}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <button onClick={start} disabled={loading} className="w-full btn-primary flex justify-center items-center space-x-2">
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <MessageSquare className="w-5 h-5" />
            <span>开始面试</span>
          </button>
        </div>
      </div>
    )
  }

  const roundLabels: Record<string, string> = { hr: 'HR 面试', tech1: '技术一面', tech2: '技术二面' }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-64px-56px)]">
      {/* 顶部栏 */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-blue-500 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">{roundLabels[round]}</h1>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Clock className="w-3 h-3" />
              <span>{formatTime(timeElapsed)}</span>
              <span className="text-gray-300">|</span>
              <span>{messages.filter(m => m.role === 'interviewer').length} 道题</span>
            </div>
          </div>
        </div>
        {!ended && (
          <button onClick={end} className="text-sm text-red-500 hover:text-red-600 flex items-center px-3 py-1.5 rounded-lg hover:bg-red-50 transition-colors">
            <Flag className="w-4 h-4 mr-1" />结束面试
          </button>
        )}
      </div>

      {/* 实时评分面板 */}
      {latestEval && (
        <div className="card mb-3 py-3 px-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary-600" />
              <span className="text-sm font-medium">实时评分</span>
            </div>
            <span className={`text-lg font-bold ${latestEval.overall >= 80 ? 'text-green-600' : latestEval.overall >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
              {latestEval.overall}分
            </span>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {[
              { label: '专业', val: latestEval.professional, color: 'blue' },
              { label: '逻辑', val: latestEval.logic, color: 'green' },
              { label: '沟通', val: latestEval.communication, color: 'purple' },
              { label: '项目', val: latestEval.project, color: 'orange' },
              { label: '匹配', val: latestEval.match, color: 'pink' },
              ...(latestEval.learning != null ? [{ label: '学习', val: latestEval.learning, color: 'cyan' }] : []),
              ...(latestEval.stress_resistance != null ? [{ label: '抗压', val: latestEval.stress_resistance, color: 'indigo' }] : []),
              ...(latestEval.decomposition != null ? [{ label: '拆解', val: latestEval.decomposition, color: 'rose' }] : []),
              ...(latestEval.engineering_quality != null ? [{ label: '工程', val: latestEval.engineering_quality, color: 'teal' }] : []),
              ...(latestEval.innovation != null ? [{ label: '创新', val: latestEval.innovation, color: 'amber' }] : []),
            ].map((d) => (
              <div key={d.label} className="text-center">
                <div className={`text-lg font-bold ${d.val >= 80 ? 'text-green-600' : d.val >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {d.val}
                </div>
                <div className="text-xs text-gray-400">{d.label}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2 flex items-start">
            <Target className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
            {latestEval.feedback}
          </p>
        </div>
      )}

      {/* 消息列表 */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start space-x-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                m.role === 'user' 
                  ? 'bg-gradient-to-br from-primary-500 to-blue-500 text-white' 
                  : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600'
              }`}>
                {m.role === 'user' ? <User className="w-4 h-4" /> : <MessageSquare className="w-4 h-4" />}
              </div>
              <div className={`px-4 py-3 rounded-2xl text-sm ${
                m.role === 'user' 
                  ? 'bg-gradient-to-br from-primary-600 to-blue-600 text-white rounded-br-md' 
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
              }`}>
                {m.content}
              </div>
            </div>
          </div>
        ))}
        {evaluating && (
          <div className="flex items-center space-x-3 text-gray-400 text-sm">
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div className="flex items-center">
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              <span>面试官正在思考并评判...</span>
            </div>
          </div>
        )}
      </div>

      {/* 输入区域 */}
      {!ended ? (
        <div className="flex flex-col gap-3 pt-3 border-t border-gray-100">
          {/* 语音分析结果 */}
          {showVoiceAnalysis && voiceAnalysis && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-purple-800 flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  语音分析
                </h4>
                <button onClick={() => setShowVoiceAnalysis(false)} className="text-purple-400 hover:text-purple-600 text-sm">关闭</button>
              </div>
              <div className="grid grid-cols-4 gap-4 mb-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">{voiceAnalysis.duration}s</div>
                  <div className="text-xs text-purple-500">时长</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">{voiceAnalysis.wordCount}</div>
                  <div className="text-xs text-purple-500">字数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">{voiceAnalysis.speed}</div>
                  <div className="text-xs text-purple-500">字/分钟</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">{voiceAnalysis.pauses}</div>
                  <div className="text-xs text-purple-500">停顿</div>
                </div>
              </div>
              {voiceAnalysis.fillerWords.length > 0 && (
                <div className="mb-2">
                  <span className="text-xs text-purple-600">语气词：</span>
                  {voiceAnalysis.fillerWords.map((w, i) => (
                    <span key={i} className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full mr-1">{w}</span>
                  ))}
                </div>
              )}
              <div className="flex items-start gap-2">
                <TrendingUp className="w-4 h-4 text-purple-600 mt-0.5" />
                <div className="text-sm text-purple-700">{voiceAnalysis.suggestions.join('；')}</div>
              </div>
            </motion.div>
          )}
          
          <div className="flex items-end space-x-3">
            <button 
              onClick={() => isRecording ? stopVoiceRecording() : startVoiceRecording()}
              className={`p-3 rounded-xl transition-colors ${isRecording ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), send())}
              className="input w-full resize-none h-12 max-h-40 py-3"
              placeholder="输入回答（Shift+Enter 换行）..."
              disabled={evaluating}
              rows={1}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = Math.min(target.scrollHeight, 160) + 'px'
              }}
            />
          </div>
          <button 
            onClick={send} 
            disabled={evaluating || !input.trim()} 
            className={`p-3 rounded-xl transition-all ${
              evaluating || !input.trim() 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-primary-600 to-blue-600 text-white hover:shadow-lg'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500 text-sm py-4">
          面试已结束，正在生成复盘报告...
        </div>
      )}
    </div>
  )
}
