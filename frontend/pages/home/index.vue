<template>
  <view class="home-page">
    <!-- Header: greeting + streak -->
    <view class="home-header">
      <view class="home-header__greeting">
        <text class="home-header__time">{{ greeting }}</text>
        <text class="home-header__sub">，{{ userStore.nickname }}</text>
      </view>
      <text v-if="userStore.streak > 0" class="home-header__streak">
        坚持的第 {{ userStore.streak }} 天 ✨
      </text>
    </view>

    <!-- Loading skeleton -->
    <view v-if="isLoading" class="home-skeleton">
      <view class="skeleton-card skeleton-card--level" />
      <view class="skeleton-card skeleton-card--quest" />
      <view class="skeleton-card skeleton-card--tasks" />
      <view class="skeleton-card skeleton-card--dream" />
    </view>

    <!-- Error state -->
    <view v-else-if="hasError" class="home-error">
      <text class="home-error__text">加载失败: {{ error }}</text>
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
      <!-- Quick start actions -->
      <view class="home-quick-actions">
        <view class="quick-action quick-action--gold" @tap="goImport">
          <text class="quick-action__icon">🎯</text>
          <text class="quick-action__title">设置目标</text>
          <text class="quick-action__desc">导入学习计划</text>
        </view>
        <view class="quick-action quick-action--blue" @tap="goRewardSetup">
          <text class="quick-action__icon">🎁</text>
          <text class="quick-action__title">设置激励</text>
          <text class="quick-action__desc">配置梦想奖励</text>
        </view>
      </view>
    </view>

    <!-- Normal content -->
    <template v-else>
      <!-- LevelCard -->
      <view class="home-section" @tap="goProfile">
        <LevelCard
          :level="userStore.level"
          :title="userStore.computedLevelTitle"
          :xp="userStore.xp"
          :xpToNext="userStore.xpToNextLevel"
          :streak="userStore.streak"
        />
      </view>

      <!-- Main Quest Progress -->
      <view v-if="projectStore.currentProject" class="home-section">
        <text class="home-section__title">今日主线任务</text>
        <view class="home-quest-card">
          <text class="home-quest__name">
            {{ categoryIcon(projectStore.currentProject) }} {{ projectStore.currentProject.title }}
          </text>
          <ProgressBar
            :value="projectStore.overallProgress"
            :max="100"
            size="normal"
            color="blue"
            showLabel
          />
          <text class="home-quest__sub" v-if="projectStore.currentProject.description">
            {{ projectStore.currentProject.description }}
          </text>
        </view>
      </view>

      <!-- Today Task Preview -->
      <view v-if="taskStore.todayTasks.length > 0" class="home-section">
        <view class="home-section__header">
          <text class="home-section__title">今日任务 ({{ taskStore.totalCount }})</text>
          <text class="home-section__link" @tap="goTasks">查看全部 →</text>
        </view>
        <view class="home-tasks-list">
          <TaskCard
            v-for="task in taskStore.todayTasks.slice(0, 3)"
            :key="task.id"
            :task="task"
            variant="checkbox"
            size="compact"
            @toggle="handleTaskToggle"
          />
        </view>
      </view>

      <!-- Dream Mini Progress -->
      <view v-if="rewardStore.rewardTitle" class="home-section" @tap="goReward">
        <text class="home-section__title">梦想奖励</text>
        <view class="home-dream-card">
          <text class="home-dream__name">🎁 {{ rewardStore.rewardTitle }} ¥{{ rewardStore.rewardPrice }}</text>
          <ProgressBar
            :value="rewardStore.progressPercent"
            :max="100"
            size="normal"
            color="gold"
            showLabel
          />
          <text class="home-dream__stats">
            ¥{{ rewardStore.accumulatedValue }}/¥{{ rewardStore.rewardPrice }}
          </text>
          <text v-if="rewardStore.etaDate" class="home-dream__eta">
            预计 {{ rewardStore.etaDate }} 完成
          </text>
        </view>
      </view>

      <!-- Encouragement Card -->
      <view class="home-section">
        <view class="home-encouragement" @tap="refreshEncouragement">
          <text class="home-encouragement__text">{{ encouragement }}</text>
        </view>
      </view>

      <!-- Quick Actions -->
      <view class="home-quick-actions">
        <view class="quick-action quick-action--gold" @tap="goImport">
          <text class="quick-action__icon">🎯</text>
          <text class="quick-action__title">设置目标</text>
        </view>
        <view class="quick-action quick-action--blue" @tap="goRewardSetup">
          <text class="quick-action__icon">🎁</text>
          <text class="quick-action__title">设置激励</text>
        </view>
      </view>
    </template>

    <!-- Fly-in animation overlay -->
    <view v-if="flyIn.visible" class="fly-container">
      <text
        class="fly-text fly-text--xp"
        :style="{
          '--fly-x': flyIn.xpX + 'px',
          '--fly-y': flyIn.xpY + 'px',
          animationDelay: '0ms'
        }"
      >+{{ flyIn.xp }} XP</text>
      <text
        class="fly-text fly-text--dream"
        :style="{
          '--fly-x': flyIn.dreamX + 'px',
          '--fly-y': flyIn.dreamY + 'px',
          animationDelay: '100ms'
        }"
      >+{{ flyIn.dream }} 梦想值</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useProjectStore } from '@/store/project'
import { useTaskStore } from '@/store/task'
import { useRewardStore } from '@/store/reward'
import LevelCard from '@/components/LevelCard.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import TaskCard from '@/components/TaskCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const userStore = useUserStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const rewardStore = useRewardStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const encouragement = ref('每一次微小的坚持，都在重塑未来的你。')

