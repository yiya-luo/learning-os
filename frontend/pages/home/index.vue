<template>
  <view class="home-page">
    <!-- Header: greeting + avatar -->
    <view class="home-header">
      <view class="home-header__left">
        <text class="home-header__greeting">Hi, {{ userStore.nickname }} 👋</text>
        <text class="home-header__quote">"{{ encouragement }}"</text>
      </view>
      <view class="home-header__avatar">
        <text class="home-header__avatar-emoji">{{ avatarEmoji }}</text>
      </view>
    </view>

    <!-- Loading skeleton -->
    <view v-if="isLoading" class="home-skeleton">
      <view class="skeleton-card skeleton-card--project" />
      <view class="skeleton-card skeleton-card--actions" />
      <view class="skeleton-card skeleton-card--tasks" />
    </view>

    <!-- Error state -->
    <view v-else-if="hasError" class="home-error">
      <text class="home-error__text">{{ error }}</text>
      <view class="home-error__retry" @tap="refreshAll">
        <text class="home-error__retry-text">重试</text>
      </view>
    </view>

    <!-- Empty state -->
    <view v-else-if="!projectStore.hasProject && !isLoading">
      <EmptyState
        icon="🚀"
        title="开始你的第一段旅程吧"
        description="导入一份AI生成的学习计划，开启你的学习之旅"
        action-text="导入学习计划"
        @action="goImport"
      />
    </view>

    <!-- Normal content -->
    <template v-else>
      <!-- Project Card -->
      <view class="home-project-card" v-if="projectStore.currentProject">
        <view class="project-card__header">
          <text class="project-card__icon">{{ categoryIcon(projectStore.currentProject) }}</text>
          <text class="project-card__title">{{ projectStore.currentProject.title }}</text>
          <view class="project-card__badge">
            <text class="project-card__badge-text">完成率{{ projectStore.overallProgress }}%</text>
          </view>
        </view>
        <view class="project-card__progress">
          <view class="project-card__progress-bar" :style="{ width: projectStore.overallProgress + '%' }" />
        </view>
        <view class="project-card__stats">
          <view class="project-card__stat">
            <text class="project-card__stat-value">{{ taskStore.completedCount }}/{{ taskStore.totalCount }}</text>
            <text class="project-card__stat-label">今日进度</text>
          </view>
          <view class="project-card__stat">
            <text class="project-card__stat-value">{{ userStore.streak }}天 🔥</text>
            <text class="project-card__stat-label">连续打卡</text>
          </view>
        </view>
      </view>

      <!-- 4 Action Buttons -->
      <view class="home-actions">
        <view class="action-btn" @tap="goGoal">
          <view class="action-btn__icon action-btn__icon--blue">
            <text>📝</text>
          </view>
          <text class="action-btn__label">创建目标</text>
        </view>
        <view class="action-btn" @tap="goGoal">
          <view class="action-btn__icon action-btn__icon--purple">
            <text>✨</text>
          </view>
          <text class="action-btn__label">AI Prompt</text>
        </view>
        <view class="action-btn" @tap="goImport">
          <view class="action-btn__icon action-btn__icon--green">
            <text>📥</text>
          </view>
          <text class="action-btn__label">导入计划</text>
        </view>
        <view class="action-btn" @tap="goAnalytics">
          <view class="action-btn__icon action-btn__icon--orange">
            <text>📊</text>
          </view>
          <text class="action-btn__label">数据统计</text>
        </view>
      </view>

      <!-- Today Tasks -->
      <view v-if="taskStore.todayTasks.length > 0" class="home-tasks-card">
        <text class="home-tasks__title">🎯 今日任务列表</text>
        <view class="home-tasks__list">
          <view
            v-for="task in taskStore.todayTasks.slice(0, 5)"
            :key="task.id"
            class="task-item"
            :class="{ 'task-item--done': task.done }"
            @tap="handleTaskToggle(task.id)"
          >
            <view class="task-item__checkbox" :class="{ 'task-item__checkbox--checked': task.done }">
              <text v-if="task.done" class="task-item__check">✓</text>
            </view>
            <text class="task-item__text" :class="{ 'task-item__text--done': task.done }">{{ task.title }}</text>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { useProjectStore } from '@/store/project'
import { useTaskStore } from '@/store/task'
import { useRewardStore } from '@/store/reward'
import EmptyState from '@/components/EmptyState.vue'

const userStore = useUserStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const rewardStore = useRewardStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const encouragement = ref('')
const avatarEmoji = ref('🦊')

const encouragements = [
  '每一次微小的坚持，都在重塑未来的你。',
  '学习的复利效应，会在某一天给你惊喜。',
  '成长不是一蹴而就，而是日积月累的奇迹。',
  '与其焦虑远方，不如做好今天的任务。',
  '每天进步1%，一年后你将成长37倍。',
  '把大目标拆成小任务，然后一个个搞定。'
]

