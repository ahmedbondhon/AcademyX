const riskConfig = {
  high:   { color: 'text-red-600',    bg: 'bg-red-50',    badge: 'bg-red-100 text-red-700',    icon: '🔴' },
  medium: { color: 'text-amber-600',  bg: 'bg-amber-50',  badge: 'bg-amber-100 text-amber-700', icon: '🟡' },
  low:    { color: 'text-green-600',  bg: 'bg-green-50',  badge: 'bg-green-100 text-green-700', icon: '🟢' },
}

export default function RiskTable({ data = [] }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div className="p-5 border-b border-slate-100">
        <h3 className="font-semibold text-slate-700">At-Risk Students</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Sorted by risk score — highest first
        </p>
      </div>
      <div className="overflow-auto max-h-80">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-slate-400 text-xs uppercase tracking-wide">
              <th className="px-4 py-3 text-left font-medium">Student</th>
              <th className="px-4 py-3 text-left font-medium">Risk</th>
              <th className="px-4 py-3 text-left font-medium">Score</th>
              <th className="px-4 py-3 text-left font-medium">At-risk COs</th>
            </tr>
          </thead>
          <tbody>
            {data.map((s, i) => {
              const cfg = riskConfig[s.risk_level] || riskConfig.low
              return (
                <tr key={i}
                    className={`border-t border-slate-50 hover:${cfg.bg} transition-colors`}>
                  <td className="px-4 py-3 font-medium text-slate-700">
                    {cfg.icon} {s.student_name}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs
                                      font-medium ${cfg.badge}`}>
                      {s.risk_level}
                    </span>
                  </td>
                  <td className={`px-4 py-3 font-semibold ${cfg.color}`}>
                    {s.risk_pct}%
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {s.at_risk_cos?.length > 0
                      ? s.at_risk_cos.join(', ')
                      : <span className="text-green-500">None</span>
                    }
                  </td>
                </tr>
              )
            })}
            {data.length === 0 && (
              <tr>
                <td colSpan={4}
                    className="px-4 py-8 text-center text-slate-400 text-sm">
                  No risk data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}