<template>
  <view class="map-page">
    <!-- Nav header -->
    <view class="map-nav">
      <text class="map-nav__back" @tap="goBack">← 返回</text>
      <text class="map-nav__title">学习地图</text>
      <view />
    </view>

    <!-- Loading -->
    <view v-if="isLoading" class="map-skeleton">
      <view class="map-skeleton__badge" />
      <view v-for="i in 5" :key="i" class="map-skeleton__chain">
        <view class="map-skeleton__node" />
        <view v-if="i < 5" class="map-skeleton__line" />
      </view>
    </view>

    <!-- Error -->
    <view v-else-if="hasError" class="map-error">
      <text class="map-error__text">{{ error }}</text>
      <view class="map-error__retry" @tap="loadStages">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty -->
    <view v-else-if="stages.length === 0">
      <view class="map-empty">
        <text class="map-empty__icon">🗺️</text>
        <text class="map-empty__title">还没有学习计划</text>
        <text class="map-empty__desc">先去导入一份AI生成的学习计划吧</text>
        <view class="map-empty__action" @tap="goImport">
          <text>📥 导入学习计划</text>
        </view>
      </view>
    </view>

    <!-- Normal -->
    <scroll-view v-else class="map-content" scroll-y>
      <!-- Subject badge -->
      <view class="map-badge">
        <text class="map-badge__subject">{{ projectStore.currentProject?.title || '学习路径' }}</text>
        <view class="map-badge__progress-bar">
          <view
            class="map-badge__progress-fill"
            :style="{ width: overallProgress + '%' }"
          />
        </view>
        <text class="map-badge__label">{{ overallProgress }}% 总体</text>
      </view>

      <!-- Stage tree with SVG overlay -->
      <view class="map-tree">
        <view class="map-tree__svg-container">
          <svg
            class="map-tree__svg"
            :width="svgWidth"
            :height="svgHeight"
            :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
          >
            <defs>
              <linearGradient
                v-for="grad in svgGradients"
                :key="grad.id"
                :id="grad.id"
                x1="0" y1="0" x2="0" y2="1"
              >
                <stop offset="0%" :stop-color="grad.top" />
                <stop offset="100%" :stop-color="grad.bottom" />
              </linearGradient>
            </defs>
            <line
              v-for="line in dependencyLines"
              :key="line.id"
              :x1="line.x1"
              :y1="line.y1"
              :x2="line.x2"
              :y2="line.y2"
              :stroke="line.isGradient ? `url(#${line.gradientId})` : line.color"
              :stroke-width="2"
              :stroke-dasharray="line.dashed ? '6 4' : 'none'"
              :class="{ 'map-line--animated': line.dashed }"
            />
          </svg>
        </view>

        <view
          v-for="(stage, idx) in stages"
          :key="stage.id"
          class="map-stage-group"
        >
          <!-- Stage node -->
          <view
            class="map-stage-node"
            :class="[
              'map-stage-node--' + stage.status,
              { 'map-stage-node--expanded': stage._expanded }
            ]"
            @tap="toggleStage(stage)"
          >
            <!-- SVG progress ring -->
            <svg class="map-stage-ring" viewBox="0 0 48 48">
              <!-- Track -->
              <circle
                r="22" cx="24" cy="24"
                stroke="#1A1D22"
                stroke-width="3"
                fill="none"
              />
              <!-- Progress arc (only for open) -->
              <circle
                v-if="stage.status === 'open'"
                r="22" cx="24" cy="24"
                stroke="#22C55E"
                stroke-width="3"
                fill="none"
                stroke-linecap="round"
                :stroke-dasharray="138.2"
                :stroke-dashoffset="138.2 * (1 - (stage.progress || 0) / 100)"
                transform="rotate(-90, 24, 24)"
                class="map-stage-ring__progress"
              />
            </svg>

            <!-- Icon overlay -->
            <view class="map-stage-icon">
              <text v-if="stage.status === 'locked'" class="map-stage-icon__lock">🔒</text>
              <text v-else-if="stage.status === 'complete'" class="map-stage-icon__check">✓</text>
              <text v-else class="map-stage-icon__arrow">▶</text>
            </view>
          </view>

          <!-- Stage info -->
          <view class="map-stage-info">
            <text
              class="map-stage-title"
              :class="{ 'map-stage-title--locked': stage.status === 'locked' }"
            >{{ stage.title }}</text>
            <text class="map-stage-meta">
              {{ stage.completedTaskCount || stage.done_count || 0 }}/{{ stage.taskCount || stage.task_count || 0 }} 任务
            </text>
          </view>

          <!-- Expandable task list -->
          <view
            v-if="stage._expanded && stage.tasks && stage.tasks.length > 0"
            class="map-stage-tasks"
          >
            <view
              v-for="(task, tIdx) in stage.tasks"
              :key="task.id"
              class="map-task-row"
              :style="{ animationDelay: (tIdx * 50) + 'ms' }"
              @tap="openTaskDetail(stage, task)"
            >
              <text class="map-task-row__icon">{{ taskTypeIcon(task.type) }}</text>
              <text
                class="map-task-row__title"
                :class="{ 'map-task-row__title--done': task.done || task.status === 'done' }"
              >{{ task.title }}</text>
              <view class="map-task-row__badge" :class="'map-task-row__badge--' + (task.type || 'theory')">
                <text>{{ taskTypeLabel(task.type) }}</text>
              </view>
              <text class="map-task-row__xp">⚡{{ task.xp }}XP</text>
              <text class="map-task-row__est" v-if="task.estimate">⏱{{ task.estimate }}</text>
            </view>
          </view>
        </view>

        <view class="map-bottom-spacer" />
      </view>
    </scroll-view>

    <!-- Task detail bottom sheet backdrop -->
    <view
      v-if="taskDetail.visible"
      class="bottom-sheet-backdrop"
      @tap="closeTaskDetail"
    />

    <!-- Task detail bottom sheet -->
    <view
      v-if="taskDetail.visible"
      class="bottom-sheet"
      :class="{ 'bottom-sheet--visible': taskDetail.visible }"
    >
      <view class="bottom-sheet__handle" @tap="closeTaskDetail">
        <view class="bottom-sheet__handle-bar" />
      </view>

      <scroll-view class="bottom-sheet__body" scroll-y>
        <text class="bottom-sheet__title">
          {{ taskTypeEmoji(taskDetail.task.type) }} {{ taskDetail.task.title }}
        </text>

        <view class="bottom-sheet__badge" :class="'bottom-sheet__badge--' + (taskDetail.task.type || 'theory')">
          <text>{{ taskTypeLabel(taskDetail.task.type) }}</text>
        </view>

        <view class="bottom-sheet__meta">
          <text class="bottom-sheet__xp">⚡ +{{ taskDetail.task.xp }} XP</text>
          <text v-if="taskDetail.task.estimate" class="bottom-sheet__est">⏱ 预计 {{ taskDetail.task.estimate }}</text>
        </view>

        <view v-if="taskDetail.task.checkCriteria" class="bottom-sheet__section">
          <text class="bottom-sheet__section-label">📋 检查标准</text>
          <text class="bottom-sheet__section-text">{{ taskDetail.task.checkCriteria }}</text>
        </view>

        <view v-if="taskDetail.task.resourceLink" class="bottom-sheet__section">
          <text class="bottom-sheet__section-label">📎 资源链接</text>
          <text class="bottom-sheet__link">→ {{ taskDetail.task.resourceLink }}</text>
        </view>

        <view
          v-if="taskDetail.task.dependencies && taskDetail.task.dependencies.length > 0"
          class="bottom-sheet__section"
        >
          <text class="bottom-sheet__section-label">🔗 前置依赖 ({{ taskDetail.task.dependencies.length }})</text>
          <text
            v-for="(dep, dIdx) in taskDetail.task.dependencies"
            :key="dIdx"
            class="bottom-sheet__dep"
          >○ {{ findTaskTitle(dep) || dep }}</text>
        </view>

        <view class="bottom-sheet__cta" @tap="startTask">
          <text>🚀 开始任务</text>
        </view>

        <view class="bottom-sheet__safe" />
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '@/store/project'
import { api } from '@/utils/api'

