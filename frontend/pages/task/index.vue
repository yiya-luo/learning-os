<template>
  <view class="task-page">
    <!-- Nav header -->
    <view class="task-nav">
      <text class="task-nav__back" @tap="goBack">← 返回</text>
      <text class="task-nav__title">今日任务</text>
      <text v-if="taskStore.estimatedTime > 0" class="task-nav__time">
        {{ formatTime(taskStore.estimatedTime) }}
      </text>
    </view>

    <!-- Loading skeleton -->
    <view v-if="isLoading" class="task-skeleton">
      <view v-for="i in 3" :key="i" class="task-skeleton__section">
        <view class="task-skeleton__header" />
        <view v-for="j in 3" :key="j" class="task-skeleton__row" />
      </view>
    </view>

    <!-- Error -->
    <view v-else-if="hasError" class="task-error">
      <text class="task-error__text">{{ error }}</text>
      <view class="task-error__retry" @tap="loadTasks">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty -->
    <view v-else-if="taskStore.totalCount === 0">
      <EmptyState
        icon="📋"
        title="今天没有任务"
        description="去学习地图添加任务吧"
        action-text="去学习地图"
        @action="goMap"
      />
    </view>

    <!-- Task Sections -->
    <scroll-view v-else class="task-content" scroll-y>
      <!-- Theory section -->
      <view v-if="taskStore.theoryTasks.length > 0" class="task-section">
        <view class="task-section__header">
          <text class="task-section__icon">📖</text>
          <text class="task-section__title">理论</text>
          <text class="task-section__count">
            ({{ sectionDoneCount(taskStore.theoryTasks) }}/{{ taskStore.theoryTasks.length }})
          </text>
        </view>
        <view class="task-section__list">
          <TaskCard
            v-for="task in taskStore.theoryTasks"
            :key="task.id"
            :task="task"
            variant="checkbox"
            @toggle="handleToggle"
            @tap="handleTaskTap(task)"
          />
        </view>
      </view>

      <!-- Practice section -->
      <view v-if="taskStore.practiceTasks.length > 0" class="task-section">
        <view class="task-section__header">
          <text class="task-section__icon">✏️</text>
          <text class="task-section__title">练习</text>
          <text class="task-section__count">
            ({{ sectionDoneCount(taskStore.practiceTasks) }}/{{ taskStore.practiceTasks.length }})
          </text>
        </view>
        <view class="task-section__list">
          <TaskCard
            v-for="task in taskStore.practiceTasks"
            :key="task.id"
            :task="task"
            variant="checkbox"
            @toggle="handleToggle"
            @tap="handleTaskTap(task)"
          />
        </view>
      </view>

      <!-- Output section -->
      <view v-if="taskStore.outputTasks.length > 0" class="task-section">
        <view class="task-section__header">
          <text class="task-section__icon">💬</text>
          <text class="task-section__title">输出</text>
          <text class="task-section__count">
            ({{ sectionDoneCount(taskStore.outputTasks) }}/{{ taskStore.outputTasks.length }})
          </text>
        </view>
        <view class="task-section__list">
          <TaskCard
            v-for="task in taskStore.outputTasks"
            :key="task.id"
            :task="task"
            variant="checkbox"
            @toggle="handleToggle"
            @tap="handleTaskTap(task)"
          />
        </view>
      </view>

      <!-- Reward preview -->
      <view class="task-reward-preview">
        <text class="task-reward__title">完成后可获得</text>
        <view class="task-reward__values">
          <text class="task-reward__xp">⚡ +{{ taskStore.totalXP }} XP</text>
        </view>
      </view>

      <!-- Checkin button -->
      <view class="task-checkin-wrapper">
        <view
          class="task-checkin-btn"
          :class="checkinBtnClass"
          @tap="handleCheckin"
        >
          <text v-if="checkinLoading" class="task-checkin__spinner" />
          <text v-else-if="checkinSuccess" class="task-checkin__label">✅ 全部完成,打卡!</text>
          <text v-else class="task-checkin__label">✨ 完成打卡</text>
        </view>
      </view>

      <!-- Bottom padding -->
      <view class="task-bottom-spacer" />
    </scroll-view>

    <!-- Checkin Animation -->
    <CheckinAnimation
      :visible="showAnimation"
      :xpGained="animationXP"
      :dreamGained="animationDream"
      @complete="onAnimationComplete"
      @dismiss="showAnimation = false"
    />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useUserStore } from '@/store/user'
import { useProjectStore } from '@/store/project'
import { useTaskStore } from '@/store/task'
import { useRewardStore } from '@/store/reward'
import { useEncouragementStore } from '@/store/encouragement'
import TaskCard from '@/components/TaskCard.vue'
import CheckinAnimation from '@/components/CheckinAnimation.vue'
import EmptyState from '@/components/EmptyState.vue'

const userStore = useUserStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const rewardStore = useRewardStore()
const encouragementStore = useEncouragementStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const checkinLoading = ref(false)
const checkinSuccess = ref(false)
const showAnimation = ref(false)
const animationXP = ref(0)
const animationDream = ref(0)

const checkinBtnClass = computed(() => ({
  'task-checkin-btn--disabled': taskStore.totalCount === 0,
  'task-checkin-btn--active': taskStore.allDone,
  'task-checkin-btn--loading': checkinLoading.value
}))

