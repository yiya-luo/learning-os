import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useRewardStore = defineStore('reward', () => {
  const rewardTitle = ref('')
  const rewardPrice = ref(0)
  const accumulatedValue = ref(0)
  const progressPercent = ref(0)
  const remaining = ref(0)
  const estimatedDaysRemaining = ref(null)
  const aiAnalysis = ref('')
  const aiSuggestions = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const remainingAmount = computed(() => {
    return Math.max(rewardPrice.value - accumulatedValue.value, 0)
  })

  const progressDisplay = computed(() => {
    return Math.round(progressPercent.value)
  })

  const etaDate = computed(() => {
    if (!estimatedDaysRemaining.value) return ''
    const d = new Date()
    d.setDate(d.getDate() + estimatedDaysRemaining.value)
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
  })

  async function fetchRewardProgress(pid) {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.getRewardProgress(pid)
      rewardTitle.value = data.reward_name || ''
      rewardPrice.value = data.reward_price || 0
      accumulatedValue.value = data.dream_value_earned || 0
      progressPercent.value = (data.progress_percent || 0) * 100
      estimatedDaysRemaining.value = data.estimated_days_remaining
      remaining.value = remainingAmount.value
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  return {
    rewardTitle, rewardPrice, accumulatedValue, progressPercent, remaining,
    estimatedDaysRemaining, aiAnalysis, aiSuggestions, isLoading, error,
    remainingAmount, progressDisplay, etaDate,
    fetchRewardProgress
  }
})