const projectStore = useProjectStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const stages = ref([])
const dagData = ref(null)
const taskDetail = ref({
  visible: false,
  stage: null,
  task: null
})

const overallProgress = computed(() => projectStore.overallProgress)

/* SVG layout constants */
const SVG_WIDTH = 100
const NODE_RADIUS = 24
const NODE_SPACING = 64
const LINE_START_X = SVG_WIDTH / 2

const svgWidth = computed(() => SVG_WIDTH)
const svgHeight = computed(() => Math.max(stages.value.length * NODE_SPACING, 100))

function mapStageStatus(stage, allStages, idx) {
  const progress = stage.progress || 0
  if (progress >= 100 || stage.done_count === stage.task_count) return 'complete'
  // Check if prior stage is complete
  if (idx > 0) {
    const prevStage = allStages[idx - 1]
    const prevProgress = prevStage.progress || 0
    if (prevProgress >= 100 || prevStage.done_count === prevStage.task_count) {
      return 'open'
    }
    if (prevProgress > 0) return 'open'
    return 'locked'
  }
  return 'open' // first stage is always open
}

function getDependencyLineStyle(fromStatus, toStatus) {
  if (fromStatus === 'locked' && toStatus === 'locked') {
    return { color: '#444A54', dashed: false }
  }
  if (fromStatus === 'locked' && toStatus === 'open') {
    return { gradientId: 'locked-open', isGradient: true }
  }
  if (fromStatus === 'open' && toStatus === 'open') {
    return { color: '#4A9EFF', dashed: true }
  }
  if (fromStatus === 'open' && toStatus === 'complete') {
    return { gradientId: 'open-complete', isGradient: true }
  }
  if (fromStatus === 'complete' && toStatus === 'complete') {
    return { color: '#22C55E', dashed: false }
  }
  if (fromStatus === 'complete' && toStatus === 'open') {
    return { gradientId: 'complete-open', isGradient: true }
  }
  return { color: '#444A54', dashed: false }
}

