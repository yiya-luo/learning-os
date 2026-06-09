<template>
  <view class="timeline-page">
    <!-- Nav header -->
    <view class="timeline-nav">
      <text class="timeline-nav__back" @tap="goBack">← 返回</text>
      <text class="timeline-nav__title">成长时间线</text>
      <view style="width:48px" />
    </view>

    <!-- Filter chips -->
    <scroll-view class="timeline-filters" scroll-x :show-scrollbar="false">
      <view
        v-for="opt in timelineStore.filterOptions"
        :key="opt.value"
        class="timeline-filter-chip"
        :class="{ 'timeline-filter-chip--active': timelineStore.filter === opt.value }"
        @tap="timelineStore.setFilter(opt.value)"
      >
        <text class="timeline-filter-chip__label">{{ opt.label }}</text>
        <view
          v-if="timelineStore.filter === opt.value"
          class="timeline-filter-chip__indicator"
        />
      </view>
    </scroll-view>

    <!-- Loading -->
    <view v-if="timelineStore.isLoading" class="timeline-loading">
      <view v-for="i in 3" :key="i" class="timeline-skeleton">
        <view class="timeline-skeleton__date" />
        <view class="timeline-skeleton__card" />
        <view class="timeline-skeleton__card" />
      </view>
    </view>

    <!-- Error -->
    <view v-else-if="timelineStore.error && timelineStore.events.length === 0" class="timeline-error">
      <text class="timeline-error__text">{{ timelineStore.error }}</text>
      <view class="timeline-error__retry" @tap="retryLoad">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty -->
    <view v-else-if="!timelineStore.isLoading && timelineStore.events.length === 0" class="timeline-empty">
      <text class="timeline-empty__emoji">📋</text>
      <text class="timeline-empty__title">
        {{ timelineStore.filter !== 'all' ? `还没有"${timelineStore.filterLabels[timelineStore.filter]}"的记录` : '还没有记录' }}
      </text>
      <text class="timeline-empty__desc">{{ emptyDescription }}</text>
      <text v-if="timelineStore.filter === 'all'" class="timeline-empty__link" @tap="goTasks">去打卡 →</text>
    </view>

    <!-- Timeline feed -->
    <scroll-view
      v-else
      class="timeline-content"
      scroll-y
      @scrolltolower="timelineStore.loadMore"
      :lower-threshold="100"
    >
      <view
        v-for="(group, gIdx) in groupedEvents"
        :key="group.date"
        class="timeline-group"
      >
        <!-- Date separator -->
        <view class="timeline-date-separator">
          <view class="timeline-date-separator__line" />
          <text class="timeline-date-separator__text">● {{ group.dateLabel }}</text>
          <view class="timeline-date-separator__line" />
        </view>

        <!-- Event cards -->
        <view
          v-for="event in group.items"
          :key="`${event.type}-${gIdx}`"
          class="timeline-event-card"
          :class="`timeline-event-card--${event.type}`"
          :style="{ borderLeftColor: eventColor(event) }"
        >
          <view class="timeline-event__dot" :style="{ backgroundColor: eventColor(event) }" />

          <!-- Milestone -->
          <template v-if="event.type === 'milestone'">
            <view class="timeline-event__icon">{{ event.icon || '🏆' }}</view>
            <view class="timeline-event__body">
              <text class="timeline-event__title">{{ event.title }}</text>
              <text class="timeline-event__desc">{{ event.description }}</text>
            </view>
            <view class="timeline-event__badge">
              <text class="timeline-event__badge-text">+{{ event.xp_bonus }} XP</text>
            </view>
          </template>

          <!-- Achievement -->
          <template v-else-if="event.type === 'achievement'">
            <view class="timeline-event__icon">{{ event.icon || '⭐' }}</view>
            <view class="timeline-event__body">
              <text class="timeline-event__title">{{ event.title }}</text>
              <text class="timeline-event__desc">{{ event.description }}</text>
            </view>
            <view class="timeline-event__badge">
              <text class="timeline-event__badge-text">+{{ event.xp_bonus }} XP</text>
            </view>
          </template>

          <!-- Checkin -->
          <template v-else-if="event.type === 'checkin'">
            <view class="timeline-event__icon">✓</view>
            <view class="timeline-event__body">
              <text class="timeline-event__title">{{ event.title }}</text>
              <view class="timeline-event__meta">
                <text
                  class="timeline-event__task-type"
                  :style="{ color: taskTypeColor(event.task_type) }"
                >{{ taskTypeLabel(event.task_type) }}</text>
              </view>
            </view>
            <view class="timeline-event__badge">
              <text class="timeline-event__badge-text">+{{ event.xp_earned }} XP</text>
            </view>
          </template>

          <!-- Stage -->
          <template v-else-if="event.type === 'stage'">
            <view class="timeline-event__icon">🚩</view>
            <view class="timeline-event__body">
              <text class="timeline-event__title">{{ event.title }}</text>
              <text class="timeline-event__desc">{{ event.description }}</text>
              <view class="timeline-event__stage-progress">
                <text class="timeline-event__stage-text">
                  {{ event.tasks_completed || 0 }} 个任务 · {{ event.stage_progress || 0 }}%
                </text>
              </view>
            </view>
          </template>
        </view>
      </view>

      <!-- Load more -->
      <view v-if="timelineStore.isLoadingMore" class="timeline-loading-more">
        <view v-for="i in 2" :key="i" class="timeline-skeleton__card" />
      </view>

      <text v-if="!timelineStore.hasMore && timelineStore.events.length > 0" class="timeline-no-more">
        没有更多了
      </text>

      <view class="timeline-bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTimelineStore } from '@/store/timeline'

