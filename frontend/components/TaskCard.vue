<template>
  <view
    class="task-card"
    :class="[
      `task-card--${variant}`,
      `task-card--${size}`,
      { 'task-card--done': task.status === 'done' }
    ]"
    @tap="handleTap"
    @longpress="handleLongpress"
  >
    <view class="task-card__checkbox" @tap.stop="handleToggle">
      <view class="task-card__check" :class="{ 'task-card__check--checked': task.status === 'done' }">
        <text v-if="task.status === 'done'" class="task-card__check-icon">✓</text>
      </view>
    </view>
    <view class="task-card__body">
      <text class="task-card__title" :class="{ 'task-card__title--done': task.status === 'done' }">
        {{ task.title }}
      </text>
      <view class="task-card__meta">
        <text v-if="task.type" :class="['task-card__type', `task-card__type--${task.type}`]">
          {{ typeLabel }}
        </text>
        <text v-if="task.xp" class="task-card__xp">+{{ task.xp }} XP</text>
        <text v-if="task.estimate" class="task-card__estimate">{{ task.estimate }}min</text>
      </view>
    </view>
    <slot name="actions" />
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true,
    default: () => ({ id: '', title: '', status: 'pending', xp: 0, type: '', estimate: 0 })
  },
  variant: {
    type: String,
    default: 'checkbox'
  },
  size: {
    type: String,
    default: 'normal'
  }
})

const emit = defineEmits(['toggle', 'tap', 'longpress'])

const typeLabel = computed(() => {
  const labels = { theory: '理论', practice: '练习', output: '输出' }
  return labels[props.task.type] || ''
})

function handleToggle() {
  emit('toggle', props.task.id)
}

function handleTap() {
  emit('tap', props.task.id)
}

function handleLongpress() {
  emit('longpress', props.task.id)
}
</script>

<style scoped>
.task-card {
  display: flex;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg-card-light);
  border-radius: var(--radius-md);
  gap: var(--space-sm);
  transition: background var(--anim-duration-fast) ease-out;
}

.task-card--compact {
  padding: var(--space-xs) var(--space-sm);
}

.task-card--done {
  opacity: 0.7;
}

.task-card__checkbox {
  flex-shrink: 0;
}

.task-card__check {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-gray-300);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--anim-duration-fast) ease-out;
}

.task-card__check--checked {
  background: var(--color-green-400);
  border-color: var(--color-green-400);
}

.task-card__check-icon {
  color: white;
  font-size: 12px;
  font-weight: var(--weight-bold);
}

.task-card__body {
  flex: 1;
  min-width: 0;
}

.task-card__title {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  line-height: var(--leading-tight);
  display: block;
  transition: color var(--anim-duration-fast);
}

.task-card__title--done {
  color: var(--color-text-muted);
  text-decoration: line-through;
}

.task-card__meta {
  display: flex;
  gap: var(--space-xs);
  margin-top: 4px;
  align-items: center;
}

.task-card__type {
  font-size: var(--font-xs);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  font-weight: var(--weight-medium);
}

.task-card__type--theory {
  background: rgba(74, 158, 255, 0.1);
  color: var(--color-blue-400);
}

.task-card__type--practice {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-purple-400);
}

.task-card__type--output {
  background: rgba(230, 185, 61, 0.1);
  color: var(--color-gold-500);
}

.task-card__xp {
  font-size: var(--font-xs);
  color: var(--color-gold-400);
  font-weight: var(--weight-medium);
}

.task-card__estimate {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}
</style>
