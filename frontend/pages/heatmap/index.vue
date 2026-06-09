<template>
  <view class="heatmap-page">
    <!-- Nav header -->
    <view class="heatmap-nav">
      <text class="heatmap-nav__title">成长热力图</text>
    </view>

    <!-- Loading -->
    <view v-if="isLoading" class="heatmap-skeleton">
      <view class="heatmap-skeleton__title" />
      <view class="heatmap-skeleton__grid" />
      <view class="heatmap-skeleton__stats" />
    </view>

    <!-- Error -->
    <view v-else-if="hasError" class="heatmap-error">
      <text class="heatmap-error__text">{{ error }}</text>
      <view class="heatmap-error__retry" @tap="loadHeatmap">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty -->
    <view v-else-if="heatmapData && heatmapData.stats.total_days_active === 0" class="heatmap-empty">
      <text class="heatmap-empty__icon">📈</text>
      <text class="heatmap-empty__title">还没有打卡记录</text>
      <text class="heatmap-empty__desc">完成今日任务来点亮第一格吧!</text>
      <view class="heatmap-empty__link" @tap="goTasks">
        <text>去做任务 →</text>
      </view>
    </view>

    <!-- Normal -->
    <scroll-view v-else class="heatmap-content" scroll-y>
      <!-- Year header -->
      <view class="heatmap-year-header">
        <text class="heatmap-year">{{ heatmapYear }}</text>
        <text class="heatmap-total">共 {{ heatmapData.stats.total_checkins }} 次打卡</text>
      </view>

      <!-- Heatmap grid -->
      <view class="heatmap-grid-container">
        <!-- Weekday labels (sticky left) -->
        <view class="heatmap-weekdays">
          <text
            v-for="(label, idx) in weekLabels"
            :key="label"
            class="heatmap-weekday"
            :style="{ marginTop: idx === 0 ? '20px' : '2px' }"
          >{{ label }}</text>
        </view>

        <!-- Scrollable grid -->
        <scroll-view class="heatmap-scroll" scroll-x :show-scrollbar="false">
          <view class="heatmap-grid-wrapper">
            <!-- Month labels row -->
            <view class="heatmap-months">
              <text
                v-for="(pos, month) in monthPositions"
                :key="month"
                class="heatmap-month"
                :style="{ marginLeft: pos === 0 ? '0px' : ((pos - (monthPositions[Object.keys(monthPositions)[Object.keys(monthPositions).indexOf(month) - 1]] || 0)) * 14 + 'px') }"
              >{{ month }}月</text>
            </view>

            <!-- Grid cells -->
            <view class="heatmap-grid">
              <view
                v-for="(row, rowIdx) in heatmapGrid"
                :key="rowIdx"
                class="heatmap-row"
              >
                <view
                  v-for="(cell, colIdx) in row"
                  :key="colIdx"
                  class="heatmap-cell"
                  :class="['heatmap-cell--' + cell.level]"
                  :style="cell.isToday ? { border: '1px solid #4A9EFF' } : {}"
                  @tap="showTooltip($event, cell)"
                />
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Tooltip -->
      <view
        v-if="tooltip.visible"
        class="heatmap-tooltip"
        :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
      >
        <text class="heatmap-tooltip__date">{{ tooltip.date }}</text>
        <text class="heatmap-tooltip__count">{{ tooltip.checkins }}次打卡</text>
        <text class="heatmap-tooltip__xp">{{ tooltip.xp }} XP</text>
      </view>

      <!-- Stats section -->
      <view class="heatmap-stats">
        <view class="heatmap-stats__title">统计</view>
        <view class="heatmap-stats-grid">
          <view class="heatmap-stat">
            <text class="heatmap-stat__value">{{ heatmapData.stats.total_days_active }}</text>
            <text class="heatmap-stat__label">活跃天数</text>
          </view>
          <view class="heatmap-stat">
            <text class="heatmap-stat__value">{{ heatmapData.stats.longest_streak }}</text>
            <text class="heatmap-stat__label">最长连续(天)</text>
          </view>
          <view class="heatmap-stat">
            <text class="heatmap-stat__value">{{ heatmapData.stats.total_checkins }}</text>
            <text class="heatmap-stat__label">总打卡</text>
          </view>
          <view class="heatmap-stat">
            <text class="heatmap-stat__value">{{ avgXpPerDay }}</text>
            <text class="heatmap-stat__label">日均 XP</text>
          </view>
        </view>
      </view>

      <!-- Legend -->
      <view class="heatmap-legend">
        <text class="heatmap-legend__label">色阶说明</text>
        <view class="heatmap-legend__colors">
          <view class="heatmap-legend__item" v-for="(color, idx) in legendColors" :key="idx">
            <view class="heatmap-legend__swatch" :class="'heatmap-cell--' + idx" />
            <text class="heatmap-legend__text">{{ idx === 0 ? '无' : idx === 4 ? '4+' : idx + '次' }}</text>
          </view>
        </view>
      </view>

      <view class="heatmap-bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const heatmapData = ref(null)
