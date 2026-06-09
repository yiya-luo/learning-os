<template>
  <view class="analytics-page">
    <!-- Nav header -->
    <view class="analytics-nav">
      <text class="analytics-nav__back" @tap="goBack">← 返回</text>
      <text class="analytics-nav__title">数据洞察</text>
      <view style="width:48px" />
    </view>

    <!-- Loading -->
    <view v-if="analyticsStore.loading" class="analytics-loading">
      <view class="analytics-skeleton__section" v-for="i in 5" :key="i">
        <view class="analytics-skeleton__title" />
        <view class="analytics-skeleton__content" />
      </view>
    </view>

    <!-- Error -->
    <view v-else-if="analyticsStore.error && !analyticsStore.analyticsData" class="analytics-error">
      <text class="analytics-error__text">{{ analyticsStore.error }}</text>
      <view class="analytics-error__retry" @tap="retryLoad">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty -->
    <view v-else-if="analyticsStore.isEmpty" class="analytics-empty">
      <text class="analytics-empty__emoji">📊</text>
      <text class="analytics-empty__text">还没有足够的数据，完成一些任务后再来看看！</text>
    </view>

    <!-- Dashboard -->
    <scroll-view v-else class="analytics-content" scroll-y>
      <!-- Period selector -->
      <view class="period-selector">
        <view
          v-for="opt in analyticsStore.periodOptions"
          :key="opt.value"
          class="period-selector__item"
          :class="{ 'period-selector__item--active': analyticsStore.period === opt.value }"
          @tap="changePeriod(opt.value)"
        >
          <text class="period-selector__label">{{ opt.label }}</text>
        </view>
      </view>

      <!-- Comparison cards -->
      <view v-if="analyticsStore.analyticsData?.current" class="section">
        <text class="section__title">周期对比</text>
        <view class="comparison-grid">
          <view class="comparison-card" v-for="card in comparisonCards" :key="card.label">
            <text class="comparison-card__label">{{ card.label }}</text>
            <text class="comparison-card__value">{{ card.current }}</text>
            <view class="comparison-card__change" :class="card.changeClass">
              <text class="comparison-card__arrow">{{ card.arrow }}</text>
              <text class="comparison-card__pct">{{ card.change }}</text>
            </view>
            <text class="comparison-card__prev">{{ card.prevLabel }} {{ card.previous }}</text>
          </view>
        </view>
      </view>

      <!-- Daily trend -->
      <view v-if="analyticsStore.analyticsData?.trend?.length" class="section">
        <text class="section__title">每日趋势</text>
        <view class="trend-chart">
          <canvas
            canvas-id="trendCanvas"
            id="trendCanvas"
            class="trend-chart__canvas"
            @touchstart="onTrendTap"
          />
        </view>
      </view>

      <!-- Task type distribution -->
      <view v-if="analyticsStore.analyticsData?.task_type_distribution" class="section">
        <text class="section__title">任务类型分布</text>
        <view class="task-type-bars">
          <view
            v-for="item in taskTypeBars"
            :key="item.type"
            class="task-type-bar"
          >
            <text class="task-type-bar__label">{{ item.label }}</text>
            <view class="task-type-bar__track">
              <view
                class="task-type-bar__fill"
                :style="{ width: item.percent + '%', backgroundColor: item.color }"
              />
            </view>
            <text class="task-type-bar__value">{{ item.percent }}% ({{ item.count }})</text>
          </view>
        </view>
      </view>

      <!-- Radar chart -->
      <view v-if="analyticsStore.analyticsData?.radar" class="section">
        <text class="section__title">能力雷达</text>
        <view class="radar-chart">
          <canvas
            canvas-id="radarCanvas"
            id="radarCanvas"
            class="radar-chart__canvas"
          />
        </view>
      </view>

      <!-- Stage progress -->
      <view v-if="analyticsStore.analyticsData?.stage_progress?.length" class="section">
        <text class="section__title">阶段进度</text>
        <view class="stage-progress-list">
          <view
            v-for="stage in analyticsStore.analyticsData.stage_progress"
            :key="stage.stage_title"
            class="stage-progress-item"
          >
            <text class="stage-progress-item__name">{{ stage.stage_title }}</text>
            <view class="stage-progress-item__track">
              <view
                class="stage-progress-item__fill"
                :style="{ width: stage.percent + '%' }"
              />
            </view>
            <text class="stage-progress-item__value">{{ Math.round(stage.percent) }}% ({{ stage.done }}/{{ stage.total }})</text>
          </view>
        </view>
      </view>

      <!-- Summary grid -->
      <view v-if="analyticsStore.analyticsData?.summary" class="section">
        <text class="section__title">总览</text>
        <view class="summary-grid">
          <view class="summary-card">
            <text class="summary-card__label">总任务数</text>
            <text class="summary-card__value">{{ analyticsStore.analyticsData.summary.total_tasks_completed || 0 }}</text>
          </view>
          <view class="summary-card">
            <text class="summary-card__label">总经验值</text>
            <text class="summary-card__value">{{ formattedXP }}</text>
          </view>
          <view class="summary-card">
            <text class="summary-card__label">活跃天数</text>
            <text class="summary-card__value">{{ analyticsStore.analyticsData.summary.total_days_active || 0 }} 天</text>
          </view>
          <view class="summary-card">
            <text class="summary-card__label">最长连续</text>
            <text class="summary-card__value">{{ analyticsStore.analyticsData.summary.longest_streak || 0 }} 天</text>
          </view>
          <view class="summary-card">
            <text class="summary-card__label">最爱类型</text>
            <text class="summary-card__value">{{ favoriteTypeLabel }}</text>
          </view>
          <view class="summary-card">
            <text class="summary-card__label">首次打卡</text>
            <text class="summary-card__value">{{ firstCheckin }}</text>
          </view>
        </view>
      </view>

      <view class="analytics-bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAnalyticsStore } from '@/store/analytics'

