import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Radar, ArrowUp, Target, BookOpen, TrendingUp, Zap } from 'lucide-react'
import RadarChart from '../components/charts/RadarChart'
import { skillApi } from '../services/api'

interface SkillDimension {
  name: string
  score: number
  max_score: number
  description: string
  keywords: string[]
}

interface SkillRadarResponse {
  dimensions: SkillDimension[]
  job_fit_score: number
  suggested_skills: string[]
  improvement_path: string[]
}

interface SkillCategory {
  name: string
  skills: string[]
}

interface SkillGapAnalysis {
  required_skills: string[]
  matched_skills: string[]
  missing_skills: string[]
  gap_description: string
  learning_suggestions: string[]
}

const DOMAINS = [
  { value: 'default', label: '通用' },
  { value: 'frontend', label: '前端开发' },
  { value: 'backend', label: '后端开发' },
  { value: 'ai', label: 'AI/机器学习' },
  { value: 'test', label: '测试/QA' },
  { value: 'product', label: '产品经理' },
]

export default function SkillPage() {
  const [activeTab, setActiveTab] = useState<'radar' | 'tree' | 'gap'>('radar')
  const [radarData, setRadarData] = useState<SkillRadarResponse | null>(null)
  const [treeData, setTreeData] = useState<{ categories: SkillCategory[] } | null>(null)
  const [gapData, setGapData] = useState<SkillGapAnalysis | null>(null)
  const [selectedDomain, setSelectedDomain] = useState('default')
  const [jobDescription, setJobDescription] = useState('')
  const [resumeId, setResumeId] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchRadar()
    fetchTree()
  }, [])

  const fetchRadar = async () => {
    setLoading(true)
    try {
      const res = await skillApi.radar(resumeId || undefined, jobDescription || undefined)
      setRadarData(res.data)
    } catch (err) {
      console.error('Failed to fetch skill radar:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTree = async () => {
    try {
      const res = await skillApi.tree(selectedDomain)
      setTreeData(res.data)
    } catch (err) {
      console.error('Failed to fetch skill tree:', err)
    }
  }

  const analyzeGap = async () => {
    if (!resumeId || !jobDescription) return
    setLoading(true)
    try {
      const res = await skillApi.gap(resumeId, jobDescription)
      setGapData(res.data)
    } catch (err) {
      console.error('Failed to analyze skill gap:', err)
    } finally {
      setLoading(false)
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
            <Radar className="w-4 h-4" />
            技能图谱
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-3">技能能力全景分析</h1>
          <p className="text-gray-600">可视化你的技能结构，发现短板，规划成长路径</p>
        </motion.div>

        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-white rounded-xl shadow-sm border border-gray-100 p-1">
            {[
              { key: 'radar', label: '能力雷达', icon: Radar },
              { key: 'tree', label: '技能树', icon: BookOpen },
              { key: 'gap', label: '差距分析', icon: Target },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as typeof activeTab)}
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

        {activeTab === 'radar' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid lg:grid-cols-2 gap-8"
          >
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-primary-600" />
                能力雷达图
              </h2>
              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
                </div>
              ) : radarData ? (
                <RadarChart
                  data={radarData.dimensions.map((d) => ({
                    subject: d.name,
                    A: d.score,
                    fullMark: 100,
                  }))}
                />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Radar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p>暂无数据，请先上传简历</p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                  岗位匹配度
                </h2>
                {radarData && (
                  <div className="flex items-center gap-4">
                    <div className="relative w-32 h-32">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="#e5e7eb"
                          strokeWidth="12"
                          fill="none"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke={radarData.job_fit_score >= 80 ? '#10b981' : radarData.job_fit_score >= 60 ? '#f59e0b' : '#ef4444'}
                          strokeWidth="12"
                          fill="none"
                          strokeLinecap="round"
                          strokeDasharray={`${radarData.job_fit_score * 3.52} 352`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-3xl font-bold text-gray-900">{radarData.job_fit_score}</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-gray-600 mb-1">综合匹配分数</div>
                      <div className="text-xs text-gray-500">
                        {radarData.job_fit_score >= 80 ? '优秀，岗位匹配度很高' : radarData.job_fit_score >= 60 ? '良好，有一定竞争力' : '需加强，建议针对性提升'}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <ArrowUp className="w-5 h-5 mr-2 text-amber-600" />
                  补强建议
                </h2>
                {radarData?.suggested_skills && (
                  <ul className="space-y-2">
                    {radarData.suggested_skills.map((skill, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-start gap-2 text-gray-700"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-2 flex-shrink-0" />
                        {skill}
                      </motion.li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white">
                <h2 className="text-lg font-bold mb-3">成长路径</h2>
                {radarData?.improvement_path && (
                  <ol className="space-y-2">
                    {radarData.improvement_path.map((step, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-center gap-2"
                      >
                        <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs font-medium">
                          {i + 1}
                        </span>
                        {step}
                      </motion.li>
                    ))}
                  </ol>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'tree' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center">
                  <BookOpen className="w-5 h-5 mr-2 text-primary-600" />
                  技能树
                </h2>
                <select
                  value={selectedDomain}
                  onChange={(e) => {
                    setSelectedDomain(e.target.value)
                    fetchTree()
                  }}
                  className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {DOMAINS.map((d) => (
                    <option key={d.value} value={d.value}>{d.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {treeData?.categories.map((category, i) => (
                <motion.div
                  key={category.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-white rounded-xl shadow-md p-6 border border-gray-100"
                >
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                    <span className="w-6 h-6 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs mr-2">
                      {i + 1}
                    </span>
                    {category.name}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {category.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium hover:bg-primary-100 hover:text-primary-700 transition-colors"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'gap' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <Target className="w-5 h-5 mr-2 text-primary-600" />
              技能差距分析
            </h2>

            <div className="grid lg:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">简历 ID</label>
                <input
                  type="text"
                  value={resumeId}
                  onChange={(e) => setResumeId(e.target.value)}
                  placeholder="输入简历ID"
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">岗位 JD</label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="粘贴目标岗位的任职要求..."
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                />
              </div>
            </div>

            <button
              onClick={analyzeGap}
              disabled={!resumeId || !jobDescription || loading}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '分析中...' : '开始分析'}
            </button>

            {gapData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 space-y-6"
              >
                <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
                  <h3 className="font-bold text-amber-800 mb-2">{gapData.gap_description}</h3>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                    <h4 className="font-medium text-blue-800 mb-2">需求技能</h4>
                    <div className="flex flex-wrap gap-2">
                      {gapData.required_skills.map((skill) => (
                        <span key={skill} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-green-50 rounded-xl p-4 border border-green-100">
                    <h4 className="font-medium text-green-800 mb-2">已匹配</h4>
                    <div className="flex flex-wrap gap-2">
                      {gapData.matched_skills.map((skill) => (
                        <span key={skill} className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-red-50 rounded-xl p-4 border border-red-100">
                    <h4 className="font-medium text-red-800 mb-2">技能缺口</h4>
                    <div className="flex flex-wrap gap-2">
                      {gapData.missing_skills.map((skill) => (
                        <span key={skill} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-xl p-4">
                  <h4 className="font-medium text-gray-800 mb-2">学习建议</h4>
                  <ul className="space-y-2">
                    {gapData.learning_suggestions.map((suggestion, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-700">
                        <ArrowUp className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  )
}
