<template>
  <view class="progress-bar" :class="`progress-bar--${size}`">
    <view class="progress-bar__track">
      <view
        class="progress-bar__fill"
        :class="`progress-bar__fill--${color}`"
        :style="fillStyle"
      />
    </view>
    <text v-if="showLabel" class="progress-bar__label">
      {{ displayPercent }}%
    </text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  size: { type: String, default: 'normal' },
  color: { type: String, default: 'gold' },
  showLabel: { type: Boolean, default: false },
  animated: { type: Boolean, default: true }
})

const percent = computed(() => {
  if (props.max <= 0) return 0
  return Math.min((props.value / props.max) * 100, 100)
})

const displayPercent = computed(() => Math.round(percent.value))

const fillStyle = computed(() => ({
  width: `${percent.value}%`,
  transition: props.animated
    ? `width ${percent.value > 0 ? '600ms' : '0ms'} cubic-bezier(0.4, 0, 0.2, 1)`
    : 'none'
}))
</script>

<style scoped>
.progress-bar {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  width: 100%;
}

.progress-bar__track {
  flex: 1;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar--small .progress-bar__track {
  height: var(--progress-height-sm);
  border-radius: 2px;
}

.progress-bar--normal .progress-bar__track {
  height: var(--progress-height-md);
  border-radius: 4px;
}

.progress-bar--large .progress-bar__track {
  height: var(--progress-height-lg);
  border-radius: var(--radius-sm);
}

.progress-bar__fill {
  height: 100%;
  border-radius: inherit;
  width: 0;
}

.progress-bar__fill--gold {
  background: var(--color-gold-gradient);
}

.progress-bar__fill--blue {
  background: linear-gradient(135deg, var(--color-blue-400), var(--color-blue-300));
}

.progress-bar__fill--green {
  background: linear-gradient(135deg, var(--color-green-400), var(--color-green-300));
}

.progress-bar__label {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
  font-weight: var(--weight-medium);
  min-width: 36px;
  text-align: right;
}
</style>