const svgGradients = computed(() => [
  { id: 'locked-open', top: '#444A54', bottom: '#4A9EFF' },
  { id: 'open-complete', top: '#4A9EFF', bottom: '#22C55E' },
  { id: 'complete-open', top: '#22C55E', bottom: '#4A9EFF' }
])

const dependencyLines = computed(() => {
  const lines = []
  for (let i = 1; i < stages.value.length; i++) {
    const from = stages.value[i - 1]
    const to = stages.value[i]
    const y1 = i * NODE_SPACING - NODE_SPACING + NODE_RADIUS
    const y2 = i * NODE_SPACING + NODE_RADIUS
    const style = getDependencyLineStyle(from.status, to.status)

    lines.push({
      id: `line-${i}`,
      x1: LINE_START_X,
      y1,
      x2: LINE_START_X,
      y2,
      ...style
    })
  }
  return lines
})

function taskTypeIcon(type) {
  const map = { theory: '📖', practice: '✏️', output: '🎨' }
  return map[type] || '📋'
}

function taskTypeEmoji(type) {
  return taskTypeIcon(type)
}

function taskTypeLabel(type) {
  const map = { theory: '理论', practice: '练习', output: '输出' }
  return map[type] || '任务'
}

function findTaskTitle(id) {
  if (!dagData.value?.nodes) return null
  const node = dagData.value.nodes.find(n => n.id === id)
  return node?.title || null
}

