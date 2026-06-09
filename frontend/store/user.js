import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const id = ref('')
  const nickname = ref('Learner')
  const avatar = ref('')
  const xp = ref(0)
  const level = ref(1)
  const levelTitle = ref('初学者')
  const streak = ref(0)
  const longestStreak = ref(0)
  const checkedInToday = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  const xpToNextLevel = computed(() => {
    return level.value * 100
  })

  const xpProgress = computed(() => {
    return Math.min((xp.value % (level.value * 100)) / (level.value * 100) * 100, 100)
  })

  const levelTitles = ['初学者', '探索者', '实践者', '知识学徒', '知识工匠', '知识大师', '终身学习者']

  const computedLevelTitle = computed(() => {
    const idx = Math.min(level.value - 1, levelTitles.length - 1)
    return levelTitles[idx]
  })

  async function fetchUser() {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.getUser()
      id.value = data.id || ''
      nickname.value = data.nickname || 'Learner'
      avatar.value = data.avatar || ''
      xp.value = data.xp || 0
      level.value = data.level || 1
      streak.value = data.streak || 0
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  async function fetchXP() {
    try {
      const data = await api.getUserXP()
      xp.value = data.total_xp || 0
      level.value = data.level || 1
      levelTitle.value = computedLevelTitle.value
    } catch (err) {
      // silently fail
    }
  }

  async function fetchStreak() {
    try {
      const data = await api.getUserStreak()
      streak.value = data.current_streak || 0
      longestStreak.value = data.longest_streak || 0
      checkedInToday.value = data.checked_in_today || false
    } catch (err) {
      // silently fail
    }
  }

  async function updateProfile(data) {
    try {
      const result = await api.updateUser(data)
      if (data.nickname !== undefined) nickname.value = result.nickname
      if (data.avatar !== undefined) avatar.value = result.avatar
      return true
    } catch (err) {
      return false
    }
  }

  function applyCheckinResult(result) {
    xp.value = result.new_total_xp || (xp.value + (result.xp_earned || 0))
    level.value = result.new_level || level.value
    streak.value = result.streak || streak.value
    levelTitle.value = computedLevelTitle.value
  }

  return {
    id, nickname, avatar, xp, level, levelTitle, streak, longestStreak,
    checkedInToday, isLoading, error,
    xpToNextLevel, xpProgress, computedLevelTitle,
    fetchUser, fetchXP, fetchStreak, updateProfile, applyCheckinResult
  }
})
