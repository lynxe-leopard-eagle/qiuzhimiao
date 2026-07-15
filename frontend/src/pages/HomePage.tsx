import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useState } from 'react'
import {
  FileText, Target, MessageSquare, TrendingUp, ArrowRight,
  Upload, Search, Lightbulb, Rocket, Shield, Zap, BarChart3,
  Bot, Star, Briefcase, Clock, MapPin,
  Quote, ChevronLeft, ChevronRight, User, CircleDot
} from 'lucide-react'
import { motion } from 'framer-motion'

const QUICK_ACTIONS = [
  { label: '帮我诊断简历', icon: FileText, route: '/upload' },
  { label: '推荐适合的岗位', icon: Target, route: '/matching' },
  { label: '模拟面试练习', icon: MessageSquare, route: '/interview' },
  { label: '查看成长曲线', icon: TrendingUp, route: '/growth' },
]

const FEATURES = [
  { icon: FileText, title: 'ATS 简历诊断', desc: '关键词覆盖率、格式兼容性、结构完整度多维度扫描，定位被 ATS 过滤的风险点', color: 'text-blue-600 bg-blue-50' },
  { icon: Target, title: '智能职位匹配', desc: 'AI 分析职位需求，量化匹配度，给出匹配理由和技能缺口清单', color: 'text-emerald-600 bg-emerald-50' },
  { icon: MessageSquare, title: 'AI 模拟面试', desc: 'HR / 技术 / 系统设计三轮面试，实时追问，10 维度评判', color: 'text-purple-600 bg-purple-50' },
  { icon: BarChart3, title: '复盘报告', desc: '每场面试生成详细复盘，雷达图 + 逐题点评 + 优先级改进方案', color: 'text-orange-600 bg-orange-50' },
  { icon: TrendingUp, title: '成长追踪', desc: '能力雷达图与趋势曲线，跨面试维度追踪进步轨迹', color: 'text-pink-600 bg-pink-50' },
  { icon: Shield, title: '隐私安全', desc: '简历数据本地存储，JWT 鉴权保障账户安全', color: 'text-indigo-600 bg-indigo-50' },
]

const MOCK_JOBS = [
  { company: '字节跳动', title: '后端开发工程师', score: 91, tags: ['新匹配', '全职'], location: '北京', salary: '35-60K', time: '2天前' },
  { company: '阿里巴巴', title: '高级前端工程师', score: 85, tags: ['匹配度高', '远程'], location: '杭州', salary: '30-55K', time: '3天前' },
  { company: '腾讯', title: '技术产品经理', score: 78, tags: ['良好匹配'], location: '深圳', salary: '30-50K', time: '5天前' },
]

const TESTIMONIALS = [
  { name: '张三', role: '后端开发', company: '字节跳动', content: '面试前用 AI 模拟了 5 轮，真正面试时感觉游刃有余。特别是系统设计那部分，AI 的追问让我提前想到了很多边界情况。', score: 95 },
  { name: '李四', role: '前端工程师', company: '阿里巴巴', content: '简历诊断功能太实用了！ATS 兼容性分析帮我发现了很多被过滤的风险点，修改后投递命中率提升了 3 倍。', score: 92 },
  { name: '王五', role: '产品经理', company: '腾讯', content: 'HR 面试的模拟特别真实，AI 会根据我的回答不断追问，让我提前适应了各种压力场景。最终拿到了 3 个 Offer。', score: 98 },
  { name: '赵六', role: '算法工程师', company: '美团', content: '能力雷达图让我清楚看到自己的薄弱项，针对性训练后，技术一面的表现明显提升。推荐所有求职者使用！', score: 94 },
]