async function loadStages() {
  const pid = projectStore.currentProjectId
  if (!pid) {
    isLoading.value = false
    return
  }

  isLoading.value = true
  hasError.value = false

  try {
    const [projectDetail, dagResponse] = await Promise.all([
      projectStore.fetchProjectDetail(pid),
      api.getDAG(pid).catch(() => null)
    ])

    dagData.value = dagResponse

    if (dagResponse?.stages && dagResponse?.nodes) {
      // Build stages from DAG data
      const stageMap = {}
      for (const stage of dagResponse.stages) {
        stageMap[stage.title] = {
          ...stage,
          id: stage.title,
          title: stage.title,
          taskCount: stage.task_count || 0,
          completedTaskCount: stage.done_count || 0,
          progress: Math.round((stage.progress || 0) * 100),
          tasks: []
        }
      }
      for (const node of dagResponse.nodes) {
        const st = stageMap[node.stage_title]
        if (st) {
          st.tasks.push({
            id: node.id,
            title: node.title,
            type: node.type || 'theory',
            status: node.status || 'pending',
            done: node.status === 'done',
            xp: node.xp || 0,
            estimate: '',
            dependencies: dagResponse.edges
              ?.filter(e => e.to === node.id)
              .map(e => e.from) || []
          })
        }
      }

      const arr = Object.values(stageMap)
      arr.forEach((s, idx) => {
        s.status = mapStageStatus(s, arr, idx)
        s._expanded = s.status === 'open' && idx === arr.findIndex(a => a.status === 'open')
      })
      stages.value = arr
    } else if (projectDetail?.stages) {
      stages.value = projectDetail.stages.map((s, idx, arr) => ({
        ...s,
        tasks: s.tasks || [],
        status: mapStageStatus(s, arr, idx),
        _expanded: false
      }))
    }
  } catch (err) {
    hasError.value = true
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

function toggleStage(stage) {
  if (stage.status === 'locked') {
    uni.showToast({ title: '先完成前置阶段', icon: 'none' })
    return
  }

  if (stage._expanded) {
    stage._expanded = false
  } else {
    // Collapse others and expand this one
    stages.value.forEach(s => { s._expanded = false })
    stage._expanded = true
  }
}

function openTaskDetail(stage, task) {
  taskDetail.value = { visible: true, stage, task }
}

function closeTaskDetail() {
  taskDetail.value.visible = false
}

function startTask() {
  const tid = taskDetail.value.task?.id
  if (tid) {
    uni.navigateTo({ url: `/pages/task/index?taskId=${tid}` })
  }
  closeTaskDetail()
}

function goBack() { uni.switchTab({ url: '/pages/home/index' }) }
function goImport() { uni.navigateTo({ url: '/pages/import/index' }) }

onMounted(() => {
  loadStages()
})
</script>

<style scoped>
.map-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.map-nav {
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

.map-nav__back {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.map-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.map-content {
  padding: var(--space-lg) var(--page-padding-h);
}

.map-badge {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  margin-bottom: var(--space-2xl);
  box-shadow: var(--shadow-card);
}

.map-badge__subject {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  display: block;
  margin-bottom: var(--space-sm);
}

.map-badge__progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-gray-100);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--space-xs);
}

.map-badge__progress-fill {
  height: 100%;
  background: var(--color-blue-400);
  border-radius: 4px;
  transition: width 600ms var(--anim-ease-in-out);
}

.map-badge__label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

/* Stage tree */
.map-tree {
  position: relative;
  padding-left: 0;
}

.map-tree__svg-container {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.map-line--animated {
  animation: dash-move 1s linear infinite;
}

@keyframes dash-move {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -10; }
}

/* Stage group */
.map-stage-group {
  position: relative;
  display: flex;
  align-items: flex-start;
  min-height: 64px;
  padding-left: 0;
}

/* Stage node circle */
.map-stage-node {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  margin-right: var(--space-md);
  z-index: 1;
  transition: transform 150ms var(--anim-ease-spring);
}

.map-stage-node--locked {
  opacity: 0.55;
  filter: grayscale(100%);
}

.map-stage-node--open {
  box-shadow: 0 0 12px rgba(74, 158, 255, 0.3);
}

.map-stage-node--complete {
  background: #22C55E;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.2);
}

.map-stage-node--expanded {
  transform: scale(1.05);
}

.map-stage-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 48px;
  height: 48px;
}

.map-stage-ring__progress {
  transition: stroke-dashoffset 600ms var(--anim-ease-in-out);
}

.map-stage-icon {
  position: relative;
  z-index: 2;
}

.map-stage-icon__lock {
  font-size: 16px;
}

.map-stage-icon__check {
  font-size: 18px;
  font-weight: var(--weight-bold);
  color: #FFFFFF;
}

.map-stage-icon__arrow {
  font-size: 14px;
  color: #4A9EFF;
}

/* Stage info */
.map-stage-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 4px;
}

.map-stage-title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  display: block;
}

.map-stage-title--locked {
  opacity: 0.4;
}

.map-stage-meta {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* Expandable task list */
.map-stage-tasks {
  position: absolute;
  top: 52px;
  left: 80px;
  right: 0;
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-card);
  padding: var(--space-xs);
  z-index: 2;
  animation: slide-down 300ms ease-out;
  overflow: hidden;
}

@keyframes slide-down {
  from { opacity: 0; transform: translateY(-8px); max-height: 0; }
  to { opacity: 1; transform: translateY(0); max-height: 500px; }
}

.map-task-row {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 var(--space-sm);
  background: var(--color-bg-card-light);
  border-radius: var(--radius-sm);
  border-bottom: 1px solid var(--color-gray-100);
  opacity: 0;
  animation: task-fade-in 200ms ease-out forwards;
}