const analyticsStore = useAnalyticsStore()

const comparisonCards = computed(() => {
  const d = analyticsStore.analyticsData
  if (!d?.current || !d?.previous) return []

  const items = [
    { key: 'tasks_completed', label: '完成任务', suffix: '' },
    { key: 'xp_earned', label: '获得XP', suffix: '' },
    { key: 'completion_rate', label: '完成率', suffix: '%', isRate: true }
  ]

  return items.map(item => {
    const cur = d.current[item.key]
    const prev = d.previous[item.key]
    const changeKey = item.key + '_pct'
    const change = d.changes?.[changeKey]

    let displayCur = item.isRate ? Math.round(cur * 100) : (cur || 0)
    let displayPrev = item.isRate ? Math.round(prev * 100) : (prev || 0)
    let changeText = analyticsStore.formatPct(change)
    let arrow = analyticsStore.getChangeArrow(change)
    let changeClass = analyticsStore.getChangeClass(change)

    return {
      label: item.label,
      current: displayCur + item.suffix,
      previous: displayPrev + item.suffix,
      prevLabel: analyticsStore.period === 'week' ? '上周' : analyticsStore.period === 'month' ? '上月' : '前段',
      change: changeText,
      arrow,
      changeClass: changeClass ? `comparison-card__change--${changeClass}` : ''
    }
  })
})

const favoriteTypeLabel = computed(() => {
  const ft = analyticsStore.analyticsData?.summary?.favorite_type
  const labels = { theory: '理论', practice: '练习', output: '输出' }
  return labels[ft] || ft || '--'
})

const formattedXP = computed(() => {
  const xp = analyticsStore.analyticsData?.summary?.total_xp || 0
  return xp >= 1000 ? (xp / 1000).toFixed(1) + 'k' : String(xp)
})

const firstCheckin = computed(() => {
  const d = analyticsStore.analyticsData?.summary?.first_checkin_date
  if (!d) return '--'
  const parts = d.split('-')
  if (parts.length === 3) return `${parseInt(parts[1])}-${parseInt(parts[2])}`
  return d
})

