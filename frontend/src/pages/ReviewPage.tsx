import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { reviewApi } from '../services/api'
import RadarChart from '../components/charts/RadarChart'
import type { ReviewDetail } from '../types'
import { Loader2, AlertCircle, ChevronRight, Lightbulb, Star, TrendingUp, Target, Award, Clock, MessageSquare, RefreshCw, ArrowRight, BookOpen, CheckCircle } from 'lucide-react'

export default function ReviewPage() {
  const { reviewId } = useParams<{ reviewId?: string }>()
  const [review, setReview] = useState<ReviewDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (reviewId) {
      setLoading(true)
      reviewApi.get(reviewId)
        .then((res) => setReview(res.data))
        .catch((err) => setError(err.response?.data?.detail || '加载失败'))
        .finally(() => setLoading(false))
    }
  }, [reviewId])

  const radarData = review
    ? Object.entries(review.radar_data).map(([k, v]) => ({ subject: k, A: v, fullMark: 100 }))
    : []

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const getScoreBarBg = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getLevel = (score: number) => {
    if (score >= 90) return { label: '优秀', emoji: '🏆' }
    if (score >= 80) return { label: '良好', emoji: '👍' }
    if (score >= 70) return { label: '合格', emoji: '✅' }
    if (score >= 60) return { label: '需提升', emoji: '💪' }
    return { label: '待改进', emoji: '📚' }
  }

  const priorityColors: Record<string, string> = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200',
  }

  const priorityLabels: Record<string, string> = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级',
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <Award className="w-6 h-6 mr-2 text-primary-600" />
        面试复盘报告
      </h1>
      
      {loading && <div className="flex items-center text-gray-500"><Loader2 className="w-5 h-5 animate-spin mr-2" />加载中...</div>}
      {error && <p className="text-red-500 flex items-center"><AlertCircle className="w-4 h-4 mr-1" />{error}</p>}
      
      {!reviewId && !review && !loading && (
        <div className="card text-center py-16 text-gray-500">
          <Target className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-lg">暂无复盘报告</p>
          <p className="text-sm mt-2">请先完成一次 AI 面试，系统会自动生成复盘报告。</p>
        </div>
      )}

      {review && (
        <div className="space-y-6">
          {/* 总体评分 */}
          <div className="card text-center bg-gradient-to-br from-primary-50 to-blue-50 border-primary-100">
            <div className="text-6xl font-extrabold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent mb-2">
              {review.overall_score}
            </div>
            <div className="flex items-center justify-center gap-2">
              <span className="text-2xl">{getLevel(review.overall_score).emoji}</span>
              <span className={`text-lg font-semibold ${getScoreColor(review.overall_score)}`}>
                {getLevel(review.overall_score).label}
              </span>
            </div>
            <p className="text-gray-500 text-sm mt-2">综合评分</p>
            
            {/* 评分进度条 */}
            <div className="max-w-xs mx-auto mt-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className={`h-4 rounded-full transition-all duration-1000 ${getScoreBarBg(review.overall_score)}`} 
                  style={{ width: `${review.overall_score}%` }} 
                />
              </div>
            </div>
          </div>

          {/* 能力雷达图 */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-primary-600" />
              能力雷达图
            </h2>
            {radarData.length > 0 ? (
              <div className="flex justify-center">
                <RadarChart data={radarData} />
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">暂无数据</p>
            )}
          </div>

          {/* 维度详情 */}
          {review.radar_data && Object.keys(review.radar_data).length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                各维度详情
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {Object.entries(review.radar_data).map(([k, v]) => (
                  <div key={k} className={`p-4 rounded-xl ${getScoreBg(v)}`}>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getScoreColor(v)}`}>{v}</div>
                      <div className="text-xs text-gray-600 mt-1">{k}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 面试官视角 */}
          <div className="card bg-gray-50 border-gray-100">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Star className="w-5 h-5 mr-2 text-yellow-500" />
              面试官视角
            </h2>
            <div className="p-4 bg-white rounded-lg border border-gray-100">
              <p className="text-gray-600 text-sm leading-relaxed">{review.interviewer_summary}</p>
            </div>
          </div>

          {/* 逐题点评 */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">逐题点评</h2>
            <div className="space-y-4">
              {review.question_reviews.map((qr, i) => (
                <div key={i} className="border border-gray-100 rounded-xl p-4 hover:border-primary-200 hover:shadow-sm transition-all">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-900 flex items-center">
                        <ChevronRight className="w-4 h-4 mr-2 text-primary-500" />
                        {qr.question}
                      </span>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">{qr.answer_summary}</p>
                    </div>
                    <div className={`flex items-center gap-1 px-3 py-1.5 rounded-full ${getScoreBg(qr.score)}`}>
                      <Star className="w-4 h-4 fill-current" />
                      <span className={`font-bold ${getScoreColor(qr.score)}`}>{qr.score}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {qr.strengths.map((s, j) => (
                      <span key={j} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full border border-green-100">
                        ✅ {s}
                      </span>
                    ))}
                    {qr.improvements.map((s, j) => (
                      <span key={j} className="text-xs bg-orange-50 text-orange-700 px-2 py-1 rounded-full border border-orange-100">
                        🔧 {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 改进建议 */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
              改进建议
            </h2>
            <div className="space-y-4">
              {review.suggestions.map((s, i) => (
                <div key={i} className={`p-4 rounded-xl border ${priorityColors[s.priority]}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold">{s.dimension}</span>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-white/50">
                      {priorityLabels[s.priority]}
                    </span>
                  </div>
                  <p className="text-sm">{s.action}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 面试时间统计 */}
        <div className="card bg-gray-50">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-primary-600" />
            面试统计
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-primary-600">{review.question_reviews.length}</div>
              <div className="text-xs text-gray-500 mt-1">回答题目</div>
            </div>
            <div className="bg-white rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {review.question_reviews.filter(qr => qr.score >= 80).length}
              </div>
              <div className="text-xs text-gray-500 mt-1">高分回答</div>
            </div>
            <div className="bg-white rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {review.question_reviews.filter(qr => qr.score >= 60 && qr.score < 80).length}
              </div>
              <div className="text-xs text-gray-500 mt-1">中等回答</div>
            </div>
            <div className="bg-white rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-red-600">
                {review.question_reviews.filter(qr => qr.score < 60).length}
              </div>
              <div className="text-xs text-gray-500 mt-1">需改进</div>
            </div>
          </div>
        </div>

        {/* 面试技巧指南 */}
        <div className="card bg-gradient-to-br from-blue-50 to-purple-50 border-blue-100">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <BookOpen className="w-5 h-5 mr-2 text-blue-600" />
            面试技巧指南
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'STAR 法则', desc: '情境(Situation)、任务(Task)、行动(Action)、结果(Result)', icon: CheckCircle, color: 'text-green-600 bg-green-50' },
              { title: '金字塔原理', desc: '先讲结论，再分点阐述，逻辑清晰', icon: TrendingUp, color: 'text-blue-600 bg-blue-50' },
              { title: '反问技巧', desc: '回答完后适当反问，展示主动性', icon: MessageSquare, color: 'text-purple-600 bg-purple-50' },
              { title: '时间管理', desc: '每个问题控制在 1-3 分钟，重点突出', icon: Clock, color: 'text-orange-600 bg-orange-50' },
            ].map((tip, i) => (
              <div key={i} className="bg-white rounded-xl p-4 border border-gray-100">
                <div className={`w-10 h-10 rounded-lg ${tip.color} flex items-center justify-center mb-3`}>
                  <tip.icon className="w-5 h-5" />
                </div>
                <h4 className="font-semibold text-gray-900 text-sm">{tip.title}</h4>
                <p className="text-xs text-gray-500 mt-1">{tip.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 下一步行动建议 */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <ArrowRight className="w-5 h-5 mr-2 text-primary-600" />
            下一步行动
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/interview" className="flex flex-col items-center p-4 bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl border border-primary-200 hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center mb-3">
                <RefreshCw className="w-6 h-6 text-primary-600" />
              </div>
              <span className="font-medium text-gray-900">再次模拟面试</span>
              <span className="text-xs text-gray-500 mt-1">针对薄弱项专项练习</span>
            </Link>
            <Link to="/matching" className="flex flex-col items-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200 hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-3">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <span className="font-medium text-gray-900">智能岗位匹配</span>
              <span className="text-xs text-gray-500 mt-1">发现更适合的机会</span>
            </Link>
            <Link to="/growth" className="flex flex-col items-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200 hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-3">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <span className="font-medium text-gray-900">查看成长曲线</span>
              <span className="text-xs text-gray-500 mt-1">追踪能力进步轨迹</span>
            </Link>
          </div>
        </div>

        {/* 底部信息 */}
        <div className="text-center text-sm text-gray-400 flex items-center justify-center gap-4">
          <span className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            {review.created_at}
          </span>
        </div>
      </div>
      )}
    </div>
  )
}