/* Fly-in animation state */
const flyIn = ref({ visible: false, xp: 0, dream: 0, xpX: 0, xpY: 0, dreamX: 0, dreamY: 0 })

const encouragements = [
  '每一次微小的坚持，都在重塑未来的你。',
  '学习的复利效应，会在某一天给你惊喜。',
  '昨天的你决定了今天的你，今天的你塑造明天的你。',
  '成长不是一蹴而就，而是日积月累的奇迹。',
  '与其焦虑远方，不如做好今天的任务。',
  '每天进步1% 一年后你将成长37倍。'
]

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '凌晨好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

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

function refreshEncouragement() {
  const idx = Math.floor(Math.random() * encouragements.length)
  encouragement.value = encouragements[idx]
}

function categoryIcon(project) {
  return '📚'
}

function handleTaskToggle(tid) {
  taskStore.toggleTaskLocally(tid)
}

function goProfile() {
  uni.switchTab({ url: '/pages/profile/index' })
}

function goTasks() {
  uni.switchTab({ url: '/pages/task/index' })
}

function goReward() {
  uni.switchTab({ url: '/pages/reward/index' })
}

function goImport() {
  uni.navigateTo({ url: '/pages/import/index' })
}

function goRewardSetup() {
  uni.navigateTo({ url: '/pages/reward/index' })
}

/* Fly-in animation trigger */
function triggerFlyIn(xp, dream) {
  const query = uni.createSelectorQuery()
  query.select('.home-dream-card').boundingClientRect()
  query.exec((res) => {
    const target = res[0]
    if (!target) return

    const systemInfo = uni.getSystemInfoSync()
    const screenW = systemInfo.windowWidth
    const screenH = systemInfo.windowHeight

    // Start from bottom-center (checkin button position)
    const startX = screenW / 2
    const startY = screenH - 120

    // Target is dream card center
    const targetX = target.left + target.width / 2
    const targetY = target.top + target.height / 2

    flyIn.value = {
      visible: true,
      xp,
      dream,
      xpX: targetX - startX,
      xpY: targetY - startY,
      dreamX: targetX - startX,
      dreamY: targetY - startY + 24
    }

    setTimeout(() => {
      flyIn.value.visible = false
    }, 1600)
  })
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.home-page {
  padding: 0 var(--page-padding-h) var(--section-gap);
  min-height: 100vh;
}

.home-header {
  margin-bottom: var(--section-gap);
}

.home-header__greeting {
  font-size: var(--font-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
}

.home-header__time {
  display: inline;
}

.home-header__sub {
  display: inline;
  font-weight: var(--weight-normal);
}

.home-header__streak {
  display: block;
  font-size: var(--font-sm);
  color: var(--color-gold-400);
  margin-top: 4px;
}

.home-section {
  margin-bottom: var(--section-gap);
}

.home-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.home-section__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
  display: block;
}

.home-section__link {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.home-quest-card {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-card);
}

.home-quest__name {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
  margin-bottom: var(--space-xs);
  display: block;
}

.home-quest__sub {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
  display: block;
  margin-top: var(--space-xs);
  line-height: var(--leading-relaxed);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.home-tasks-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.home-dream-card {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-card);
}

.home-dream__name {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
  margin-bottom: var(--space-xs);
  display: block;
}

.home-dream__stats {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
  display: block;
}

.home-dream__eta {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  display: block;
  margin-top: 2px;
}

.home-encouragement {
  background: var(--gradient-encouragement);
  border-radius: var(--card-radius);
  padding: var(--space-lg);
}

.home-encouragement__text {
  font-size: var(--font-sm);
  color: var(--color-text-inverse);
  font-style: italic;
  line-height: var(--leading-relaxed);
  opacity: 0.9;
}

/* Quick Actions */
.home-quick-actions {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--section-gap);
}

.quick-action {
  flex: 1;
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--space-md);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xxs);
  transition: transform 150ms var(--anim-ease-out);
}

.quick-action:active {
  transform: scale(0.97);
}

.quick-action__icon {
  font-size: 28px;
}

.quick-action__title {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}

.quick-action__desc {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
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

.skeleton-card--level { height: 120px; }
.skeleton-card--quest { height: 80px; }
.skeleton-card--tasks { height: 150px; }
.skeleton-card--dream { height: 90px; }

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

/* Fly-in animation */
.fly-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: var(--z-animation, 800);
}

.fly-text {
  position: absolute;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  font-weight: var(--weight-bold);
  animation: fly-to-target 1500ms cubic-bezier(0.4, 0, 0.6, 1) forwards;
}

.fly-text--xp {
  color: #3B82F6;
  font-size: 20px;
  text-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
}

.fly-text--dream {
  color: #FFD700;
  font-size: 18px;
  text-shadow: 0 1px 4px rgba(255, 215, 0, 0.4);
}

@keyframes fly-to-target {
  0% {
    opacity: 0;
    transform: translate(-50%, 0) scale(0.5);
  }
  15% {
    opacity: 1;
    transform: translate(calc(-50% + var(--fly-x) * 0.1), calc(var(--fly-y) * 0.1)) scale(1);
  }
  70% {
    opacity: 0.8;
    transform: translate(calc(-50% + var(--fly-x) * 0.85), calc(var(--fly-y) * 0.85)) scale(0.7);
  }
  100% {
    opacity: 0;
    transform: translate(calc(-50% + var(--fly-x)), var(--fly-y)) scale(0.4);
  }
}
</style>
