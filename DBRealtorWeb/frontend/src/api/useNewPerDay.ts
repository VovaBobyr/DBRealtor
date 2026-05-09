import { useQuery } from '@tanstack/react-query'
import type { NewPerDayPoint } from './types'

interface NewPerDayParams {
  locality: string
  property_type: string
  days: number
  flat_type?: string
}

async function fetchNewPerDay(params: NewPerDayParams): Promise<NewPerDayPoint[]> {
  const qs = new URLSearchParams({
    locality: params.locality,
    property_type: params.property_type,
    days: String(params.days),
  })
  if (params.flat_type) qs.set('flat_type', params.flat_type)
  const res = await fetch(`/api/trends/new-per-day?${qs}`)
  if (!res.ok) throw new Error(`New-per-day fetch failed: ${res.status}`)
  return res.json() as Promise<NewPerDayPoint[]>
}

export function useNewPerDay(params: NewPerDayParams) {
  return useQuery<NewPerDayPoint[], Error>({
    queryKey: ['trends', 'new-per-day', params],
    queryFn: () => fetchNewPerDay(params),
    staleTime: 5 * 60_000,
  })
}