const taskTypeBars = computed(() => {
  const dist = analyticsStore.analyticsData?.task_type_distribution
  if (!dist) return []

  const colors = { theory: '#4A9EFF', practice: '#22C55E', output: '#F59E0B' }
  const labels = { theory: '理论', practice: '练习', output: '输出' }

  return ['theory', 'practice', 'output'].map(type => {
    const item = dist[type] || { count: 0, percent: 0 }
    return {
      type,
      label: labels[type] || type,
      count: item.count || 0,
      percent: Math.round((item.percent || 0) * 10) / 10,
      color: colors[type]
    }
  })
})

// Trend chart rendering
function drawTrendChart() {
  nextTick(() => {
    const ctx = uni.createCanvasContext('trendCanvas')
    const data = analyticsStore.analyticsData?.trend || []
    if (!data.length) return

    const width = 343
    const height = 120
    const padding = { top: 8, right: 8, bottom: 24, left: 30 }
    const chartW = width - padding.left - padding.right
    const chartH = height - padding.top - padding.bottom

    const maxXP = Math.max(...data.map(d => d.xp || 0), 1)
    const barWidth = Math.max(4, Math.min(10, chartW / data.length - 4))
    const gap = (chartW - barWidth * data.length) / (data.length + 1)

    // Y-axis labels
    ctx.setFontSize(10)
    ctx.setFillStyle('#8F99A3')
    for (let i = 0; i <= 4; i++) {
      const val = Math.round(maxXP * i / 4)
      const y = padding.top + chartH - (chartH * i / 4)
      ctx.fillText(String(val), 2, y + 3)
    }

    // Bars
    data.forEach((d, i) => {
      const x = padding.left + gap + i * (barWidth + gap)
      const barH = (d.xp || 0) / maxXP * chartH
      const y = padding.top + chartH - barH

      ctx.setFillStyle('#4A9EFF')
      ctx.setGlobalAlpha(0.8)
      ctx.fillRect(x, y, barWidth, barH)
      ctx.setGlobalAlpha(1)

      // Date label (abbreviated)
      if (i % Math.ceil(data.length / 7) === 0 || data.length <= 7) {
        const dateStr = d.date || ''
        const parts = dateStr.split('-')
        const label = parts.length === 3 ? `${parseInt(parts[1])}/${parseInt(parts[2])}` : ''
        ctx.setFontSize(8)
        ctx.setFillStyle('#8F99A3')
        ctx.fillText(label, x - 4, height - 2)
      }
    })

    ctx.draw()
  })
}

function onTrendTap(e) {
  const x = e.detail?.x || 0
  const data = analyticsStore.analyticsData?.trend || []
  if (!data.length) return

  const barWidth = Math.max(4, Math.min(10, (343 - 38 - 8) / data.length - 4))
  const gap = ((343 - 38 - 8) - barWidth * data.length) / (data.length + 1)
  const idx = Math.floor((x - 30 - gap) / (barWidth + gap))

  if (idx >= 0 && idx < data.length) {
    const d = data[idx]
    const parts = (d.date || '').split('-')
    const label = parts.length === 3 ? `${parts[1]}月${parts[2]}日` : d.date
    uni.showToast({ title: `${label}: ${d.tasks}任务, ${d.xp}XP`, icon: 'none' })
  }
}

