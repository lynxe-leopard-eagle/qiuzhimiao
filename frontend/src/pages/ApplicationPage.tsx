import { useState, useEffect } from 'react'
import { applicationApi } from '../services/api'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Building2, Briefcase, MapPin, Calendar, Trash2, Edit2, Users, CheckCircle2, XCircle, Clock, ArrowRightCircle } from 'lucide-react'

interface Application {
  id: string
  company: string
  position: string
  stage: string
  city: string | null
  salary_range: string | null
  notes: string | null
  contact_info: string | null
  feedback: string | null
  created_at: string
  updated_at: string
}

const STAGES = [
  { key: 'applied', label: '已投递', color: 'bg-blue-500', bg: 'bg-blue-50', border: 'border-blue-200' },
  { key: 'screening', label: '简历筛选', color: 'bg-cyan-500', bg: 'bg-cyan-50', border: 'border-cyan-200' },
  { key: 'interview', label: '面试中', color: 'bg-yellow-500', bg: 'bg-yellow-50', border: 'border-yellow-200' },
  { key: 'offer', label: '已Offer', color: 'bg-green-500', bg: 'bg-green-50', border: 'border-green-200' },
  { key: 'rejected', label: '已拒绝', color: 'bg-gray-500', bg: 'bg-gray-50', border: 'border-gray-200' },
]

