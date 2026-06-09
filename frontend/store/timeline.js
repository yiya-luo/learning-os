import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useTimelineStore = defineStore('timeline', () => {
  const events = ref([])
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const filter = ref('all')
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref(null)
  const hasMore = ref(true)

  const pagesForFilter = ref({
    all: 1,
    milestone: 1,
    achievement: 1,
    checkin: 1,
    stage: 1
  })

  const filterLabels = {
    all: '全部',
    milestone: '里程碑',
    achievement: '成就',
    checkin: '打卡',
    stage: '阶段'
  }

  const filterOptions = computed(() =>
    Object.entries(filterLabels).map(([value, label]) => ({ value, label }))
  )

  async function fetchEvents(p = 1, f) {
    const currentFilter = f || filter.value
    if (p === 1) {
      isLoading.value = true
      error.value = null
    }

    try {
      const data = await api.getTimeline(p, pageSize.value, currentFilter)
      if (p === 1) {
        events.value = data.events || []
      } else {
        events.value = [...events.value, ...(data.events || [])]
      }
      page.value = data.pagination?.page || p
      total.value = data.pagination?.total || 0
      hasMore.value = data.pagination?.has_more || false
      pagesForFilter.value[currentFilter] = p
    } catch (err) {
      error.value = err.message
      if (p === 1) events.value = []
    } finally {
      isLoading.value = false
      isLoadingMore.value = false
    }
  }

  async function loadMore() {
    if (isLoadingMore.value || !hasMore.value) return
    isLoadingMore.value = true
    const nextPage = pagesForFilter.value[filter.value] + 1
    await fetchEvents(nextPage)
  }

  async function setFilter(f) {
    if (filter.value === f) return
    filter.value = f
    page.value = 1
    hasMore.value = true
    await fetchEvents(1, f)
  }

  function formatDate(dateStr) {
    if (!dateStr) return ''
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const target = new Date(dateStr)
    const todayStr = today.toISOString().split('T')[0]
    const yesterdayStr = yesterday.toISOString().split('T')[0]
    const targetStr = target.toISOString().split('T')[0]

    if (targetStr === todayStr) return '今天'
    if (targetStr === yesterdayStr) return '昨天'

    const month = target.getMonth() + 1
    const day = target.getDate()
    return `${month}月${day}日`
  }

  return {
    events, page, pageSize, total, filter, isLoading, isLoadingMore,
    error, hasMore, pagesForFilter, filterOptions, filterLabels,
    fetchEvents, loadMore, setFilter, formatDate
  }
})
