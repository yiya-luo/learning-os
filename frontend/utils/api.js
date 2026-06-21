// 部署时修改 API_BASE 为你的后端地址
const API_BASE = 'https://learningos-268322-8-1441734924.sh.run.tcloudbase.com/api'
const BASE_URL = API_BASE

function getToken() {
  return uni.getStorageSync('token')
}

async function request(url, options = {}, _retry = false) {
  try {
    const token = getToken()
    const header = { ...(options.header || {}) }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    const response = await uni.request({
      url: `${BASE_URL}${url}`,
      timeout: 15000,
      ...options,
      header
    })
    if (response.statusCode === 401 && !_retry) {
      const { silentLogin } = require('./auth')
      const loginResult = await silentLogin()
      if (loginResult) {
        return request(url, options, true)
      }
    }
    if (response.statusCode >= 400) {
      const detail = response.data?.detail
      const msg = typeof detail === 'string' ? detail : detail?.[0]?.msg || 'Request failed'
      throw new Error(msg)
    }
    return response.data
  } catch (err) {
    if (err.message && !err.message.includes('Request failed') && !err.message.includes('timeout')) {
      throw err
    }
    throw new Error(err.message || 'Network error')
  }
}

export const api = {
  login: (code) =>
    request('/auth/login', {
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { code }
    }),

  getProjects: () => request('/projects'),

  getProject: (pid) => request(`/projects/${pid}`),

  importProject: (markdown) =>
    request('/projects/import', {
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { markdown }
    }),

  parseProject: (markdown) =>
    request('/projects/parse', {
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { markdown }
    }),

  getTasks: (pid, status) => {
    const query = status ? `?status=${status}` : ''
    return request(`/projects/${pid}/tasks${query}`)
  },

  getTodayTasks: (pid) => request(`/projects/${pid}/tasks/today`),

  getTask: (tid) => request(`/tasks/${tid}`),

  startTask: (tid) =>
    request(`/tasks/${tid}/start`, { method: 'PATCH' }),

  checkin: (tid) =>
    request(`/tasks/${tid}/checkin`, { method: 'POST' }),

  getUserXP: () => request('/users/me/xp'),

  getUserStreak: () => request('/users/me/streak'),

  getRewardProgress: (pid) => request(`/projects/${pid}/reward`),

  updateReward: (pid, data) =>
    request(`/projects/${pid}/reward`, {
      method: 'PUT',
      header: { 'Content-Type': 'application/json' },
      data
    }),

  getUser: () => request('/users/me'),

  updateUser: (data) =>
    request('/users/me', {
      method: 'PATCH',
      header: { 'Content-Type': 'application/json' },
      data
    }),

  /* Phase 2 */
  getHeatmap: (days = 365) =>
    request(`/users/me/heatmap?days=${days}`),

  getDAG: (pid) =>
    request(`/projects/${pid}/dag`),

  getStageDetail: (pid, sid) =>
    request(`/projects/${pid}/stages/${sid}`),

  getAchievements: () =>
    request('/users/me/achievements'),

  updateTheme: (theme) =>
    request('/users/me/theme', {
      method: 'PATCH',
      header: { 'Content-Type': 'application/json' },
      data: { theme }
    }),

  uploadRewardImage: (pid, filePath) =>
    new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `${BASE_URL}/projects/${pid}/reward-image`,
        filePath,
        name: 'image',
        success(res) {
          try {
            resolve(JSON.parse(res.data))
          } catch {
            resolve(res.data)
          }
        },
        fail: reject
      })
    }),

  /* Phase 3 */
  triggerEncouragement: (projectId, triggerEvent, taskId) =>
    request('/encouragement/trigger', {
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { project_id: projectId, trigger_event: triggerEvent, task_id: taskId || null }
    }),

  getAnalytics: (period = 'week') =>
    request(`/users/me/analytics?period=${period}`),

  getMilestones: () =>
    request('/users/me/milestones'),

  getTimeline: (page = 1, pageSize = 20, filter = 'all') =>
    request(`/users/me/timeline?page=${page}&page_size=${pageSize}&filter=${filter}`)
}
