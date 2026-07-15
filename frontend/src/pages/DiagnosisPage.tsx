import { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { resumeApi } from '../services/api'
import RadarChart from '../components/charts/RadarChart'
import type { DiagnosisResult } from '../types'
import { Loader2, AlertCircle, CheckCircle, Wrench, Shield, Search, Tag, Sparkles, TrendingUp, Target, Copy, ArrowRight, RefreshCw } from 'lucide-react'

export default function DiagnosisPage() {
  const location = useLocation()
  const [resumeId, setResumeId] = useState<string>(location.state?.resumeId || '')
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiagnosisResult | null>(null)
  const [error, setError] = useState('')
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  useEffect(() => {
    if (location.state?.resumeId) {
      setResumeId(location.state.resumeId)
      handleDiagnose(location.state.resumeId, '')
    }
  }, [location.state])

  const handleDiagnose = async (rid?: string, desc?: string) => {
    const id = rid || resumeId
    if (!id) { setError('请先上传简历'); return }
    setLoading(true)
    setError('')
    try {
      const res = await resumeApi.diagnose(id, desc)
      setResult(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '诊断失败')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const radarData = result
    ? Object.entries(result.radar_scores).map(([k, v]) => ({
        subject: k === 'structure' ? '结构' : k === 'content' ? '内容' : k === 'keywords' ? '关键词' : k === 'quantify' ? '量化' : k === 'expression' ? '表达' : k === 'layout' ? '排版' : k,
        A: v,
        fullMark: 100,
      }))
    : []

  const ats = result?.ats_analysis
  const sectionNameMap: Record<string, string> = {
    education: '教育背景',
    experience: '工作/实习经历',
    projects: '项目经验',
    skills: '技能列表',
    contact: '联系方式',
  }

  const getScoreLevel = (score: number) => {
    if (score >= 80) return { label: '优秀', color: 'text-green-600', bg: 'bg-green-100' }
    if (score >= 60) return { label: '良好', color: 'text-yellow-600', bg: 'bg-yellow-100' }
    if (score >= 40) return { label: '一般', color: 'text-orange-600', bg: 'bg-orange-100' }
    return { label: '较差', color: 'text-red-600', bg: 'bg-red-100' }
  }

  const polishExamples = [
    {
      original: '负责网站开发',
      polished: '独立负责企业级官网从 0 到 1 的开发，日均访问量突破 10 万次',
      tips: '使用 STAR 法则，补充量化成果',
    },
    {
      original: '参与项目开发',
      polished: '作为核心开发成员参与电商平台重构项目，优化订单处理性能提升 300%',
      tips: '明确角色定位，突出贡献价值',
    },
    {
      original: '熟悉 Java',
      polished: '精通 Java 后端开发，深入理解 JVM 原理，主导过亿级数据量的性能调优',
      tips: '展示深度和实践经验',
    },
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">简历诊断报告</h1>
          <p className="text-gray-500 text-sm mt-1">AI 智能分析您的简历，提供专业优化建议</p>
        </div>
        {result && (
          <button
            onClick={() => handleDiagnose()}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            重新诊断
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">简历 ID</label>
            <input value={resumeId} onChange={(e) => setResumeId(e.target.value)} className="input" placeholder="输入简历 ID" />
          </div>
          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">目标岗位 JD（可选）</label>
            <textarea value={jd} onChange={(e) => setJd(e.target.value)} className="input h-32 resize-none" placeholder="粘贴岗位描述..." />
          </div>
          <button
            onClick={() => handleDiagnose()}
            disabled={loading}
            className="w-full btn-primary flex justify-center items-center space-x-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>开始诊断</span>
          </button>
          {error && (
            <div className="p-3 bg-red-50 rounded-xl flex items-center text-red-500 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              {error}
            </div>
          )}
        </div>

        <div className="lg:col-span-3 space-y-4">
          {loading && (
            <div className="card text-center py-12">
              <Loader2 className="w-10 h-10 text-primary-600 animate-spin mx-auto mb-3" />
              <p className="text-gray-600">AI 正在深度分析您的简历...</p>
            </div>
          )}

          {result && !loading && (
            <>
              {/* 综合评分卡片 */}
              <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">综合评分</h2>
                    <span className={`inline-block text-xs px-2 py-1 rounded-full mt-1 ${getScoreLevel(result.match_score).bg} ${getScoreLevel(result.match_score).color}`}>
                      {getScoreLevel(result.match_score).label}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-8 h-8 text-primary-500" />
                    <span className="text-5xl font-extrabold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                      {result.match_score.toFixed(0)}
                    </span>
                    <span className="text-gray-400 text-lg">/ 100</span>
                  </div>
                </div>
                
                {/* 评分进度条 */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>简历质量评分</span>
                    <span>{result.match_score.toFixed(0)}分</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-primary-500 to-blue-500 h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${result.match_score}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 能力雷达图 */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                    能力雷达图
                  </h3>
                  {radarData.length > 0 ? <RadarChart data={radarData} /> : <p className="text-gray-500 text-center py-8">暂无数据</p>}
                </div>

                {/* 维度评分 */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <Sparkles className="w-5 h-5 mr-2 text-primary-600" />
                    各维度评分
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(result.radar_scores).map(([k, v]) => (
                      <div key={k}>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-gray-700">
                            {k === 'structure' ? '结构' : k === 'content' ? '内容' : k === 'keywords' ? '关键词' : k === 'quantify' ? '量化' : k === 'expression' ? '表达' : k === 'layout' ? '排版' : k}
                          </span>
                          <span className={`font-bold text-sm ${getScoreLevel(v).color}`}>{v}分</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-700 ${v >= 80 ? 'bg-green-500' : v >= 60 ? 'bg-yellow-500' : v >= 40 ? 'bg-orange-500' : 'bg-red-500'}`}
                            style={{ width: `${v}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* ATS 兼容性分析 */}
              {ats && (
                <div className="card border-l-4 border-l-blue-500">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold flex items-center">
                      <Shield className="w-5 h-5 mr-2 text-blue-500" />
                      ATS 兼容性分析
                    </h3>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-500">关键词覆盖</span>
                      <span className={`text-sm font-medium ${ats.keyword_coverage >= 60 ? 'text-green-600' : 'text-orange-600'}`}>
                        {ats.keyword_coverage.toFixed(0)}%
                      </span>
                      <span className="text-2xl font-bold text-blue-600">{ats.overall_score.toFixed(0)}分</span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>ATS 兼容性</span>
                      <span>{ats.overall_score.toFixed(0)} / 100</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          ats.overall_score >= 80 ? 'bg-green-500' : ats.overall_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${ats.overall_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {ats.missing_sections.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">缺失模块</p>
                        <div className="flex flex-wrap gap-2">
                          {ats.missing_sections.map((s) => (
                            <span key={s} className="px-2 py-1 rounded text-xs bg-red-50 text-red-600 border border-red-200">
                              {sectionNameMap[s] || s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {ats.detected_keywords.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                          <Tag className="w-3.5 h-3.5 mr-1 text-green-500" />
                          已检测关键词
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {ats.detected_keywords.slice(0, 10).map((kw) => (
                            <span key={kw} className="px-2 py-0.5 rounded text-xs bg-green-50 text-green-700 border border-green-200">
                              {kw}
                            </span>
                          ))}
                          {ats.detected_keywords.length > 10 && (
                            <span className="px-2 py-0.5 text-xs text-gray-400">+{ats.detected_keywords.length - 10}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {ats.missing_keywords.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        <Search className="w-3.5 h-3.5 mr-1 text-orange-500" />
                        建议补充关键词
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {ats.missing_keywords.slice(0, 8).map((kw) => (
                          <span key={kw} className="px-2 py-0.5 rounded text-xs bg-orange-50 text-orange-600 border border-orange-200">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {ats.format_issues.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">格式问题</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {ats.format_issues.map((issue, i) => (
                          <li key={i} className="flex items-start">
                            <AlertCircle className="w-3.5 h-3.5 mr-1.5 mt-0.5 text-yellow-500 shrink-0" />
                            {issue}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* AI 润色示例 */}
              <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-purple-100">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                  AI 润色示例
                </h3>
                <p className="text-sm text-gray-600 mb-4">参考以下示例，将普通描述转化为数据化成果描述</p>
                <div className="space-y-4">
                  {polishExamples.map((ex, i) => (
                    <div key={i} className="bg-white rounded-xl p-4 border border-gray-100">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="text-xs text-gray-400 mb-1">原始描述</p>
                          <p className="text-gray-600 line-through">{ex.original}</p>
                          <p className="text-xs text-gray-400 mt-2 mb-1">润色后</p>
                          <p className="text-gray-900 font-medium">{ex.polished}</p>
                          <p className="text-xs text-green-600 mt-2 flex items-center">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            {ex.tips}
                          </p>
                        </div>
                        <button
                          onClick={() => copyToClipboard(ex.polished, i)}
                          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          {copiedIndex === i ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 分析总结 */}
              <div className="card">
                <h3 className="font-semibold mb-3 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  分析总结
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">{result.analysis}</p>
              </div>

              {/* 改进建议 */}
              <div className="card">
                <h3 className="font-semibold mb-3 flex items-center">
                  <Wrench className="w-4 h-4 mr-2 text-orange-500" />
                  改进建议
                </h3>
                <div className="space-y-3">
                  {result.suggestions.map((s, i) => (
                    <div key={i} className="flex items-start p-3 bg-gray-50 rounded-xl">
                      <div className="w-6 h-6 rounded-full bg-primary-500 text-white flex items-center justify-center text-xs font-bold mr-3 flex-shrink-0">
                        {i + 1}
                      </div>
                      <span className="text-sm text-gray-700">{s}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 技能缺口 */}
              {result.skill_gap && result.skill_gap.length > 0 && result.skill_gap[0] !== '暂无显著技能缺口' && (
                <div className="card border-l-4 border-l-orange-500">
                  <h3 className="font-semibold mb-3 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2 text-orange-500" />
                    技能缺口
                  </h3>
                  <ul className="text-sm text-gray-600 space-y-2">
                    {result.skill_gap.map((gap, i) => (
                      <li key={i} className="flex items-start">
                        <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 mr-2 flex-shrink-0" />
                        {gap}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 下一步行动 */}
              <div className="card bg-gray-50">
                <h3 className="font-semibold mb-3 flex items-center">
                  <ArrowRight className="w-4 h-4 mr-2 text-primary-600" />
                  下一步行动
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Link to="/matching" className="flex items-center p-3 bg-white rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all">
                    <Target className="w-5 h-5 mr-2 text-primary-600" />
                    <span className="text-sm font-medium text-gray-700">智能岗位匹配</span>
                  </Link>
                  <Link to="/interview" className="flex items-center p-3 bg-white rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all">
                    <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                    <span className="text-sm font-medium text-gray-700">AI 模拟面试</span>
                  </Link>
                  <Link to="/growth" className="flex items-center p-3 bg-white rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-sm transition-all">
                    <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                    <span className="text-sm font-medium text-gray-700">查看成长曲线</span>
                  </Link>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
