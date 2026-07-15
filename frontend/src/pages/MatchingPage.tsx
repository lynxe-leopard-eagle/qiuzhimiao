import { useState, useEffect } from 'react'
import { jobApi, resumeApi } from '../services/api'
import type { JobAnalysis, MatchingResult, Job, Resume } from '../types'
import {
  Loader2,
  AlertCircle,
  Target,
  CheckCircle,
  XCircle,
  ArrowRight,
  Star,
  TrendingUp,
  TrendingDown,
  Zap,
  Briefcase,
  GraduationCap,
  Clock,
  DollarSign,
  BarChart3,
  TrendingUp as TrendingUpIcon,
  Sparkles,
  BookOpen,
  Award,
  RefreshCw,
  FileText,
  Bot,
} from 'lucide-react'

export default function MatchingPage() {
  const [resumeId, setResumeId] = useState('')
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null)
  const [matchResult, setMatchResult] = useState<MatchingResult | null>(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'both' | 'job' | 'match'>('both')
  const [jobs, setJobs] = useState<Job[]>([])
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loadingPreset, setLoadingPreset] = useState(true)

  useEffect(() => {
    loadPresetData()
  }, [])

  const loadPresetData = async () => {
    setLoadingPreset(true)
    try {
      const [resJobs, resResumes] = await Promise.all([
        jobApi.list(),
        resumeApi.list(),
      ])
      setJobs(resJobs.data)
      setResumes(resResumes.data)
      if (resJobs.data.length > 0) {
        setJd(resJobs.data[0].description || '')
      }
      if (resResumes.data.length > 0) {
        setResumeId(resResumes.data[0].id)
      }
    } catch (err) {
      console.error('加载预置数据失败:', err)
    } finally {
      setLoadingPreset(false)
    }
  }

  const selectJob = (job: Job) => {
    setJd(job.description || '')
    setJobAnalysis(null)
    setMatchResult(null)
  }

  const selectResume = (resume: Resume) => {
    setResumeId(resume.id)
    setMatchResult(null)
  }

  const handleAnalyze = async () => {
    if (!jd) {
      setError('请输入岗位描述')
      return
    }
    setLoading(true)
    setError('')
    setJobAnalysis(null)
    setMatchResult(null)
    try {
      const res = await jobApi.analyze(jd)
      setJobAnalysis(res.data)

      if (resumeId) {
        try {
          const matchRes = await jobApi.match(resumeId, jd)
          setMatchResult(matchRes.data)
        } catch (matchErr: any) {
          console.error('匹配分析失败:', matchErr)
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getMatchLevel = (score: number) => {
    if (score >= 90) return { label: '非常匹配', color: 'bg-green-100 text-green-700' }
    if (score >= 80) return { label: '匹配度高', color: 'bg-emerald-100 text-emerald-700' }
    if (score >= 70) return { label: '良好匹配', color: 'bg-yellow-100 text-yellow-700' }
    if (score >= 60) return { label: '有机会', color: 'bg-orange-100 text-orange-700' }
    return { label: '需要提升', color: 'bg-red-100 text-red-700' }
  }

  const getDifficultyLevel = (score: number) => {
    if (score >= 80) return { label: '难度很高', color: 'text-red-600 bg-red-50' }
    if (score >= 60) return { label: '难度中等', color: 'text-yellow-600 bg-yellow-50' }
    return { label: '难度较低', color: 'text-green-600 bg-green-50' }
  }

  const resetForm = () => {
    setJobAnalysis(null)
    setMatchResult(null)
    setJd('')
    setResumeId('')
    setActiveTab('both')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">岗位分析与匹配</h1>
          <p className="text-gray-500 text-sm mt-1">AI 深度解析岗位 JD，量化简历匹配度，精准定位差距</p>
        </div>
        {(jobAnalysis || matchResult) && (
          <button onClick={resetForm} className="btn-secondary flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            新分析
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 space-y-4">
          {loadingPreset && (
            <div className="card text-center py-4">
              <Loader2 className="w-5 h-5 text-primary-600 animate-spin mx-auto" />
              <p className="text-sm text-gray-500 mt-2">加载参考数据...</p>
            </div>
          )}

          {!loadingPreset && jobs.length > 0 && (
            <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Briefcase className="w-4 h-4 inline mr-1.5 -mt-0.5 text-primary-600" />
                选择参考岗位 <span className="text-gray-400 font-normal">（快速填充 JD）</span>
              </label>
              <div className="space-y-2">
                {jobs.map((job) => (
                  <button
                    key={job.id}
                    onClick={() => selectJob(job)}
                    className={`w-full text-left p-3 rounded-xl transition-colors text-sm ${
                      jd.includes(job.title || '')
                        ? 'bg-white border-2 border-primary-500 shadow-sm'
                        : 'bg-white/50 border border-transparent hover:bg-white hover:border-primary-200'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{job.title}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{job.company}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FileText className="w-4 h-4 inline mr-1.5 -mt-0.5 text-primary-600" />
              岗位 JD
            </label>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              className="input h-64 resize-none"
              placeholder="粘贴岗位描述（JD）..."
            />
            <p className="text-xs text-gray-400 mt-2">
              支持粘贴完整的岗位招聘信息，包含岗位职责、任职要求等内容
            </p>
          </div>

          {!loadingPreset && resumes.length > 0 && (
            <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-100">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Award className="w-4 h-4 inline mr-1.5 -mt-0.5 text-green-600" />
                选择参考简历 <span className="text-gray-400 font-normal">（进行匹配分析）</span>
              </label>
              <div className="space-y-2">
                {resumes.map((resume) => (
                  <button
                    key={resume.id}
                    onClick={() => selectResume(resume)}
                    className={`w-full text-left p-3 rounded-xl transition-colors text-sm ${
                      resumeId === resume.id
                        ? 'bg-white border-2 border-green-500 shadow-sm'
                        : 'bg-white/50 border border-transparent hover:bg-white hover:border-green-200'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{resume.original_filename}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      状态: {resume.status} | 置信度: {Math.round((resume.confidence || 0) * 100)}%
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Award className="w-4 h-4 inline mr-1.5 -mt-0.5 text-primary-600" />
              简历 ID <span className="text-gray-400 font-normal">（选填）</span>
            </label>
            <input
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="input"
              placeholder="输入简历 ID 进行匹配分析"
            />
            <p className="text-xs text-gray-400 mt-2">
              填写简历 ID 后将同时进行匹配度分析
            </p>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !jd}
            className="w-full btn-primary flex justify-center items-center space-x-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{loading ? 'AI 分析中...' : resumeId ? '开始岗位分析 + 匹配' : '开始岗位分析'}</span>
          </button>

          {error && (
            <div className="p-3 bg-red-50 rounded-xl flex items-center text-red-500 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              {error}
            </div>
          )}

          <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <Sparkles className="w-4 h-4 mr-2 text-primary-600" />
              分析维度
            </h4>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-start">
                <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                <span>岗位基本信息提取（级别、经验、学历、薪资）</span>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                <span>核心技能与加分项识别</span>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                <span>岗位职责与硬性要求梳理</span>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                <span>岗位难度评估与市场需求分析</span>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                <span>简历匹配度四维评估（需简历ID）</span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 space-y-4">
          {loading && (
            <div className="card text-center py-16">
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600 text-lg">AI 正在深度分析岗位信息...</p>
              <p className="text-gray-400 text-sm mt-2">提取关键信息、评估难度、分析市场前景</p>
            </div>
          )}

          {!loading && !jobAnalysis && (
            <div className="card text-center py-16">
              <div className="w-20 h-20 bg-primary-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-10 h-10 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">准备好开始了吗？</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                粘贴岗位 JD，AI 将为你生成详细的岗位分析报告。
                同时输入简历 ID，还能获得精准的匹配度分析和改进建议。
              </p>
            </div>
          )}

          {jobAnalysis && (
            <>
              {resumeId && (
                <div className="flex gap-2 mb-2">
                  <button
                    onClick={() => setActiveTab('both')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'both'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    全部
                  </button>
                  <button
                    onClick={() => setActiveTab('job')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'job'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    岗位分析
                  </button>
                  <button
                    onClick={() => setActiveTab('match')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === 'match'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    匹配分析
                  </button>
                </div>
              )}

              {(activeTab === 'both' || activeTab === 'job') && (
                <div className="space-y-4">
                  <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Briefcase className="w-5 h-5 text-blue-600" />
                          <h3 className="font-bold text-lg text-gray-900">
                            {jobAnalysis.title || '岗位分析报告'}
                          </h3>
                          {jobAnalysis.company && (
                            <span className="text-sm text-gray-500">· {jobAnalysis.company}</span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{jobAnalysis.summary}</p>
                      </div>
                      <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${getDifficultyLevel(jobAnalysis.difficulty_score).color}`}>
                        <BarChart3 className="w-4 h-4" />
                        {jobAnalysis.difficulty_score}分
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
                      <div className="bg-white rounded-xl p-3 border border-gray-100">
                        <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1">
                          <TrendingUpIcon className="w-3.5 h-3.5" />
                          岗位级别
                        </div>
                        <div className="font-semibold text-gray-900">{jobAnalysis.job_level || '—'}</div>
                      </div>
                      <div className="bg-white rounded-xl p-3 border border-gray-100">
                        <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1">
                          <Clock className="w-3.5 h-3.5" />
                          工作经验
                        </div>
                        <div className="font-semibold text-gray-900">{jobAnalysis.experience_required || '—'}</div>
                      </div>
                      <div className="bg-white rounded-xl p-3 border border-gray-100">
                        <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1">
                          <GraduationCap className="w-3.5 h-3.5" />
                          学历要求
                        </div>
                        <div className="font-semibold text-gray-900">{jobAnalysis.education_required || '—'}</div>
                      </div>
                      <div className="bg-white rounded-xl p-3 border border-gray-100">
                        <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1">
                          <DollarSign className="w-3.5 h-3.5" />
                          薪资范围
                        </div>
                        <div className="font-semibold text-gray-900">{jobAnalysis.salary_range || '—'}</div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {jobAnalysis.core_skills.length > 0 && (
                      <div className="card">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <Zap className="w-4 h-4 mr-2 text-yellow-500" />
                          核心技能要求
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {jobAnalysis.core_skills.map((skill, i) => (
                            <span
                              key={i}
                              className="px-2.5 py-1 bg-yellow-50 text-yellow-700 rounded-lg text-sm font-medium border border-yellow-100"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {jobAnalysis.bonus_skills.length > 0 && (
                      <div className="card">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <Sparkles className="w-4 h-4 mr-2 text-purple-500" />
                          加分项技能
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {jobAnalysis.bonus_skills.map((skill, i) => (
                            <span
                              key={i}
                              className="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium border border-purple-100"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {jobAnalysis.responsibilities.length > 0 && (
                      <div className="card">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <BookOpen className="w-4 h-4 mr-2 text-blue-500" />
                          岗位职责
                        </h4>
                        <ul className="space-y-2">
                          {jobAnalysis.responsibilities.map((resp, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start">
                              <span className="text-blue-500 mr-2 mt-0.5">•</span>
                              <span>{resp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {jobAnalysis.hard_requirements.length > 0 && (
                      <div className="card">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                          任职要求
                        </h4>
                        <ul className="space-y-2">
                          {jobAnalysis.hard_requirements.map((req, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start">
                              <span className="text-green-500 mr-2 mt-0.5">•</span>
                              <span>{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="card border-l-4 border-l-yellow-500">
                      <h4 className="font-semibold text-gray-900 mb-2 text-sm">面试难度</h4>
                      <div className="flex items-center gap-3">
                        <div className="text-2xl font-bold text-gray-900">
                          {jobAnalysis.difficulty_score}
                        </div>
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${getScoreBg(jobAnalysis.difficulty_score)}`}
                              style={{ width: `${jobAnalysis.difficulty_score}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {getDifficultyLevel(jobAnalysis.difficulty_score).label}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="card border-l-4 border-l-green-500">
                      <h4 className="font-semibold text-gray-900 mb-2 text-sm">市场需求</h4>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        <span className="font-semibold text-gray-900">
                          {jobAnalysis.market_demand || '—'}
                        </span>
                      </div>
                    </div>

                    <div className="card border-l-4 border-l-blue-500">
                      <h4 className="font-semibold text-gray-900 mb-2 text-sm">职业前景</h4>
                      <p className="text-sm text-gray-600">{jobAnalysis.career_outlook || '—'}</p>
                    </div>
                  </div>
                </div>
              )}

              {(activeTab === 'both' || activeTab === 'match') && matchResult && (
                <div className="space-y-4">
                  {activeTab === 'both' && (
                    <div className="flex items-center gap-2 pt-2">
                      <div className="flex-1 h-px bg-gray-200" />
                      <span className="text-sm text-gray-400 px-2">简历匹配分析</span>
                      <div className="flex-1 h-px bg-gray-200" />
                    </div>
                  )}

                  <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">匹配度评估</h3>
                        <span className={`inline-block text-xs px-2 py-1 rounded-full mt-1 ${getMatchLevel(matchResult.match_score).color}`}>
                          {getMatchLevel(matchResult.match_score).label}
                        </span>
                      </div>
                      <div className={`flex items-center gap-2 px-5 py-3 rounded-full ${getScoreColor(matchResult.match_score)}`}>
                        <Star className="w-6 h-6 fill-current" />
                        <span className="text-3xl font-bold">{matchResult.match_score}</span>
                      </div>
                    </div>

                    <div className="mt-4">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>综合匹配度</span>
                        <span>{matchResult.match_score} / 100</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all duration-1000 ${getScoreBg(matchResult.match_score)}`}
                          style={{ width: `${matchResult.match_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="mt-4 p-4 bg-white rounded-xl border border-gray-100">
                      <p className="text-sm text-gray-700 flex items-start">
                        <Zap className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-primary-500" />
                        {matchResult.match_score >= 80
                          ? '你的背景已经非常符合该岗位的核心要求，建议重点准备技术面试环节，突出你的相关项目经验。'
                          : matchResult.match_score >= 60
                          ? '你的背景与岗位有一定匹配度，但在某些关键领域仍需补充。建议根据下面的差距分析有针对性地优化简历和准备面试。'
                          : '当前匹配度较低，建议仔细分析差距并制定提升计划，重点补充核心技术栈和项目经验。'}
                      </p>
                    </div>
                  </div>

                  {matchResult.match_reasons && (
                    <div className="card">
                      <h3 className="font-semibold mb-4 flex items-center">
                        <Bot className="w-5 h-5 mr-2 text-primary-600" />
                        AI 匹配分析
                      </h3>
                      <div className="space-y-3">
                        <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                          <div className="flex items-center gap-2 mb-2">
                            <Zap className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-semibold text-blue-800">匹配理由</span>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {matchResult.match_reasons.why_match}
                          </p>
                        </div>

                        {matchResult.match_reasons.advantages.length > 0 && (
                          <div className="p-4 bg-green-50 rounded-xl border border-green-100">
                            <div className="flex items-center gap-2 mb-2">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              <span className="text-sm font-semibold text-green-800">核心优势</span>
                            </div>
                            <ul className="space-y-1.5">
                              {matchResult.match_reasons.advantages.map((a, i) => (
                                <li key={i} className="text-sm text-gray-700 flex items-start">
                                  <span className="text-green-500 mr-2 mt-0.5">•</span>
                                  <span>{a}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {matchResult.match_reasons.gaps.length > 0 && (
                          <div className="p-4 bg-orange-50 rounded-xl border border-orange-100">
                            <div className="flex items-center gap-2 mb-2">
                              <AlertCircle className="w-4 h-4 text-orange-600" />
                              <span className="text-sm font-semibold text-orange-800">关键差距</span>
                            </div>
                            <ul className="space-y-1.5">
                              {matchResult.match_reasons.gaps.map((g, i) => (
                                <li key={i} className="text-sm text-gray-700 flex items-start">
                                  <span className="text-orange-500 mr-2 mt-0.5">•</span>
                                  <span>{g}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="card">
                    <h3 className="font-semibold mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-primary-600" />
                      维度评分
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(matchResult.dimensions).map(([k, v]) => (
                        <div key={k} className="p-3 bg-gray-50 rounded-xl">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">{k}</span>
                            <div className="flex items-center gap-2">
                              {v >= 80 ? (
                                <TrendingUp className="w-3.5 h-3.5 text-green-500" />
                              ) : v < 60 ? (
                                <TrendingDown className="w-3.5 h-3.5 text-red-500" />
                              ) : null}
                              <span className={`font-bold text-lg ${getScoreColor(v).split(' ')[0]}`}>
                                {v}
                              </span>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all duration-700 ${getScoreBg(v)}`}
                              style={{ width: `${v}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {matchResult.strengths.length > 0 && (
                    <div className="card border-l-4 border-l-green-500">
                      <h3 className="font-semibold mb-3 flex items-center">
                        <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                        你的优势
                      </h3>
                      <div className="space-y-2">
                        {matchResult.strengths.map((s, i) => (
                          <div key={i} className="flex items-start p-2 bg-green-50 rounded-lg">
                            <CheckCircle className="w-4 h-4 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{s}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(matchResult.weaknesses.length > 0 || matchResult.gaps.length > 0) && (
                    <div className="card border-l-4 border-l-red-500">
                      <h3 className="font-semibold mb-3 flex items-center">
                        <XCircle className="w-5 h-5 mr-2 text-red-600" />
                        需要改进的方面
                      </h3>
                      <div className="space-y-2">
                        {matchResult.weaknesses.map((s, i) => (
                          <div key={i} className="flex items-start p-2 bg-red-50 rounded-lg">
                            <XCircle className="w-4 h-4 mr-2 mt-0.5 text-red-500 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{s}</span>
                          </div>
                        ))}
                        {matchResult.gaps.map((s, i) => (
                          <div key={i} className="flex items-start p-2 bg-yellow-50 rounded-lg">
                            <AlertCircle className="w-4 h-4 mr-2 mt-0.5 text-yellow-500 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{s}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
                    <h3 className="font-semibold mb-3 flex items-center">
                      <ArrowRight className="w-5 h-5 mr-2 text-primary-600" />
                      行动建议
                    </h3>
                    <div className="space-y-2">
                      {matchResult.suggestion
                        .split('。')
                        .filter(Boolean)
                        .map((sentence, i) => (
                          <p key={i} className="text-sm text-gray-700">
                            {sentence}。
                          </p>
                        ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
