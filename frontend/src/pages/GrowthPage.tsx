import { useEffect, useState } from 'react'
import { growthApi } from '../services/api'
import RadarChart from '../components/charts/RadarChart'
import type { GrowthRadar, GrowthTrend } from '../types'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Loader2, TrendingUp } from 'lucide-react'

export default function GrowthPage() {
  const [radar, setRadar] = useState<GrowthRadar | null>(null)
  const [trends, setTrends] = useState<GrowthTrend[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      growthApi.radar().then((r) => setRadar(r.data)),
      growthApi.trend().then((r) => setTrends(r.data.trends)),
    ]).finally(() => setLoading(false))
  }, [])

  const radarData = radar
    ? radar.dimensions.map((d, i) => ({
        subject: d,
        A: radar.latest_scores[i] || 0,
        B: radar.previous_scores[i] || 0,
        fullMark: 100,
      }))
    : []

  const trendData = (() => {
    if (!trends.length) return []
    const map: Record<string, Record<string, number>> = {}
    trends.forEach((t) => {
      t.data.forEach((p) => {
        if (!map[p.date]) map[p.date] = {}
        map[p.date][t.dimension] = p.score
      })
    })
    return Object.entries(map).map(([date, vals]) => ({ date, ...vals }))
  })()

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <TrendingUp className="w-6 h-6 mr-2 text-primary-600" />
        成长追踪
      </h1>
      {loading && <div className="flex items-center text-gray-500"><Loader2 className="w-5 h-5 animate-spin mr-2" />加载中...</div>}
      {!loading && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">能力雷达对比</h2>
            {radarData.length > 0 ? <RadarChart data={radarData} /> : <p className="text-gray-500 text-center py-10">暂无数据</p>}
          </div>
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">成长趋势</h2>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  {trends.map((t, i) => (
                    <Line key={t.dimension} type="monotone" dataKey={t.dimension} stroke={colors[i % colors.length]} strokeWidth={2} dot={false} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-10">暂无趋势数据，完成更多面试即可生成。</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
