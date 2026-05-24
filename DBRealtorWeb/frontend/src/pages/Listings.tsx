import { useState, useEffect, useCallback } from 'react'
import { useListings } from '../api/useListings'
import type { ListingsParams } from '../api/useListings'
import { useLang } from '../i18n'
import { ExternalLink, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'

type SortField = 'price_czk' | 'area_m2' | 'first_seen_at' | 'price_per_m2'
type SortOrder = 'asc' | 'desc'

function formatPrice(v: number | null): string {
  if (v == null) return '—'
  return new Intl.NumberFormat('cs-CZ', { style: 'currency', currency: 'CZK', maximumFractionDigits: 0 }).format(v)
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('cs-CZ', { dateStyle: 'short' }).format(new Date(iso))
}

function SortIcon({ active, order }: { active: boolean; order: SortOrder }) {
  if (!active) return <ChevronsUpDown size={12} className="text-gray-300" />
  return order === 'asc'
    ? <ChevronUp size={12} className="text-gray-700" />
    : <ChevronDown size={12} className="text-gray-700" />
}

export default function Listings() {
  const { t } = useLang()
  const [page, setPage] = useState(1)
  const [locality, setLocality] = useState('')
  const [debouncedLocality, setDebouncedLocality] = useState('')
  const [sortBy, setSortBy] = useState<SortField>('first_seen_at')
  const [order, setOrder] = useState<SortOrder>('desc')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedLocality(locality)
      setPage(1)
    }, 300)
    return () => clearTimeout(timer)
  }, [locality])

  const columns: { key: SortField; label: string }[] = [
    { key: 'first_seen_at', label: t.listings.colAdded },
    { key: 'price_czk', label: t.listings.colPrice },
    { key: 'area_m2', label: t.listings.colArea },
    { key: 'price_per_m2', label: t.listings.colPriceM2 },
  ]

  const params: ListingsParams = {
    page,
    limit: 20,
    locality: debouncedLocality || undefined,
    sort_by: sortBy,
    order,
  }

  const { data, isLoading, isFetching } = useListings(params)

  const handleSort = useCallback((field: SortField) => {
    if (field === sortBy) {
      setOrder((o) => (o === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(field)
      setOrder('desc')
    }
    setPage(1)
  }, [sortBy])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.listings.title}</h1>
          {data && (
            <p className="text-sm text-gray-500 mt-0.5">{t.listings.totalFn(data.total)}</p>
          )}
        </div>
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          placeholder={t.listings.searchPlaceholder}
          value={locality}
          onChange={(e) => setLocality(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-56 bg-white focus:outline-none focus:ring-2 focus:ring-gray-300 placeholder:text-gray-400"
        />
      </div>

      <div className={`bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden transition-opacity ${isFetching ? 'opacity-60' : 'opacity-100'}`}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
                {t.listings.colLocality}
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
                {t.listings.colType}
              </th>
              {columns.map(({ key, label }) => (
                <th
                  key={key}
                  className="text-right px-5 py-3 text-xs font-semibold uppercase tracking-wider text-gray-400 cursor-pointer select-none hover:text-gray-700"
                  onClick={() => handleSort(key)}
                >
                  <span className="inline-flex items-center gap-1">
                    {label}
                    <SortIcon active={sortBy === key} order={order} />
                  </span>
                </th>
              ))}
              <th className="px-5 py-3 w-8" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading
              ? [...Array(10)].map((_, i) => (
                  <tr key={i}>
                    {[...Array(7)].map((__, j) => (
                      <td key={j} className="px-5 py-3.5">
                        <div className="h-3.5 bg-gray-100 rounded animate-pulse" style={{ width: `${60 + (j * 13) % 40}%` }} />
                      </td>
                    ))}
                  </tr>
                ))
              : data?.items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5 text-gray-700 max-w-48 truncate font-medium">{item.locality ?? '—'}</td>
                    <td className="px-5 py-3.5">
                      <span className="capitalize text-gray-500 text-xs">{item.property_type}</span>
                      <span className="text-gray-300 mx-1">·</span>
                      <span className="capitalize text-gray-400 text-xs">{item.listing_type}</span>
                    </td>
                    <td className="px-5 py-3.5 text-right font-semibold text-gray-900 tabular-nums">{formatPrice(item.price_czk)}</td>
                    <td className="px-5 py-3.5 text-right text-gray-500 tabular-nums">
                      {item.area_m2 != null ? `${item.area_m2} m²` : '—'}
                    </td>
                    <td className="px-5 py-3.5 text-right text-gray-500 tabular-nums">{formatPrice(item.price_per_m2)}</td>
                    <td className="px-5 py-3.5 text-right text-gray-400 tabular-nums">{formatDate(item.first_seen_at)}</td>
                    <td className="px-5 py-3.5 text-center">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-300 hover:text-blue-500 transition-colors"
                        title="Otevřít na sreality.cz"
                      >
                        <ExternalLink size={14} />
                      </a>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>

        {data && data.pages > 1 && (
          <div className="border-t border-gray-100 px-5 py-3 flex items-center justify-between">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-50 transition-colors"
            >
              {t.listings.prevPage}
            </button>
            <span className="text-xs text-gray-400 tabular-nums">
              {t.listings.pageFn(data.page, data.pages)}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
              disabled={page === data.pages}
              className="px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-50 transition-colors"
            >
              {t.listings.nextPage}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
