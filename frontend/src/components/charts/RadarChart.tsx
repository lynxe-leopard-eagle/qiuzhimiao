import {
  RadarChart as ReRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface Props {
  data: { subject: string; A: number; B?: number; fullMark: number }[]
}

export default function RadarChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ReRadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" />
        <PolarRadiusAxis angle={30} domain={[0, 100]} />
        <Radar name="本次" dataKey="A" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.3} />
        {data[0]?.B !== undefined && (
          <Radar name="上次" dataKey="B" stroke="#9ca3af" fill="#d1d5db" fillOpacity={0.2} />
        )}
        <Legend />
      </ReRadarChart>
    </ResponsiveContainer>
  )
}