const tooltip = ref({ visible: false, x: 0, y: 0 })

const weekLabels = ['一', '二', '三', '四', '五', '六', '日']
const legendColors = ['#1A1D22', '#0e4429', '#006d32', '#26a641', '#39d353']

const heatmapYear = computed(() => heatmapData.value?.year || new Date().getFullYear())

const avgXpPerDay = computed(() => {
  const avg = heatmapData.value?.stats?.average_xp_per_day
  return avg != null ? Number(avg).toFixed(1) : '0'
})

function getMonthPositions(daysData) {
  const positions = {}
  const today = new Date()
  const daysAgo = 365

  for (let i = daysAgo - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    const col = i

    const month = d.getMonth() + 1
    const monthName = month + '月'
    if (!(monthName in positions)) {
      positions[monthName] = Math.floor(col / 7)
    }
  }
  return positions
}

function getColorLevel(checkins) {
  if (checkins <= 0) return 0
  if (checkins === 1) return 1
  if (checkins === 2) return 2
  if (checkins === 3) return 3
  return 4
}

const heatmapGrid = computed(() => {
  if (!heatmapData.value?.days) return []

  const today = new Date()
  const daysMap = {}
  if (heatmapData.value.days) {
    for (const d of heatmapData.value.days) {
      daysMap[d.date] = d
    }
  }

  const rows = Array.from({ length: 7 }, () => [])
  for (let i = 364; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    const dayOfWeek = d.getDay() // 0=Sun, 1=Mon, ...
    const rowIdx = dayOfWeek === 0 ? 6 : dayOfWeek - 1

    const dayStats = daysMap[dateStr]
    const checkins = dayStats ? (dayStats.count || 0) : 0
    const level = getColorLevel(checkins)
    const isToday = dateStr === today.toISOString().slice(0, 10)

    rows[rowIdx].push({
      date: dateStr,
      checkins,
      xp: dayStats ? (dayStats.xp || 0) : 0,
      level,
      isToday
    })
  }
  return rows
})

const monthPositions = computed(() => {
  if (!heatmapData.value?.days) return {}
  return getMonthPositions(heatmapData.value.days)
})

function showTooltip(e, cell) {
  if (!cell.date || cell.checkins === 0) {
    tooltip.value.visible = false
    return
  }

  const d = new Date(cell.date)
  tooltip.value = {
    visible: true,
    date: `${d.getMonth() + 1}月${d.getDate()}日`,
    checkins: cell.checkins,
    xp: cell.xp,
    x: Math.min(e.detail?.x || 0, 220),
    y: Math.max((e.detail?.y || 0) - 80, 10)
  }

  clearTimeout(tooltip.value._timer)
  tooltip.value._timer = setTimeout(() => {
    tooltip.value.visible = false
  }, 3000)
}