// Radar chart rendering
function drawRadarChart() {
  nextTick(() => {
    const ctx = uni.createCanvasContext('radarCanvas')
    const radar = analyticsStore.analyticsData?.radar
    if (!radar) return

    const size = 300
    const cx = size / 2
    const cy = size / 2
    const radius = 110
    const axes = ['completion', 'efficiency', 'streak', 'quality', 'speed']
    const labels = ['完成率', '效率', '连续打卡', '质量', '速度']
    const levels = 5

    // Grid polygons
    for (let l = 1; l <= levels; l++) {
      const r = radius * l / levels
      ctx.beginPath()
      axes.forEach((_, i) => {
        const angle = Math.PI * 2 * i / 5 - Math.PI / 2
        const px = cx + r * Math.cos(angle)
        const py = cy + r * Math.sin(angle)
        if (i === 0) ctx.moveTo(px, py)
        else ctx.lineTo(px, py)
      })
      ctx.closePath()
      ctx.setStrokeStyle('#E2E6EA')
      ctx.setLineWidth(1)
      ctx.stroke()
    }

    // Axis lines
    axes.forEach((_, i) => {
      const angle = Math.PI * 2 * i / 5 - Math.PI / 2
      ctx.beginPath()
      ctx.moveTo(cx, cy)
      ctx.lineTo(cx + radius * Math.cos(angle), cy + radius * Math.sin(angle))
      ctx.setStrokeStyle('#E2E6EA')
      ctx.setLineWidth(1)
      ctx.stroke()

      // Labels
      const lx = cx + (radius + 22) * Math.cos(angle)
      const ly = cy + (radius + 22) * Math.sin(angle)
      ctx.setFontSize(12)
      ctx.setFillStyle('#636E7A')
      ctx.setTextAlign('center')
      ctx.fillText(labels[i], lx, ly + 4)
    })

    // Data polygon
    ctx.beginPath()
    axes.forEach((k, i) => {
      const val = Math.max(0, Math.min(100, radar[k] || 0))
      const r = radius * val / 100
      const angle = Math.PI * 2 * i / 5 - Math.PI / 2
      const px = cx + r * Math.cos(angle)
      const py = cy + r * Math.sin(angle)
      if (i === 0) ctx.moveTo(px, py)
      else ctx.lineTo(px, py)
    })
    ctx.closePath()
    ctx.setFillStyle('rgba(74, 158, 255, 0.15)')
    ctx.fill()
    ctx.setStrokeStyle('#4A9EFF')
    ctx.setLineWidth(2)
    ctx.stroke()

    // Vertex dots
    axes.forEach((k, i) => {
      const val = Math.max(0, Math.min(100, radar[k] || 0))
      const r = radius * val / 100
      const angle = Math.PI * 2 * i / 5 - Math.PI / 2
      ctx.beginPath()
      ctx.arc(cx + r * Math.cos(angle), cy + r * Math.sin(angle), 3, 0, Math.PI * 2)
      ctx.setFillStyle('#FFFFFF')
      ctx.fill()
      ctx.setStrokeStyle('#4A9EFF')
      ctx.setLineWidth(2)
      ctx.stroke()
    })

    ctx.draw()
  })
}

function changePeriod(p) {
  analyticsStore.fetchAnalytics(p)
}

function goBack() {
  uni.navigateBack()
}

function retryLoad() {
  analyticsStore.fetchAnalytics()
}

watch(() => analyticsStore.analyticsData, (val) => {
  if (val) {
    drawTrendChart()
    drawRadarChart()
  }
}, { deep: false })

onMounted(() => {
  if (!analyticsStore.analyticsData) {
    analyticsStore.fetchAnalytics().then(() => {
      drawTrendChart()
      drawRadarChart()
    })
  } else {
    drawTrendChart()
    drawRadarChart()
  }
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: var(--color-bg-light);
  display: flex;
  flex-direction: column;
}

.analytics-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-header-height);
  padding: 0 var(--page-padding-h);
  background: var(--color-bg-card-light);
  flex-shrink: 0;
}

.analytics-nav__back {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.analytics-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.analytics-content {
  flex: 1;
  padding: var(--space-md) var(--page-padding-h);
}

/* Period selector */
.period-selector {
  display: flex;
  width: 240px;
  height: 36px;
  margin: 0 auto var(--space-lg);
  background: var(--color-gray-100);
  border-radius: 18px;
  overflow: hidden;
}

.period-selector__item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  transition: all 200ms ease-out;
}

.period-selector__item--active {
  background: var(--color-blue-400);
}

.period-selector__label {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
}

.period-selector__item--active .period-selector__label {
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}