export default function ApplicationPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [stats, setStats] = useState<Record<string, number>>({})
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Application | null>(null)
  const [form, setForm] = useState({ company: '', position: '', stage: 'applied', city: '', salary_range: '', notes: '', contact_info: '' })
  const [draggedId, setDraggedId] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [apps, statsRes] = await Promise.all([
        applicationApi.list(),
        applicationApi.stats(),
      ])
      setApplications(apps.data)
      const statsMap: Record<string, number> = {}
      statsRes.data.forEach((s: { stage: string; count: number }) => {
        statsMap[s.stage] = s.count
      })
      setStats(statsMap)
    } catch (err) {
      console.error('Failed to load applications:', err)
    }
  }

  const handleSubmit = async () => {
    try {
      if (editing) {
        await applicationApi.update(editing.id, {
          stage: form.stage,
          salary_range: form.salary_range,
          notes: form.notes,
          contact_info: form.contact_info,
        })
      } else {
        await applicationApi.create(form)
      }
      setShowModal(false)
      setEditing(null)
      setForm({ company: '', position: '', stage: 'applied', city: '', salary_range: '', notes: '', contact_info: '' })
      loadData()
    } catch (err) {
      alert('保存失败')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除这条投递记录吗？')) return
    try {
      await applicationApi.delete(id)
      loadData()
    } catch (err) {
      alert('删除失败')
    }
  }

  const handleStageChange = async (id: string, newStage: string) => {
    try {
      await applicationApi.update(id, { stage: newStage })
      loadData()
    } catch (err) {
      alert('更新失败')
    }
  }

  const handleDragStart = (id: string) => {
    setDraggedId(id)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = (e: React.DragEvent, targetStage: string) => {
    e.preventDefault()
    if (draggedId) {
      handleStageChange(draggedId, targetStage)
      setDraggedId(null)
    }
  }

  const getApplicationsByStage = (stage: string) => {
    return applications.filter(app => app.stage === stage)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Users className="w-7 h-7 mr-2 text-primary-600" />
                投递看板
              </h1>
              <p className="text-sm text-gray-500 mt-1">追踪你的求职进度，记录每一次机会</p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary flex items-center px-5"
            >
              <Plus className="w-4 h-4 mr-2" />
              添加投递
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          {STAGES.map((stage) => (
            <div key={stage.key} className={`p-4 rounded-xl ${stage.bg} border ${stage.border}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">{stage.label}</span>
                <span className={`w-8 h-8 rounded-full ${stage.color} text-white text-sm font-bold flex items-center justify-center`}>
                  {stats[stage.key] || 0}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Kanban */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {STAGES.map((stage) => (
            <div
              key={stage.key}
              className={`bg-white rounded-xl border ${stage.border} p-4 flex flex-col`}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, stage.key)}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">{stage.label}</h3>
                <span className={`px-2 py-0.5 rounded-full text-xs text-white ${stage.color}`}>
                  {stats[stage.key] || 0}
                </span>
              </div>
              <div className="flex-1 space-y-3 overflow-y-auto">
                <AnimatePresence>
                  {getApplicationsByStage(stage.key).map((app) => (
                    <motion.div
                      key={app.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      draggable
                      onDragStart={() => handleDragStart(app.id)}
                      className={`bg-white border ${stage.border} rounded-lg p-3 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow group`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Building2 className="w-4 h-4 text-gray-400" />
                            <span className="font-medium text-gray-900 text-sm">{app.company}</span>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <Briefcase className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-700">{app.position}</span>
                          </div>
                          {app.city && (
                            <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                              <MapPin className="w-3 h-3" />
                              {app.city}
                            </div>
                          )}
                          {app.salary_range && (
                            <div className="text-xs text-green-600 font-medium mb-1">{app.salary_range}</div>
                          )}
                          <div className="flex items-center gap-2 text-xs text-gray-400">
                            <Calendar className="w-3 h-3" />
                            {formatDate(app.created_at)}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => { setEditing(app); setForm({ company: app.company, position: app.position, stage: app.stage, city: app.city || '', salary_range: app.salary_range || '', notes: app.notes || '', contact_info: app.contact_info || '' }); setShowModal(true) }} className="p-1.5 rounded hover:bg-gray-100">
                            <Edit2 className="w-3.5 h-3.5 text-gray-500" />
                          </button>
                          <button onClick={() => handleDelete(app.id)} className="p-1.5 rounded hover:bg-red-50">
                            <Trash2 className="w-3.5 h-3.5 text-red-500" />
                          </button>
                        </div>
                      </div>
                      
                      {/* Stage Navigation */}
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                        <span className={`text-xs px-2 py-1 rounded-full ${stage.bg} text-gray-700`}>当前状态</span>
                        <div className="flex items-center gap-1">
                          {STAGES.filter(s => STAGES.indexOf(s) > STAGES.indexOf(stage)).map((nextStage) => (
                            <button
                              key={nextStage.key}
                              onClick={() => handleStageChange(app.id, nextStage.key)}
                              className={`p-1 rounded hover:bg-gray-100 transition-colors`}
                              title={nextStage.label}
                            >
                              <ArrowRightCircle className={`w-3.5 h-3.5 ${nextStage.color.replace('bg-', 'text-')}`} />
                            </button>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {getApplicationsByStage(stage.key).length === 0 && (
                  <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                    <div className={`w-12 h-12 rounded-full ${stage.bg} flex items-center justify-center mb-2`}>
                      {stage.key === 'offer' ? <CheckCircle2 className="w-6 h-6" /> : stage.key === 'rejected' ? <XCircle className="w-6 h-6" /> : <Clock className="w-6 h-6" />}
                    </div>
                    <span className="text-sm">暂无{stage.label}的投递</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => { setShowModal(false); setEditing(null) }}
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            className="bg-white rounded-xl shadow-xl w-full max-w-md p-6"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4">{editing ? '编辑投递记录' : '添加投递记录'}</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">公司名称</label>
                <input
                  value={form.company}
                  onChange={(e) => setForm({ ...form, company: e.target.value })}
                  className="input w-full"
                  placeholder="例如：字节跳动"
                  disabled={!!editing}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">岗位名称</label>
                <input
                  value={form.position}
                  onChange={(e) => setForm({ ...form, position: e.target.value })}
                  className="input w-full"
                  placeholder="例如：后端开发工程师"
                  disabled={!!editing}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">投递阶段</label>
                <select
                  value={form.stage}
                  onChange={(e) => setForm({ ...form, stage: e.target.value })}
                  className="input w-full"
                >
                  {STAGES.map((stage) => (
                    <option key={stage.key} value={stage.key}>{stage.label}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">城市</label>
                  <input
                    value={form.city}
                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                    className="input w-full"
                    placeholder="例如：北京"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">薪资范围</label>
                  <input
                    value={form.salary_range}
                    onChange={(e) => setForm({ ...form, salary_range: e.target.value })}
                    className="input w-full"
                    placeholder="例如：25k-35k"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">联系人信息</label>
                <input
                  value={form.contact_info}
                  onChange={(e) => setForm({ ...form, contact_info: e.target.value })}
                  className="input w-full"
                  placeholder="例如：HR邮箱或微信"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">备注</label>
                <textarea
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  className="input w-full"
                  rows={3}
                  placeholder="面试感受、需要注意的事项等"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => { setShowModal(false); setEditing(null) }}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSubmit}
                className="btn-primary"
              >
                {editing ? '保存修改' : '添加投递'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