.map-task-row:last-child {
  border-bottom: none;
}

@keyframes task-fade-in {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

.map-task-row__icon {
  font-size: var(--font-md);
  margin-right: var(--space-xs);
}

.map-task-row__title {
  flex: 1;
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-task-row__title--done {
  color: var(--color-text-muted);
  text-decoration: line-through;
}

.map-task-row__badge {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  margin-right: var(--space-xs);
}

.map-task-row__badge text {
  font-size: 10px;
  color: white;
}

.map-task-row__badge--theory { background: var(--color-blue-400); }
.map-task-row__badge--practice { background: var(--color-gold-400); }
.map-task-row__badge--output { background: var(--color-purple-400); }

.map-task-row__xp {
  font-size: var(--font-xs);
  color: var(--color-gold-400);
  margin-right: var(--space-xs);
}

.map-task-row__est {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

/* Empty state */
.map-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80px;
}

.map-empty__icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.map-empty__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.map-empty__desc {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-lg);
}

.map-empty__action {
  background: var(--color-gold-gradient, linear-gradient(135deg, #E6B93D 0%, #F5D56B 100%));
  border-radius: var(--radius-full);
  padding: var(--space-sm) var(--space-xl);
}

.map-empty__action text {
  font-size: var(--font-sm);
  font-weight: var(--weight-medium);
  color: var(--color-white);
}

.map-bottom-spacer {
  height: 120px;
}

/* Bottom sheet */
.bottom-sheet-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: var(--z-modal);
}

.bottom-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  max-height: 65vh;
  background: var(--color-bg-card-light);
  border-radius: 16px 16px 0 0;
  box-shadow: var(--shadow-modal);
  z-index: calc(var(--z-modal) + 1);
  animation: sheet-enter 300ms cubic-bezier(0.32, 0.72, 0, 1);
}

@keyframes sheet-enter {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.bottom-sheet__handle {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bottom-sheet__handle-bar {
  width: 32px;
  height: 4px;
  background: #C4CBD3;
  border-radius: 2px;
}

.bottom-sheet__body {
  padding: 0 var(--space-lg) var(--space-lg);
  max-height: calc(65vh - 32px);
}

.bottom-sheet__title {
  font-size: var(--font-md);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
  margin-bottom: var(--space-sm);
  line-height: var(--leading-normal);
}

.bottom-sheet__badge {
  display: inline-flex;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  margin-bottom: var(--space-sm);
}

.bottom-sheet__badge text {
  font-size: var(--font-xs);
  color: white;
}

.bottom-sheet__badge--theory { background: var(--color-blue-400); }
.bottom-sheet__badge--practice { background: var(--color-gold-400); }
.bottom-sheet__badge--output { background: var(--color-purple-400); }

.bottom-sheet__meta {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.bottom-sheet__xp {
  font-size: var(--font-sm);
  color: var(--color-gold-400);
}

.bottom-sheet__est {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
}

.bottom-sheet__section {
  padding: var(--space-sm) 0;
  border-top: 1px solid var(--color-gray-100);
}

.bottom-sheet__section-label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  display: block;
  margin-bottom: var(--space-xs);
}

.bottom-sheet__section-text {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

.bottom-sheet__link {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.bottom-sheet__dep {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  display: block;
  margin-top: 2px;
}

.bottom-sheet__cta {
  margin-top: var(--space-lg);
  height: 52px;
  background: var(--color-gold-gradient, linear-gradient(135deg, #E6B93D 0%, #F5D56B 100%));
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bottom-sheet__cta text {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-white);
}

.bottom-sheet__safe {
  height: env(safe-area-inset-bottom, 20px);
}

/* Skeleton */
.map-skeleton {
  padding: var(--space-lg) var(--page-padding-h);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-left: calc(var(--page-padding-h) + var(--space-lg));
}

.map-skeleton__badge {
  width: 200px;
  height: 60px;
  background: var(--color-gray-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xl);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.map-skeleton__chain {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-md);
}

.map-skeleton__node {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-gray-200);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.map-skeleton__line {
  width: 2px;
  height: 40px;
  background: var(--color-gray-100);
  margin-top: var(--space-md);
}

/* Error */
.map-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.map-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.map-error__retry {
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
