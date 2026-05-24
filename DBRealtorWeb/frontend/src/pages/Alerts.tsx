import { useAlerts } from '../api/useAlerts'
import type { NewListingItem, PriceDropItem } from '../api/types'
import { useLang } from '../i18n'
import { ExternalLink } from 'lucide-react'

function formatPrice(v: number): string {
  return new Intl.NumberFormat('cs-CZ', { style: 'currency', currency: 'CZK', maximumFractionDigits: 0 }).format(v)
}

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const h = Math.floor(diff / 3_600_000)
  const m = Math.floor((diff % 3_600_000) / 60_000)
  if (h > 23) return new Intl.DateTimeFormat('cs-CZ', { dateStyle: 'short' }).format(new Date(iso))
  if (h > 0) return `${h} h`
  return `${m} min`
}

interface NewListingCardProps extends NewListingItem {
  newBadge: string
  detail: string
}

function NewListingCard({ title, locality, price_czk, area_m2, property_type, first_seen_at, url, newBadge, detail }: NewListingCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold text-gray-900 leading-snug line-clamp-2">{title}</p>
        <span className="flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full bg-green-50 text-green-700 border border-green-200">
          {newBadge}
        </span>
      </div>
      <div className="flex items-center gap-1.5 flex-wrap">
        {locality && <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500">{locality}</span>}
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500 capitalize">{property_type}</span>
        {area_m2 != null && <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500">{area_m2} m²</span>}
      </div>
      <div className="flex items-center justify-between mt-auto">
        <span className="text-base font-bold text-gray-900 tabular-nums">
          {price_czk != null ? formatPrice(price_czk) : '—'}
        </span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">{formatRelativeTime(first_seen_at)}</span>
          <a href={url} target="_blank" rel="noopener noreferrer"
            className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1">
            {detail} <ExternalLink size={11} />
          </a>
        </div>
      </div>
    </div>
  )
}

interface PriceDropCardProps extends PriceDropItem {
  detail: string
}

function PriceDropCard({ title, locality, old_price_czk, new_price_czk, drop_pct, url, detail }: PriceDropCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold text-gray-900 leading-snug line-clamp-2">{title}</p>
        <span className="flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200">
          −{drop_pct.toFixed(1)} %
        </span>
      </div>
      {locality && (
        <div className="flex items-center gap-1.5">
          <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500">{locality}</span>
        </div>
      )}
      <div className="flex items-center justify-between mt-auto">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400 line-through tabular-nums">{formatPrice(old_price_czk)}</span>
          <span className="text-base font-bold text-gray-900 tabular-nums">{formatPrice(new_price_czk)}</span>
        </div>
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1">
          {detail} <ExternalLink size={11} />
        </a>
      </div>
    </div>
  )
}

export default function Alerts() {
  const { t } = useLang()
  const { data, isLoading, error } = useAlerts({ hours: 24, min_drop_pct: 5 })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-40 bg-gray-200 rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[0, 1].map((col) => (
            <div key={col} className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-200 h-28 animate-pulse" />
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return <p className="text-red-600">{t.alerts.failedLoad}: {error.message}</p>
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t.alerts.title}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{t.alerts.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section>
          <div className="flex items-center gap-2 mb-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">{t.alerts.sectionNew}</h2>
            <span className="text-xs text-gray-400">{t.alerts.totalFn(data.new_listings.length)}</span>
          </div>
          {data.new_listings.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
              {t.alerts.emptyNew}
            </div>
          ) : (
            <div className="space-y-3">
              {data.new_listings.map((item) => (
                <NewListingCard key={item.id} {...item} newBadge={t.alerts.newBadge} detail={t.alerts.detail} />
              ))}
            </div>
          )}
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">{t.alerts.sectionDrops}</h2>
            <span className="text-xs text-gray-400">{t.alerts.totalFn(data.price_drops.length)}</span>
          </div>
          {data.price_drops.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
              {t.alerts.emptyDrops}
            </div>
          ) : (
            <div className="space-y-3">
              {data.price_drops.map((item) => (
                <PriceDropCard key={item.sreality_id} {...item} detail={t.alerts.detail} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
