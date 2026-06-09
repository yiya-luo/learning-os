import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const stages = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const currentProjectId = computed(() => currentProject.value?.id || null)

  const overallProgress = computed(() => {
    if (!currentProject.value) return 0
    return Math.round((currentProject.value.progress || 0) * 100)
  })

  const hasProject = computed(() => projects.value.length > 0)

  async function fetchProjects() {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.getProjects()
      projects.value = data.projects || []
      if (projects.value.length > 0 && !currentProject.value) {
        setCurrent(projects.value[0].id)
      }
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  async function fetchProjectDetail(pid) {
    try {
      const data = await api.getProject(pid)
      currentProject.value = data
      stages.value = data.stages || []
      return data
    } catch (err) {
      error.value = err.message
      return null
    }
  }

  async function importDSL(markdown) {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.importProject(markdown)
      await fetchProjects()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setCurrent(pid) {
    const project = projects.value.find(p => p.id === pid)
    if (project) {
      currentProject.value = project
    }
  }

  return {
    projects, currentProject, stages, isLoading, error,
    currentProjectId, overallProgress, hasProject,
    fetchProjects, fetchProjectDetail, importDSL, setCurrent
  }
})
