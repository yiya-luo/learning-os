<template>
  <view class="empty-state">
    <view class="empty-state__illustration">
      <text class="empty-state__icon">{{ icon }}</text>
    </view>
    <text class="empty-state__title">{{ title }}</text>
    <text v-if="description" class="empty-state__desc">{{ description }}</text>
    <view v-if="actionText" class="empty-state__action" @tap="$emit('action')">
      <text class="empty-state__action-text">{{ actionText }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '' },
  actionText: { type: String, default: '' }
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-4xl) var(--space-lg);
  animation: empty-fade-in 400ms ease-out;
}

@keyframes empty-fade-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-state__illustration {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-lg);
}

.empty-state__icon {
  font-size: 64px;
}

.empty-state__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.empty-state__desc {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  text-align: center;
  line-height: var(--leading-relaxed);
}

.empty-state__action {
  margin-top: var(--space-lg);
  background: var(--color-gold-gradient);
  padding: var(--space-sm) var(--space-xl);
  border-radius: var(--radius-full);
  height: var(--btn-height-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state__action-text {
  font-size: var(--font-sm);
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}
</style>
