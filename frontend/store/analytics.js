import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useAnalyticsStore = defineStore('analytics', () => {
  const period = ref('week')
  const analyticsData = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const periodOptions = [
    { value: 'week', label: '本周' },
    { value: 'month', label: '本月' },
    { value: 'all', label: '全部' }
  ]

  const isEmpty = computed(() => {
    const d = analyticsData.value
    if (!d) return null
    return (!d.current || d.current.tasks_completed === 0) &&
           (!d.summary || d.summary.total_tasks_completed === 0)
  })

  async function fetchAnalytics(p) {
    if (p) period.value = p
    loading.value = true
    error.value = null

    try {
      const data = await api.getAnalytics(period.value)
      analyticsData.value = data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  function getChangeClass(value) {
    if (value === null || value === undefined) return ''
    return value >= 0 ? 'change-up' : 'change-down'
  }

  function getChangeArrow(value) {
    if (value === null || value === undefined) return ''
    return value >= 0 ? '↑' : '↓'
  }

  function formatPct(value) {
    if (value === null || value === undefined) return '--'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${Math.round(value * 10) / 10}%`
  }

  return {
    period, analyticsData, loading, error, periodOptions, isEmpty,
    fetchAnalytics, getChangeClass, getChangeArrow, formatPct
  }
})