function formatTime(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

function sectionDoneCount(tasks) {
  return tasks.filter(t => t.status === 'done').length
}

function handleToggle(tid) {
  taskStore.toggleTaskLocally(tid)
}

function handleTaskTap(task) {
  if (task.status !== 'doing') {
    taskStore.startTask(task.id).then(result => {
      if (result) {
        const t = taskStore.todayTasks.find(t => t.id === task.id)
        if (t) t.status = 'doing'
      }
    })
  }
}

async function handleCheckin() {
  if (taskStore.totalCount === 0 || checkinLoading.value) return

  const tasksToCheckin = taskStore.todayTasks.filter(
    t => t.status === 'doing' || t.status === 'done'
  )

  if (tasksToCheckin.length === 0) {
    uni.showToast({ title: '请先开始任务', icon: 'none' })
    return
  }

  checkinLoading.value = true

  try {
    // Check in the first doing task and accumulate rewards
    let totalXP = 0
    let totalDream = 0

    for (const task of tasksToCheckin) {
      try {
        const result = await taskStore.checkin(task.id)
        totalXP += result.xp_earned || 0
        totalDream += result.dream_value_earned || 0
        task.status = 'done'
        if (result.new_total_xp !== undefined) {
          userStore.applyCheckinResult(result)
        }
        break // Only checkin one task to trigger the animation
      } catch (e) {
        // Continue to next
      }
    }

    // Trigger encouragement after checkin
    const pid = projectStore.currentProjectId
    if (pid && tasksToCheckin.length > 0) {
      try {
        const encResult = await api.triggerEncouragement(pid, 'checkin', tasksToCheckin[0].id)
        if (encResult && encResult.type) {
          encouragementStore.show(encResult)
        }
      } catch (e) {
        // Encouragement fetch failure is non-blocking
      }
    }

    animationXP.value = totalXP || taskStore.totalXP
    animationDream.value = totalDream || 5

    checkinSuccess.value = true
    showAnimation.value = true

    try {
      uni.vibrateShort({ type: 'light' })
    } catch (e) {}

    // Refresh reward progress after checkin
    if (pid) {
      rewardStore.fetchRewardProgress(pid)
    }
  } catch (e) {
    uni.showToast({ title: '打卡失败，请重试', icon: 'none' })
  } finally {
    checkinLoading.value = false
  }
}

function onAnimationComplete() {
  showAnimation.value = false
  checkinSuccess.value = false
}

function loadTasks() {
  const pid = projectStore.currentProjectId
  if (!pid) {
    isLoading.value = false
    hasError.value = false
    return
  }

  isLoading.value = true
  hasError.value = false

  taskStore.fetchTodayTasks(pid)
    .then(() => { isLoading.value = false })
    .catch(err => {
      hasError.value = true
      error.value = err.message
      isLoading.value = false
    })
}

function goBack() { uni.switchTab({ url: '/pages/home/index' }) }
function goMap() { uni.switchTab({ url: '/pages/map/index' }) }

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.task-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.task-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-header-height);
  padding: 0 var(--page-padding-h);
  background: var(--color-bg-card-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.task-nav__back {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.task-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.task-nav__time {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
}

.task-content {
  padding: var(--space-md) var(--page-padding-h);
}

.task-section {
  margin-bottom: var(--section-gap);
}

.task-section__header {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.task-section__icon {
  font-size: var(--font-md);
  margin-right: var(--space-xs);
}

.task-section__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.task-section__count {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-left: var(--space-xs);
}

.task-section__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.task-reward-preview {
  background: rgba(230, 185, 61, 0.06);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  text-align: center;
  margin: var(--space-lg) 0;
}

.task-reward__title {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  display: block;
  margin-bottom: 4px;
}

.task-reward__values {
  display: flex;
  justify-content: center;
  gap: var(--space-lg);
}

.task-reward__xp {
  font-size: var(--font-md);
  color: var(--color-gold-400);
  font-weight: var(--weight-semibold);
}

.task-checkin-wrapper {
  padding: var(--space-lg) 0;
}

.task-checkin-btn {
  height: var(--btn-height-lg);
  border-radius: var(--radius-full);
  background: var(--color-gold-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-button);
  transition: all var(--anim-duration-fast) ease-out;
  width: 100%;
}

.task-checkin-btn:active {
  transform: scale(0.96);
  box-shadow: none;
}

.task-checkin-btn--disabled {
  opacity: 0.4;
  pointer-events: none;
}

.task-checkin-btn--active {
  background: linear-gradient(135deg, var(--color-green-400), var(--color-green-300));
}

.task-checkin-btn--loading {
  opacity: 0.9;
}

.task-checkin__label {
  font-size: var(--font-md);
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}

.task-checkin__spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 600ms linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.task-bottom-spacer {
  height: 40px;
}

/* Skeleton */
.task-skeleton__section {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  margin-bottom: var(--space-md);
}

.task-skeleton__header {
  height: 20px;
  width: 100px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin-bottom: var(--space-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.task-skeleton__row {
  height: 44px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin-bottom: var(--space-xs);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* Error */
.task-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.task-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.task-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}
</style>