/* Section */
.section {
  margin-bottom: var(--space-xl);
}

.section__title {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
  display: block;
}

/* Comparison cards */
.comparison-grid {
  display: flex;
  gap: var(--space-xs);
}

.comparison-card {
  flex: 1;
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm);
  box-shadow: var(--shadow-card);
}

.comparison-card__label {
  font-size: 11px;
  color: var(--color-text-muted);
  display: block;
}

.comparison-card__value {
  font-size: 20px;
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
  margin: 4px 0;
}

.comparison-card__change {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 2px;
}

.comparison-card__change--change-up .comparison-card__arrow,
.comparison-card__change--change-up .comparison-card__pct {
  color: var(--color-green-400);
}

.comparison-card__change--change-down .comparison-card__arrow,
.comparison-card__change--change-down .comparison-card__pct {
  color: var(--color-error);
}

.comparison-card__arrow {
  font-size: var(--font-xs);
}

.comparison-card__pct {
  font-size: var(--font-xs);
  font-weight: var(--weight-semibold);
}

.comparison-card__prev {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

/* Trend chart */
.trend-chart {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm);
  box-shadow: var(--shadow-card);
}

.trend-chart__canvas {
  width: 343px;
  height: 120px;
}

/* Task type bars */
.task-type-bars {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-md);
  box-shadow: var(--shadow-card);
}

.task-type-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-xs);
}

.task-type-bar:last-child {
  margin-bottom: 0;
}

.task-type-bar__label {
  width: 40px;
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  flex-shrink: 0;
}

.task-type-bar__track {
  flex: 1;
  height: 24px;
  background: var(--color-gray-100);
  border-radius: 4px;
  overflow: hidden;
}

.task-type-bar__fill {
  height: 100%;
  border-radius: 4px;
  transition: width 400ms cubic-bezier(0.25, 0.1, 0.25, 1);
  min-width: 4px;
}

.task-type-bar__value {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
  flex-shrink: 0;
  min-width: 70px;
  text-align: right;
}

/* Radar chart */
.radar-chart {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm);
  box-shadow: var(--shadow-card);
  display: flex;
  justify-content: center;
}

.radar-chart__canvas {
  width: 300px;
  height: 300px;
}

/* Stage progress */
.stage-progress-list {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-md);
  box-shadow: var(--shadow-card);
}

.stage-progress-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.stage-progress-item:last-child {
  margin-bottom: 0;
}

.stage-progress-item__name {
  font-size: 14px;
  color: var(--color-text-primary);
  min-width: 60px;
  flex-shrink: 0;
}

.stage-progress-item__track {
  flex: 1;
  height: 18px;
  background: var(--color-gray-100);
  border-radius: 9px;
  overflow: hidden;
}

.stage-progress-item__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-green-400), var(--color-green-300));
  border-radius: 9px;
  transition: width 400ms cubic-bezier(0.25, 0.1, 0.25, 1);
  min-width: 18px;
}

.stage-progress-item__value {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

/* Summary grid */
.summary-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.summary-card {
  width: calc(50% - 4px);
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm);
  box-shadow: var(--shadow-card);
  box-sizing: border-box;
}

.summary-card__label {
  font-size: 11px;
  color: var(--color-text-muted);
  display: block;
}

.summary-card__value {
  font-size: 18px;
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
  margin-top: 2px;
}

/* Loading skeleton */
.analytics-loading {
  padding: var(--space-md) var(--page-padding-h);
}

.analytics-skeleton__section {
  margin-bottom: var(--space-xl);
}

.analytics-skeleton__title {
  height: 16px;
  width: 80px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin-bottom: var(--space-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.analytics-skeleton__content {
  height: 100px;
  background: var(--color-gray-200);
  border-radius: var(--radius-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* Error / Empty */
.analytics-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.analytics-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.analytics-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}

.analytics-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl) var(--space-xl);
  text-align: center;
}

.analytics-empty__emoji {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.analytics-empty__text {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
}

.analytics-bottom-spacer {
  height: 40px;
}
</style>
