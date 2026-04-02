import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell
} from 'recharts'

const getColor = (pct) =>
  pct >= 70 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#ef4444'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-lg">
      <p className="font-semibold text-slate-800">{d.co}</p>
      <p className="text-sm text-slate-500">{d.description}</p>
      <p className="text-sm font-medium mt-1" style={{ color: getColor(d.attainment_pct) }}>
        Attainment: {d.attainment_pct}%
      </p>
      <p className="text-xs text-slate-400">
        {d.passing_students}/{d.total_students} students passed
      </p>
      <p className={`text-xs font-medium mt-1 ${d.threshold_met ? 'text-green-600' : 'text-red-500'}`}>
        {d.threshold_met ? '✓ Threshold Met' : '✗ Below Threshold'}
      </p>
    </div>
  )
}

export default function COAttainmentBar({ data = [] }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-700">CO Attainment</h3>
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"/>
            ≥ 70% Excellent
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-amber-400 inline-block"/>
            ≥ 60% OK
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500 inline-block"/>
            Below target
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="co" tick={{ fontSize: 12, fill: '#64748b' }} />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11, fill: '#94a3b8' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={60}
            stroke="#6366f1"
            strokeDasharray="5 5"
            label={{ value: '60% target', fill: '#6366f1', fontSize: 11 }}
          />
          <Bar dataKey="attainment_pct" radius={[6, 6, 0, 0]} maxBarSize={60}>
            {data.map((entry, i) => (
              <Cell key={i} fill={getColor(entry.attainment_pct)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}