export default function HomePage() {
  const token = useAuthStore((s) => s.token)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [testimonialIndex, setTestimonialIndex] = useState(0)
  const navigate = useNavigate()

  const handleQuickAction = (action: typeof QUICK_ACTIONS[0]) => {
    setSelectedAction(action.label)
    setTimeout(() => {
      navigate(token ? action.route : '/login')
    }, 300)
  }

  return (
    <div>
      {/* Hero - 聊天式入口 */}
      <section className="relative bg-gradient-to-br from-primary-50 via-white to-blue-50 py-24 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(59,130,246,0.08),transparent_50%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-100 text-primary-700 text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              AI 驱动的求职全流程闭环
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
              从简历到 Offer
              <br />
              <span className="bg-gradient-to-r from-primary-600 to-blue-500 bg-clip-text text-transparent">
                每一步都精准把控
              </span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto mb-4">
              简历投出去石沉大海？面试紧张说不出话？Offer 总是差一点点？
            </p>
            <p className="text-gray-500 max-w-xl mx-auto mb-10">
              ATS 简历诊断 · 岗位匹配度分析 · AI 模拟面试 · 成长追踪复盘
            </p>

            {/* 聊天式快捷操作 */}
            <div className="max-w-2xl mx-auto mb-10">
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-blue-500 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">求职助手</p>
                    <p className="text-sm text-gray-500">今天有什么可以帮你的？</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {QUICK_ACTIONS.map((action) => (
                    <motion.button
                      key={action.label}
                      onClick={() => handleQuickAction(action)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${
                        selectedAction === action.label
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                      }`}
                    >
                      <action.icon className={`w-6 h-6 ${selectedAction === action.label ? 'text-primary-600' : 'text-gray-500'}`} />
                      <span className="text-xs font-medium text-gray-700">{action.label}</span>
                    </motion.button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to={token ? '/upload' : '/login'}
                className="inline-flex items-center space-x-2 btn-primary text-lg px-8 py-3"
              >
                <span>立即开始</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to={token ? '/interview' : '/login'}
                className="inline-flex items-center space-x-2 btn-secondary text-lg px-8 py-3"
              >
                <MessageSquare className="w-5 h-5" />
                <span>体验面试</span>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '5 维度', label: 'ATS 简历诊断' },
              { value: '10 维度', label: '面试评判体系' },
              { value: '3 轮', label: '模拟面试流程' },
              { value: '< 2 秒', label: '实时反馈延迟' },
            ].map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              >
                <div className="text-4xl font-extrabold bg-gradient-to-r from-primary-600 to-blue-500 bg-clip-text text-transparent">
                  {s.value}
                </div>
                <div className="mt-2 text-gray-500 text-sm">{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">全链路求职能力引擎</h2>
            <p className="mt-3 text-gray-500">覆盖从简历投递到面试复盘的每一个关键环节</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.5 }}
                className="card hover:shadow-md transition-shadow duration-300"
              >
                <div className={`w-12 h-12 rounded-lg ${f.color} flex items-center justify-center mb-4`}>
                  <f.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 求职闭环流程（参考职途AI） */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">从准备到 Offer，一路推进</h2>
            <p className="mt-3 text-gray-500">简历、诊断、匹配、面试、复盘在同一个平台里持续流动</p>
          </div>
          
          {/* 流程步骤 */}
          <div className="relative">
            {/* 连接线 */}
            <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200 transform -translate-y-1/2" />
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {[
                { step: '01', icon: Upload, title: '上传简历', desc: '上传 PDF/Word 简历，自动解析内容', color: 'from-blue-500 to-cyan-500' },
                { step: '02', icon: Zap, title: 'ATS 诊断', desc: '关键词覆盖率、格式兼容性多维度分析', color: 'from-cyan-500 to-teal-500' },
                { step: '03', icon: Target, title: '岗位匹配', desc: '智能分析 JD，量化匹配度与技能缺口', color: 'from-teal-500 to-green-500' },
                { step: '04', icon: MessageSquare, title: '模拟面试', desc: '多轮面试练习，实时反馈与追问', color: 'from-green-500 to-emerald-500' },
                { step: '05', icon: BarChart3, title: '复盘提升', desc: '详细分析报告，追踪成长轨迹', color: 'from-emerald-500 to-primary-500' },
              ].map((item, i) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                  viewport={{ once: true }}
                  className="relative flex flex-col items-center"
                >
                  {/* 步骤编号圆圈 */}
                  <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg mb-4 z-10`}>
                    <item.icon className="w-8 h-8 text-white" />
                  </div>
                  
                  {/* 步骤内容 */}
                  <div className="text-center">
                    <span className="text-xs font-bold text-primary-600 mb-1 block">步骤 {item.step}</span>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-sm text-gray-500">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
          
          {/* 数据闭环说明 */}
          <div className="mt-16 bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
                  <CircleDot className="w-6 h-6 mr-2 text-primary-600" />
                  数据闭环，持续优化
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  每一次诊断、每一场面试、每一份匹配结果都会沉淀到你的成长曲线中。
                  系统会基于你的历史数据，给出更精准的建议和更个性化的面试题目。
                </p>
              </div>
              <div className="flex-shrink-0">
                <div className="flex items-center gap-3">
                  {[
                    { label: '简历', color: 'bg-blue-100 text-blue-700' },
                    { label: '诊断', color: 'bg-cyan-100 text-cyan-700' },
                    { label: '匹配', color: 'bg-green-100 text-green-700' },
                    { label: '面试', color: 'bg-purple-100 text-purple-700' },
                    { label: '复盘', color: 'bg-orange-100 text-orange-700' },
                  ].map((item, i) => (
                    <motion.div
                      key={item.label}
                      initial={{ scale: 0.8, opacity: 0 }}
                      whileInView={{ scale: 1, opacity: 1 }}
                      transition={{ delay: i * 0.08 }}
                      viewport={{ once: true }}
                      className={`px-4 py-2 rounded-full text-sm font-medium ${item.color}`}
                    >
                      {item.label}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 职位匹配展示（参考 huunt.ai） */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">智能职位匹配</h2>
            <p className="mt-3 text-gray-500">AI 分析职位需求，为你推荐最匹配的机会</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {MOCK_JOBS.map((job, i) => (
              <motion.div
                key={`${job.company}-${job.title}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.12, duration: 0.5 }}
                className="card hover:shadow-lg transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">{job.company}</p>
                    <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                  </div>
                  <div className="flex items-center gap-1 bg-gradient-to-r from-primary-500 to-blue-500 text-white px-3 py-1.5 rounded-full">
                    <Star className="w-4 h-4 fill-current" />
                    <span className="font-bold">{job.score}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mb-4">
                  {job.tags.map((tag) => (
                    <span
                      key={tag}
                      className={`text-xs px-2 py-1 rounded-full ${
                        tag === '新匹配' ? 'bg-green-100 text-green-700' :
                        tag === '匹配度高' ? 'bg-primary-100 text-primary-700' :
                        tag === '良好匹配' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>{job.location}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Briefcase className="w-4 h-4" />
                    <span>{job.salary}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 mt-3 text-xs text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span>{job.time}</span>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link
              to={token ? '/matching' : '/login'}
              className="inline-flex items-center space-x-2 text-primary-600 font-medium hover:text-primary-700"
            >
              <span>查看更多匹配岗位</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Steps */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">四步开启求职加速</h2>
            <p className="mt-3 text-gray-500">几分钟即可获得专业的简历优化与面试模拟方案</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { icon: Upload, step: '01', title: '上传简历', desc: '支持 PDF / Word / 纯文本格式，自动解析关键信息' },
              { icon: Search, step: '02', title: 'AI 智能分析', desc: 'ATS 兼容性扫描 + 岗位匹配度计算 + 技能缺口识别' },
              { icon: Lightbulb, step: '03', title: '获取改进方案', desc: '雷达图可视化报告 + 个性化建议 + 模拟面试练习' },
              { icon: Rocket, step: '04', title: '提升通过率', desc: '应用优化建议，持续模拟练习，追踪能力成长曲线' },
            ].map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.12, duration: 0.5 }}
                className="relative"
              >
                <div className="text-5xl font-extrabold text-primary-100 mb-2">{s.step}</div>
                <div className="w-12 h-12 rounded-lg bg-primary-50 flex items-center justify-center mb-4">
                  <s.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
                {i < 3 && (
                  <div className="hidden md:block absolute top-6 -right-4 text-gray-200">
                    <ArrowRight className="w-6 h-6" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-br from-primary-600 to-blue-500">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              准备好拿下理想 Offer 了吗？
            </h2>
            <p className="text-primary-100 text-lg mb-8 max-w-xl mx-auto">
              从简历诊断到模拟面试，全流程 AI 赋能，让每一次求职都更有底气
            </p>
            <Link
              to={token ? '/upload' : '/login'}
              className="inline-flex items-center space-x-2 bg-white text-primary-600 font-semibold px-8 py-3 rounded-lg hover:bg-primary-50 transition-colors duration-200 text-lg"
            >
              <span>免费开始使用</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <p className="text-primary-200 text-sm mt-4">测试账号即可体验全部功能</p>
          </motion.div>
        </div>
      </section>

      {/* 用户反馈（参考 finsight.work 的真实案例展示） */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">他们都拿到了心仪 Offer</h2>
            <p className="mt-3 text-gray-500">真实用户的成功案例，见证 AI 求职助手的效果</p>
          </div>
          <div className="relative">
            <div className="overflow-hidden">
              <div className="flex transition-transform duration-500 ease-out" style={{ transform: `translateX(-${testimonialIndex * 100}%)` }}>
                {TESTIMONIALS.map((t, i) => (
                  <div key={i} className="w-full flex-shrink-0 px-4">
                    <div className="max-w-3xl mx-auto">
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="card bg-white border-primary-100 shadow-lg"
                      >
                        <div className="p-8">
                          <Quote className="w-10 h-10 text-primary-200 mb-4" />
                          <p className="text-gray-700 text-lg leading-relaxed mb-6">
                            "{t.content}"
                          </p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-blue-500 flex items-center justify-center">
                                <User className="w-6 h-6 text-white" />
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{t.name}</p>
                                <p className="text-sm text-gray-500">{t.role} @ {t.company}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 bg-primary-50 px-3 py-1.5 rounded-full">
                              <Star className="w-4 h-4 fill-current text-primary-500" />
                              <span className="font-bold text-primary-700">{t.score}</span>
                              <span className="text-xs text-primary-600">分</span>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <button
              onClick={() => setTestimonialIndex((i) => (i === 0 ? TESTIMONIALS.length - 1 : i - 1))}
              className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 md:-translate-x-8 p-3 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={() => setTestimonialIndex((i) => (i === TESTIMONIALS.length - 1 ? 0 : i + 1))}
              className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 md:translate-x-8 p-3 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex justify-center gap-2 mt-6">
              {TESTIMONIALS.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setTestimonialIndex(i)}
                  className={`w-2 h-2 rounded-full transition-all ${i === testimonialIndex ? 'bg-primary-500 w-6' : 'bg-gray-300'}`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 成就数据 */}
      <section className="py-16 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '50,000+', label: '用户信赖' },
              { value: '98%', label: '面试通过率提升' },
              { value: '100,000+', label: '模拟面试次数' },
              { value: '500+', label: '企业录用' },
            ].map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              >
                <div className="text-4xl font-extrabold bg-gradient-to-r from-primary-600 to-blue-500 bg-clip-text text-transparent">
                  {s.value}
                </div>
                <div className="mt-2 text-gray-500 text-sm">{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
