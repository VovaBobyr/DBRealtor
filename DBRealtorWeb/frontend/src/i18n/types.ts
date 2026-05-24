export type Lang = 'cs' | 'en' | 'ua'

export interface PeriodOption {
  label: string
  days: number
}

export interface Translations {
  periods: PeriodOption[]

  nav: {
    dashboard: string
    trends: string
    listings: string
    alerts: string
  }

  dashboard: {
    title: string
    subtitle: string
    liveBadge: string
    errorBadge: string
    kpiActiveListings: string
    kpiNewToday: string
    kpiAvgPrice: string
    kpiLastScrape: string
    kpiAddedToday: string
    kpiActiveSub: string
    statusSuccess: string
    statusFailed: string
    statusFound: string
    chartTitle: string
    chartSubtitle: string
    chartNoData: string
    chartTooltip: string
    failedLoad: string
  }

  trends: {
    title: string
    subtitleFn: (locality: string) => string
    filterPeriod: string
    filterCity: string
    filterType: string
    filterLayout: string
    allLayouts: string
    priceChartTitleFn: (locality: string) => string
    priceChartSubtitle: string
    priceChartNoData: string
    priceLabel: string
    priceLabelM2: string
    priceError: string
    newChartTitle: string
    newChartSubtitleFn: (locality: string) => string
    newChartNoData: string
    newTooltipLabel: string
    newError: string
  }

  alerts: {
    title: string
    subtitle: string
    newBadge: string
    sectionNew: string
    sectionDrops: string
    totalFn: (n: number) => string
    emptyNew: string
    emptyDrops: string
    detail: string
    failedLoad: string
  }

  listings: {
    title: string
    totalFn: (n: number) => string
    searchPlaceholder: string
    colLocality: string
    colType: string
    colAdded: string
    colPrice: string
    colArea: string
    colPriceM2: string
    prevPage: string
    nextPage: string
    pageFn: (page: number, total: number) => string
  }
}
