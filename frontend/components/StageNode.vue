<template>
  <view
    class="stage-node"
    :class="`stage-node--${stage.status}`"
    @tap="handleTap"
    @longpress="handleLongpress"
  >
    <view class="stage-node__circle">
      <text v-if="stage.status === 'locked'" class="stage-node__icon">🔒</text>
      <text v-else-if="stage.status === 'open'" class="stage-node__icon">▶</text>
      <text v-else class="stage-node__icon stage-node__icon--complete">✓</text>
    </view>
    <view class="stage-node__info">
      <text class="stage-node__title">{{ stage.title }}</text>
      <text v-if="stage.status === 'open' && stage.progress !== undefined" class="stage-node__progress">
        {{ Math.round(stage.progress) }}%
      </text>
    </view>
    <view v-if="!isLast" class="stage-node__line" :class="`stage-node__line--${stage.status}`" />
  </view>
</template>

<script setup>
const props = defineProps({
  stage: {
    type: Object,
    required: true,
    default: () => ({ id: '', title: '', status: 'locked', order: 1, progress: 0 })
  },
  isLast: { type: Boolean, default: false }
})

const emit = defineEmits(['tap', 'longpress'])

function handleTap() {
  emit('tap', props.stage.id)
}

function handleLongpress() {
  emit('longpress', props.stage.id)
}
</script>

<style scoped>
.stage-node {
  position: relative;
  display: flex;
  align-items: center;
  padding: var(--space-md) 0;
  z-index: 1;
}

.stage-node__circle {
  width: var(--stage-node-size);
  height: var(--stage-node-size);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-bg-card-light);
  transition: all var(--anim-duration-normal) var(--anim-ease-out);
  z-index: 1;
}

.stage-node--locked .stage-node__circle {
  border: 2px dashed var(--color-gray-600);
  background: var(--color-gray-100);
}

.stage-node--open .stage-node__circle {
  border: 2px solid var(--color-blue-400);
  background: rgba(74, 158, 255, 0.08);
}

.stage-node--complete .stage-node__circle {
  border: 2px solid var(--color-green-400);
  background: var(--color-green-400);
}

.stage-node__icon {
  font-size: 16px;
}

.stage-node__icon--complete {
  color: white;
  font-weight: var(--weight-bold);
}

.stage-node__info {
  margin-left: var(--space-sm);
  flex: 1;
}

.stage-node__title {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
}

.stage-node--locked .stage-node__title {
  color: var(--color-text-muted);
}

.stage-node__progress {
  font-size: var(--font-xs);
  color: var(--color-blue-400);
  margin-top: 2px;
}

.stage-node__line {
  position: absolute;
  left: calc(var(--stage-node-size) / 2 - 1px);
  top: calc(var(--stage-node-size) + var(--space-md));
  width: var(--stage-line-width);
  height: calc(var(--stage-line-height) + var(--space-md));
  z-index: 0;
}

.stage-node__line--locked {
  background: var(--color-gray-300);
}

.stage-node__line--open {
  background: var(--color-blue-400);
}

.stage-node__line--complete {
  background: var(--color-green-400);
}
</style>