async function loadHeatmap() {
  isLoading.value = true
  hasError.value = false

  try {
    const data = await api.getHeatmap(365)
    heatmapData.value = {
      year: new Date().getFullYear(),
      totalCheckins: data.stats?.total_checkins || 0,
      days: data.heatmap || [],
      stats: data.stats || {}
    }
  } catch (err) {
    hasError.value = true
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

function goTasks() {
  uni.switchTab({ url: '/pages/task/index' })
}

onMounted(() => {
  loadHeatmap()
})
</script>

<style scoped>
.heatmap-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.heatmap-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  height: var(--nav-header-height);
  padding: 0 var(--page-padding-h);
  background: var(--color-bg-card-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.heatmap-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}

/* Content */
.heatmap-content {
  padding: var(--space-lg) var(--page-padding-h);
}

/* Year header */
.heatmap-year-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.heatmap-year {
  font-size: var(--font-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.heatmap-total {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  margin-top: 4px;
  display: block;
}

/* Grid container */
.heatmap-grid-container {
  display: flex;
  margin-bottom: var(--space-xl);
}

/* Weekday labels */
.heatmap-weekdays {
  display: flex;
  flex-direction: column;
  width: 24px;
  flex-shrink: 0;
  position: sticky;
  left: 0;
  z-index: 2;
  background: var(--color-bg-light);
}

.heatmap-weekday {
  font-size: 10px;
  color: var(--color-text-muted);
  line-height: 14px;
  height: 14px;
}

/* Scrollable area */
.heatmap-scroll {
  flex: 1;
  white-space: nowrap;
}

.heatmap-grid-wrapper {
  display: inline-block;
}

/* Month labels */
.heatmap-months {
  display: flex;
  height: 20px;
  align-items: flex-end;
}

.heatmap-month {
  font-size: 10px;
  color: var(--color-text-muted);
  line-height: 14px;
}

/* Heatmap grid */
.heatmap-grid {
  display: flex;
  flex-direction: column;
}

.heatmap-row {
  display: flex;
  gap: 2px;
  height: 14px;
}

.heatmap-cell {
  width: var(--heatmap-cell-size, 12px);
  height: var(--heatmap-cell-size, 12px);
  border-radius: 2px;
  flex-shrink: 0;
  transition: transform 150ms var(--anim-ease-out, cubic-bezier(0, 0, 0.2, 1));
}

.heatmap-cell:active {
  transform: scale(1.5);
}

.heatmap-cell--0 { background: var(--heatmap-0, #1A1D22); }
.heatmap-cell--1 { background: var(--heatmap-1, #0e4429); }
.heatmap-cell--2 { background: var(--heatmap-2, #006d32); }
.heatmap-cell--3 { background: var(--heatmap-3, #26a641); }
.heatmap-cell--4 { background: var(--heatmap-4, #39d353); }

/* Tooltip */
.heatmap-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 160px;
  z-index: var(--z-tooltip, 900);
  pointer-events: none;
  animation: tooltip-in 150ms ease-out;
}

@keyframes tooltip-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.heatmap-tooltip__date {
  font-size: 12px;
  font-weight: var(--weight-bold);
  display: block;
}

.heatmap-tooltip__count,
.heatmap-tooltip__xp {
  font-size: 12px;
  display: block;
  margin-top: 2px;
}

/* Stats */
.heatmap-stats {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius, 16px);
  padding: var(--card-padding, 16px);
  margin-bottom: var(--space-xl);
  box-shadow: var(--shadow-card);
}

.heatmap-stats__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.heatmap-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xs, 8px);
}

.heatmap-stat {
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-sm, 8px);
  padding: var(--space-sm, 12px);
  text-align: center;
}

.heatmap-stat__value {
  font-size: var(--font-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.heatmap-stat__label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
  display: block;
}

/* Legend */
.heatmap-legend {
  margin-bottom: var(--space-xl);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  justify-content: center;
}

.heatmap-legend__label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.heatmap-legend__colors {
  display: flex;
  gap: 4px;
  align-items: center;
}

.heatmap-legend__item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.heatmap-legend__swatch {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.heatmap-legend__text {
  font-size: 10px;
  color: var(--color-text-muted);
}

.heatmap-bottom-spacer {
  height: 80px;
}

/* Empty */
.heatmap-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80px;
}

.heatmap-empty__icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.heatmap-empty__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.heatmap-empty__desc {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-lg);
}

.heatmap-empty__link {
  color: var(--color-blue-400);
  font-size: var(--font-sm);
}

/* Skeleton */
.heatmap-skeleton {
  padding: var(--space-xl) var(--page-padding-h);
}

.heatmap-skeleton__title {
  width: 120px;
  height: 24px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin: 0 auto var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.heatmap-skeleton__grid {
  width: 100%;
  height: 100px;
  background: var(--color-gray-200);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.heatmap-skeleton__stats {
  width: 100%;
  height: 120px;
  background: var(--color-gray-200);
  border-radius: var(--radius-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

/* Error */
.heatmap-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.heatmap-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.heatmap-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