function categoryIcon(project) {
  const title = (project.title || '').toLowerCase()
  if (title.includes('python') || title.includes('编程') || title.includes('code')) return '💻'
  if (title.includes('英语') || title.includes('english')) return '🌍'
  if (title.includes('数学') || title.includes('算法')) return '🧮'
  if (title.includes('cfa') || title.includes('金融') || title.includes('量化')) return '📚'
  return '📚'
}
/* PLACEHOLDER_SCRIPT_REST */
async function refreshAll() {
  isLoading.value = true
  hasError.value = false
  error.value = ''
  try {
    await Promise.all([
      userStore.fetchUser(),
      userStore.fetchXP(),
      userStore.fetchStreak(),
      projectStore.fetchProjects()
    ])
    if (userStore.avatar) avatarEmoji.value = userStore.avatar
    const pid = projectStore.currentProjectId
    if (pid) {
      await Promise.all([
        taskStore.fetchTodayTasks(pid),
        rewardStore.fetchRewardProgress(pid)
      ])
    }
  } catch (e) {
    hasError.value = true
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

function handleTaskToggle(tid) {
  taskStore.toggleTaskLocally(tid)
}

function goGoal() { uni.navigateTo({ url: '/pages/goal/index' }) }
function goImport() { uni.navigateTo({ url: '/pages/import/index' }) }
function goAnalytics() { uni.navigateTo({ url: '/pages/analytics/index' }) }

onMounted(() => {
  encouragement.value = encouragements[Math.floor(Math.random() * encouragements.length)]
  refreshAll()
})

onPullDownRefresh(async () => {
  await refreshAll()
  uni.stopPullDownRefresh()
})
</script>

<style scoped>
.home-page {
  padding: var(--page-padding-top) var(--page-padding-h);
  padding-bottom: 80px;
  min-height: 100vh;
  background: var(--color-bg-light);
}

.home-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.home-header__left {
  flex: 1;
}

.home-header__greeting {
  font-size: var(--font-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.home-header__quote {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
  display: block;
  line-height: var(--leading-relaxed);
}
/* PLACEHOLDER_STYLE_REST */

.home-header__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary-light);
  border: 2px solid var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: var(--space-md);
}

.home-header__avatar-emoji {
  font-size: 24px;
}

/* Project Card */
.home-project-card {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-xl);
}

.project-card__header {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.project-card__icon {
  font-size: 20px;
  margin-right: var(--space-xs);
}

.project-card__title {
  flex: 1;
  font-size: var(--font-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}

.project-card__badge {
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
  padding: 4px 10px;
}

.project-card__badge-text {
  font-size: var(--font-xs);
  color: var(--color-primary);
  font-weight: var(--weight-semibold);
}

.project-card__progress {
  height: 12px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-md);
}

.project-card__progress-bar {
  height: 100%;
  background: var(--gradient-progress);
  border-radius: var(--radius-full);
  transition: width 300ms ease-out;
}

.project-card__stats {
  display: flex;
}

.project-card__stat {
  flex: 1;
}

.project-card__stat-value {
  font-size: var(--font-md);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.project-card__stat-label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}
/* PLACEHOLDER_STYLE_2 */

/* Action Buttons Grid */
.home-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm);
  margin-bottom: var(--space-xl);
}

.action-btn {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  box-shadow: var(--shadow-card);
  transition: transform 150ms ease-out;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-btn__icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.action-btn__icon--blue { background: #EFF6FF; }
.action-btn__icon--purple { background: #F5F3FF; }
.action-btn__icon--green { background: #ECFDF5; }
.action-btn__icon--orange { background: #FFF7ED; }

.action-btn__label {
  font-size: var(--font-xs);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
}

/* Tasks Card */
.home-tasks-card {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-card);
}

.home-tasks__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  display: block;
  margin-bottom: var(--space-sm);
}

.home-tasks__list {
  display: flex;
  flex-direction: column;
}

.task-item {
  display: flex;
  align-items: center;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-gray-100);
}

.task-item:last-child {
  border-bottom: none;
}

.task-item--done {
  background: var(--color-green-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm);
  margin: 2px 0;
  border-bottom: none;
}

.task-item__checkbox {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--color-gray-300);
  margin-right: var(--space-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-item__checkbox--checked {
  background: var(--color-green-400);
  border-color: var(--color-green-400);
}

.task-item__check {
  color: white;
  font-size: 12px;
  font-weight: var(--weight-bold);
}

.task-item__text {
  font-size: 15px;
  color: var(--color-text-primary);
  line-height: var(--leading-normal);
}

.task-item__text--done {
  color: var(--color-text-muted);
  text-decoration: line-through;
}

/* Skeleton */
.home-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.skeleton-card {
  border-radius: var(--card-radius);
  background: var(--color-gray-200);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-card--project { height: 140px; }
.skeleton-card--actions { height: 100px; }
.skeleton-card--tasks { height: 180px; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* Error */
.home-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl) var(--space-lg);
}

.home-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
  text-align: center;
}

.home-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
}

.home-error__retry-text {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
}
</style>