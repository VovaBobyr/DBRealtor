import { useState } from 'react'
import { useDashboard } from '../api/useDashboard'
import { useTrends } from '../api/useTrends'
import { useLang } from '../i18n'
import { CheckCircle, XCircle, Clock, Home, Plus, TrendingUp, Timer } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

function formatPrice(czk: number | null): string {
  if (czk == null) return '—'
  return new Intl.NumberFormat('cs-CZ', { style: 'currency', currency: 'CZK', maximumFractionDigits: 0 }).format(czk)
}

function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat('cs-CZ', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso))
}

function formatCZK(v: number): string {
  return new Intl.NumberFormat('cs-CZ', { style: 'currency', currency: 'CZK', maximumFractionDigits: 0 }).format(v)
}

interface KpiCardProps {
  label: string
  value: string
  sub?: string
  subColor?: string
  icon: React.ReactNode
}

function KpiCard({ label, value, sub, subColor = 'text-gray-400', icon }: KpiCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{label}</span>
        <div className="text-gray-300">{icon}</div>
      </div>
      <p className="text-4xl font-bold text-gray-900 tabular-nums">{value}</p>
      {sub && <p className={`text-sm mt-2 ${subColor}`}>{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { t } = useLang()
  const [days, setDays] = useState(90)
  const { data, isLoading, error } = useDashboard()
  const { data: trendData, isLoading: trendLoading } = useTrends({
    locality: 'Praha',
    property_type: 'flat',
    days,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-40 bg-gray-200 rounded animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 h-32 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return <p className="text-red-600">{t.dashboard.failedLoad}: {error.message}</p>
  }

  if (!data) return null

  const run = data.last_scrape_run
  const runOk = run?.status === 'success'

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.dashboard.title}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{t.dashboard.subtitle}</p>
        </div>
        {run && (
          <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${
            runOk
              ? 'bg-green-50 text-green-700 border-green-200'
              : 'bg-red-50 text-red-700 border-red-200'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${runOk ? 'bg-green-500' : 'bg-red-500'}`} />
            {runOk ? t.dashboard.liveBadge : t.dashboard.errorBadge}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label={t.dashboard.kpiActiveListings}
          value={data.total_listings.toLocaleString('cs-CZ')}
          icon={<Home size={18} />}
        />
        <KpiCard
          label={t.dashboard.kpiNewToday}
          value={`+${data.new_today.toLocaleString('cs-CZ')}`}
          sub={t.dashboard.kpiAddedToday}
          subColor="text-green-600"
          icon={<Plus size={18} />}
        />
        <KpiCard
          label={t.dashboard.kpiAvgPrice}
          value={formatPrice(data.avg_price_czk)}
          sub={t.dashboard.kpiActiveSub}
          icon={<TrendingUp size={18} />}
        />

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <div className="flex items-start justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{t.dashboard.kpiLastScrape}</span>
            <div className="text-gray-300"><Timer size={18} /></div>
          </div>
          {run ? (
            <>
              <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-semibold ${
                runOk ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                {runOk ? <CheckCircle size={13} /> : <XCircle size={13} />}
                {runOk ? t.dashboard.statusSuccess : t.dashboard.statusFailed}
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {formatDateTime(run.started_at)} · {run.listings_found.toLocaleString()} {t.dashboard.statusFound}
              </p>
            </>
          ) : (
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-semibold bg-gray-100 text-gray-400">
              <Clock size={13} />
              —
            </div>
          )}
        </div>
      </div>

      {/* Price trend chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-gray-900">{t.dashboard.chartTitle}</h2>
            <p className="text-xs text-gray-400 mt-0.5">{t.dashboard.chartSubtitle}</p>
          </div>
          <div className="flex gap-0.5">
            {t.periods.map((p) => (
              <button
                key={p.days}
                onClick={() => setDays(p.days)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  days === p.days
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {trendLoading && <div className="h-64 bg-gray-100 rounded-lg animate-pulse" />}

        {trendData && !trendLoading && (
          trendData.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-16">{t.dashboard.chartNoData}</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trendData} margin={{ top: 5, right: 16, bottom: 5, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <YAxis
                  tickFormatter={(v: number) => `${(v / 1_000_000).toFixed(1)}M`}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  width={52}
                />
                <Tooltip
                  formatter={(v: number) => [formatCZK(v), t.dashboard.chartTooltip]}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '13px' }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_price_czk"
                  stroke="#111827"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )
        )}
      </div>
    </div>
  )
}
