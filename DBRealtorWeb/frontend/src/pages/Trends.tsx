import { useState } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useTrends } from '../api/useTrends'
import { useNewPerDay } from '../api/useNewPerDay'
import { useLang } from '../i18n'

const LOCALITIES = ['Praha', 'Brno', 'Ostrava', 'Plzeň', 'Liberec']
const PROPERTY_TYPES = ['flat', 'house', 'land', 'commercial']
const FLAT_TYPES = ['1+kk', '1+1', '2+kk', '2+1', '3+kk', '3+1', '4+kk', '4+1', '5+kk', '5+1', '6 a více', 'atypický']

function formatCZK(val: number): string {
  return new Intl.NumberFormat('cs-CZ', { style: 'currency', currency: 'CZK', maximumFractionDigits: 0 }).format(val)
}

interface TooltipEntry { value?: number }
interface NewPerDayTooltipProps {
  active?: boolean
  payload?: TooltipEntry[]
  label?: string
  newLabel: string
}

function NewPerDayTooltip({ active, payload, label, newLabel }: NewPerDayTooltipProps) {
  if (!active || !payload || payload.length === 0) return null
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm shadow-sm">
      <span className="text-gray-700">
        {String(label)} — <strong className="tabular-nums">{payload[0].value}</strong> {newLabel}
      </span>
    </div>
  )
}

function FilterLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 mr-2">{children}</span>
  )
}

export default function Trends() {
  const { t } = useLang()
  const [locality, setLocality] = useState('Praha')
  const [propertyType, setPropertyType] = useState('flat')
  const [flatType, setFlatType] = useState('')
  const [days, setDays] = useState(90)

  function handlePropertyTypeChange(type: string) {
    setPropertyType(type)
    if (type !== 'flat') setFlatType('')
  }

  const flatTypeParam = propertyType === 'flat' && flatType ? flatType : undefined

  const { data, isLoading, error } = useTrends({ locality, property_type: propertyType, days, flat_type: flatTypeParam })
  const { data: newPerDay, isLoading: newPerDayLoading, error: newPerDayError } =
    useNewPerDay({ locality, property_type: propertyType, days, flat_type: flatTypeParam })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t.trends.title}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{t.trends.subtitleFn(locality)}</p>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        <div className="flex items-center">
          <FilterLabel>{t.trends.filterPeriod}</FilterLabel>
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

        <div className="flex items-center gap-2">
          <FilterLabel>{t.trends.filterCity}</FilterLabel>
          <select
            value={locality}
            onChange={(e) => setLocality(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-gray-300"
          >
            {LOCALITIES.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <FilterLabel>{t.trends.filterType}</FilterLabel>
          <select
            value={propertyType}
            onChange={(e) => handlePropertyTypeChange(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-gray-300"
          >
            {PROPERTY_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
          </select>
        </div>

        {propertyType === 'flat' && (
          <div className="flex items-center gap-2">
            <FilterLabel>{t.trends.filterLayout}</FilterLabel>
            <select
              value={flatType}
              onChange={(e) => setFlatType(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-gray-300"
            >
              <option value="">{t.trends.allLayouts}</option>
              {FLAT_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
            </select>
          </div>
        )}
      </div>

      {/* Chart 1 — avg price */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="mb-1">
          <h2 className="text-base font-semibold text-gray-900">{t.trends.priceChartTitleFn(locality)}</h2>
          <p className="text-xs text-gray-400 mt-0.5">{t.trends.priceChartSubtitle}</p>
        </div>

        {isLoading && <div className="h-64 mt-4 bg-gray-100 rounded-lg animate-pulse" />}
        {error && <p className="text-red-600 text-sm mt-4">{t.trends.priceError}: {error.message}</p>}

        {data && !isLoading && (
          data.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-16">{t.trends.priceChartNoData}</p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={data} margin={{ top: 12, right: 20, bottom: 5, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <YAxis
                  yAxisId="price"
                  tickFormatter={(v: number) => `${(v / 1_000_000).toFixed(1)}M`}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  width={56}
                />
                <YAxis
                  yAxisId="perm2"
                  orientation="right"
                  tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  width={48}
                />
                <Tooltip
                  formatter={(value, name) => [
                    typeof value === 'number' ? formatCZK(value) : value,
                    name === 'avg_price_czk' ? t.trends.priceLabel : t.trends.priceLabelM2,
                  ]}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '13px' }}
                />
                <Legend formatter={(v) => (v === 'avg_price_czk' ? t.trends.priceLabel : t.trends.priceLabelM2)} />
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="avg_price_czk"
                  stroke="#111827"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
                <Line
                  yAxisId="perm2"
                  type="monotone"
                  dataKey="avg_price_per_m2"
                  stroke="#6b7280"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          )
        )}
      </div>

      {/* Chart 2 — new listings per day */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="mb-1">
          <h2 className="text-base font-semibold text-gray-900">{t.trends.newChartTitle}</h2>
          <p className="text-xs text-gray-400 mt-0.5">{t.trends.newChartSubtitleFn(locality)}</p>
        </div>

        {newPerDayLoading && <div className="h-48 mt-4 bg-gray-100 rounded-lg animate-pulse" />}
        {newPerDayError && (
          <p className="text-red-600 text-sm mt-4">{t.trends.newError}: {newPerDayError.message}</p>
        )}

        {newPerDay && !newPerDayLoading && (
          newPerDay.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-12">{t.trends.newChartNoData}</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={newPerDay} margin={{ top: 12, right: 20, bottom: 5, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9ca3af' }} interval={6} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#9ca3af' }} width={36} />
                <Tooltip content={<NewPerDayTooltip newLabel={t.trends.newTooltipLabel} />} />
                <Bar dataKey="count" fill="#bfdbfe" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )
        )}
      </div>
    </div>
  )
}
