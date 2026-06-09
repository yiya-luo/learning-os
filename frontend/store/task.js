import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const todayTasks = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const theoryTasks = computed(() =>
    todayTasks.value.filter(t => t.type === 'theory')
  )
  const practiceTasks = computed(() =>
    todayTasks.value.filter(t => t.type === 'practice')
  )
  const outputTasks = computed(() =>
    todayTasks.value.filter(t => t.type === 'output')
  )

  const completedCount = computed(() =>
    todayTasks.value.filter(t => t.status === 'done').length
  )
  const totalCount = computed(() => todayTasks.value.length)

  const allDone = computed(() =>
    totalCount.value > 0 && completedCount.value === totalCount.value
  )

  const estimatedTime = computed(() =>
    todayTasks.value.reduce((sum, t) => sum + (t.estimate || 0), 0)
  )

  const totalXP = computed(() =>
    todayTasks.value.reduce((sum, t) => sum + (t.xp || 0), 0)
  )

  async function fetchTasks(pid, status) {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.getTasks(pid, status)
      tasks.value = data.tasks || []
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTodayTasks(pid) {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.getTodayTasks(pid)
      todayTasks.value = data.tasks || []
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  async function startTask(tid) {
    try {
      const result = await api.startTask(tid)
      const task = todayTasks.value.find(t => t.id === tid)
      if (task) {
        task.status = 'doing'
      }
      return result
    } catch (err) {
      return null
    }
  }

  async function checkin(tid) {
    try {
      const result = await api.checkin(tid)
      return result
    } catch (err) {
      throw err
    }
  }

  function toggleTaskLocally(tid) {
    const task = todayTasks.value.find(t => t.id === tid)
    if (task) {
      task.status = task.status === 'done' ? 'doing' : 'done'
    }
  }

  return {
    tasks, todayTasks, isLoading, error,
    theoryTasks, practiceTasks, outputTasks,
    completedCount, totalCount, allDone, estimatedTime, totalXP,
    fetchTasks, fetchTodayTasks, startTask, checkin, toggleTaskLocally
  }
})
