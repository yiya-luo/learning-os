<template>
  <view class="level-card" :class="`level-card--${variant}`">
    <view class="level-card__badge">
      <text class="level-card__level">Lv.{{ level }}</text>
      <text class="level-card__title-text">{{ displayTitle }}</text>
    </view>
    <view class="level-card__xp-section">
      <ProgressBar
        :value="xpProgress"
        :max="100"
        size="normal"
        color="gold"
      />
      <text class="level-card__xp-text">
        距离 Lv.{{ level + 1 }} 还需 {{ xpToNext - (xpProgress * xpToNext / 100).toFixed(0) }} XP
      </text>
    </view>
    <view v-if="variant === 'full' && streak > 0" class="level-card__streak">
      <text class="level-card__streak-icon">🔥</text>
      <text class="level-card__streak-text">连续 {{ streak }} 天</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import ProgressBar from './ProgressBar.vue'

const props = defineProps({
  level: { type: Number, default: 1 },
  xp: { type: Number, default: 0 },
  xpToNext: { type: Number, default: 100 },
  title: { type: String, default: '初学者' },
  streak: { type: Number, default: 0 },
  variant: { type: String, default: 'full' }
})

const displayTitle = computed(() => props.title || '初学者')

const xpProgress = computed(() => {
  if (props.xpToNext <= 0) return 0
  const xpInLevel = props.xp % props.xpToNext
  return Math.round((xpInLevel / props.xpToNext) * 100)
})
</script>

<style scoped>
.level-card {
  background: var(--gradient-level-card);
  border-radius: var(--card-radius);
  padding: var(--space-lg);
  border: 1px solid rgba(230, 185, 61, 0.15);
}

.level-card--compact {
  padding: var(--space-md);
}

.level-card--compact .level-card__badge {
  justify-content: center;
}

.level-card__badge {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs);
  margin-bottom: var(--space-sm);
}

.level-card__level {
  font-size: var(--font-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-gold-400);
}

.level-card__title-text {
  font-size: var(--font-md);
  color: var(--color-text-inverse);
  font-weight: var(--weight-medium);
}

.level-card__xp-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.level-card__xp-text {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.level-card__streak {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: var(--space-sm);
}

.level-card__streak-icon {
  font-size: var(--font-md);
}

.level-card__streak-text {
  font-size: var(--font-sm);
  color: var(--color-gold-400);
  font-weight: var(--weight-medium);
}
</style>