const timelineStore = useTimelineStore()

const emptyDescription = computed(() => {
  return timelineStore.filter === 'all'
    ? '还没有记录，完成第一次打卡后会在这里看到。'
    : '试试切换到其他筛选类型看看。'
})

const groupedEvents = computed(() => {
  const groups = []
  const events = timelineStore.events

  for (const event of events) {
    const dateStr = event.date || ''
    let last = groups[groups.length - 1]
    if (!last || last.date !== dateStr) {
      last = {
        date: dateStr,
        dateLabel: timelineStore.formatDate(dateStr),
        items: []
      }
      groups.push(last)
    }
    last.items.push(event)
  }
  return groups
})

const eventColors = {
  milestone: '#FFD700',
  achievement: '#8B5CF6',
  checkin: '#4A9EFF',
  stage: '#22C55E'
}

function eventColor(event) {
  return eventColors[event.type] || eventColors.checkin
}

const taskTypeColors = {
  theory: '#4A9EFF',
  practice: '#22C55E',
  output: '#F59E0B'
}

function taskTypeColor(type) {
  return taskTypeColors[type] || '#8F99A3'
}

const taskTypeLabels = {
  theory: '理论',
  practice: '练习',
  output: '输出'
}

function taskTypeLabel(type) {
  return taskTypeLabels[type] || type
}

function goBack() {
  uni.navigateBack()
}

function goTasks() {
  uni.switchTab({ url: '/pages/task/index' })
}

function retryLoad() {
  timelineStore.fetchEvents(1, timelineStore.filter)
}

onMounted(() => {
  if (timelineStore.events.length === 0) {
    timelineStore.fetchEvents(1)
  }
})
</script>

<style scoped>
.timeline-page {
  min-height: 100vh;
  background: var(--color-bg-light);
  display: flex;
  flex-direction: column;
}

.timeline-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-header-height);
  padding: 0 var(--page-padding-h);
  background: var(--color-bg-card-light);
  flex-shrink: 0;
}

.timeline-nav__back {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.timeline-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.timeline-filters {
  display: flex;
  padding: var(--space-sm) var(--page-padding-h);
  white-space: nowrap;
  background: var(--color-bg-card-light);
  border-bottom: 1px solid var(--color-gray-100);
  flex-shrink: 0;
}

.timeline-filter-chip {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xs) var(--space-sm);
  position: relative;
  margin-right: var(--space-xs);
}

.timeline-filter-chip__label {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  transition: color 200ms ease-out;
}

.timeline-filter-chip--active .timeline-filter-chip__label {
  color: var(--color-blue-400);
  font-weight: var(--weight-semibold);
}

.timeline-filter-chip__indicator {
  width: 20px;
  height: 2px;
  background: var(--color-blue-400);
  border-radius: 1px;
  margin-top: 4px;
}

.timeline-content {
  flex: 1;
  padding: var(--space-md) var(--page-padding-h);
}

.timeline-group {
  margin-bottom: var(--space-md);
}

.timeline-date-separator {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
  padding: var(--space-xs) 0;
}

.timeline-date-separator__line {
  flex: 1;
  height: 1px;
  background: var(--color-gray-200);
}

.timeline-date-separator__text {
  font-size: 13px;
  color: var(--color-text-secondary);
  padding: 0 var(--space-sm);
  flex-shrink: 0;
}

.timeline-event-card {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-xs);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  border-left-width: 3px;
  border-left-style: solid;
  box-shadow: var(--shadow-card);
  position: relative;
  animation: timeline-card-in 300ms ease-out;
  min-height: 64px;
}

@keyframes timeline-card-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.timeline-event__dot {
  position: absolute;
  left: -6.5px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--color-bg-card-light);
}

.timeline-event__icon {
  font-size: 22px;
  min-width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timeline-event__body {
  flex: 1;
  min-width: 0;
}

.timeline-event__title {
  font-size: var(--font-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-primary);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timeline-event__desc {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
  display: block;
}

.timeline-event__meta {
  margin-top: 2px;
}

.timeline-event__task-type {
  font-size: var(--font-xs);
  font-weight: var(--weight-medium);
}

.timeline-event__stage-progress {
  margin-top: 2px;
}

.timeline-event__stage-text {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.timeline-event__badge {
  background: rgba(230, 185, 61, 0.1);
  border-radius: var(--radius-xs);
  padding: 2px var(--space-xs);
  flex-shrink: 0;
}

.timeline-event__badge-text {
  font-size: var(--font-xs);
  color: var(--color-gold-400);
  font-weight: var(--weight-semibold);
}

/* Loading */
.timeline-loading {
  padding: var(--space-md) var(--page-padding-h);
}

.timeline-skeleton {
  margin-bottom: var(--space-md);
}

.timeline-skeleton__date {
  height: 16px;
  width: 120px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin-bottom: var(--space-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.timeline-skeleton__card {
  height: 64px;
  background: var(--color-gray-200);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-xs);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.timeline-loading-more {
  padding: var(--space-sm) 0;
}

.timeline-loading-more .timeline-skeleton__card {
  margin-bottom: var(--space-xs);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* Error */
.timeline-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.timeline-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.timeline-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}

/* Empty */
.timeline-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl) var(--space-xl);
  text-align: center;
}

.timeline-empty__emoji {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.timeline-empty__title {
  font-size: var(--font-md);
  font-weight: var(--weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.timeline-empty__desc {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
}

.timeline-empty__link {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
  text-decoration: underline;
}

/* No more */
.timeline-no-more {
  text-align: center;
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  padding: var(--space-lg);
  display: block;
}

.timeline-bottom-spacer {
  height: 40px;
}
</style>
