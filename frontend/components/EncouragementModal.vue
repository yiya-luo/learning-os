<template>
  <view v-if="visible" class="encouragement-overlay" @tap="handleBackdrop">
    <view
      class="encouragement-card"
      :style="{ borderTopColor: color, borderTopWidth: '4px', borderTopStyle: 'solid' }"
      @tap.stop
    >
      <view class="encouragement-close" @tap="handleClose">
        <text class="encouragement-close__icon">✕</text>
      </view>

      <view class="encouragement-icon" :class="{ 'encouragement-icon--sparkle': type === 'easter_egg' }">
        <text class="encouragement-icon__emoji">{{ icon }}</text>
        <view v-if="type === 'easter_egg'" class="sparkle-particles">
          <view
            v-for="i in 6"
            :key="i"
            class="sparkle-particle"
            :style="sparkleStyle(i)"
          />
        </view>
      </view>

      <text class="encouragement-message">{{ message }}</text>

      <view v-if="type === 'reward' && bonus" class="encouragement-dream-bar">
        <view class="encouragement-dream-bar__track">
          <view
            class="encouragement-dream-bar__fill"
            :style="{ width: (bonus.dream_multiplier ? (bonus.dream_multiplier - 1) * 1000 : 0) + '%' }"
          />
        </view>
      </view>

      <view v-if="type === 'easter_egg' && bonus" class="encouragement-bonus">
        <text class="encouragement-bonus__text">额外 +{{ bonus.xp || 0 }} XP</text>
        <text v-if="bonus.dream_multiplier > 1" class="encouragement-bonus__text">梦想值 x{{ bonus.dream_multiplier }} 加成</text>
      </view>

      <view
        class="encouragement-cta"
        :style="{ backgroundColor: color }"
        @tap="handleClose"
      >
        <text class="encouragement-cta__text">继续</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  type: { type: String, default: 'growth' },
  icon: { type: String, default: '🌱' },
  color: { type: String, default: '#3B82F6' },
  message: { type: String, default: '' },
  bonus: { type: Object, default: null }
})

const emit = defineEmits(['close'])

let autoDismissTimer = null

function sparkleStyle(i) {
  const angle = (Math.PI * 2 * i) / 6
  const distance = 35 + Math.random() * 25
  return {
    '--dx': `${Math.cos(angle) * distance}px`,
    '--dy': `${Math.sin(angle) * distance}px`,
    '--delay': `${i * 150}ms`,
    '--size': `${4 + Math.random() * 6}px`
  }
}

function handleClose() {
  if (autoDismissTimer) clearTimeout(autoDismissTimer)
  emit('close')
}

function handleBackdrop() {
  handleClose()
}

watch(() => props.visible, (val) => {
  if (val) {
    autoDismissTimer = setTimeout(() => {
      emit('close')
    }, 3500)
  } else if (autoDismissTimer) {
    clearTimeout(autoDismissTimer)
  }
})
</script>

<style scoped>
.encouragement-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: var(--z-animation);
  display: flex;
  align-items: center;
  justify-content: center;
}

.encouragement-card {
  width: 280px;
  min-height: 360px;
  border-radius: 16px;
  background: var(--color-bg-card-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xl);
  position: relative;
  box-shadow: var(--shadow-modal);
  animation: encourage-enter 350ms cubic-bezier(0.34, 1.56, 0.64, 1);
  gap: var(--space-md);
}

.encouragement-card--exit {
  animation: encourage-exit 250ms ease-in forwards;
}

@keyframes encourage-enter {
  0% { transform: scale(0.8); opacity: 0; }
  60% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes encourage-exit {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(0.9); opacity: 0; }
}

.encouragement-close {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-gray-100);
}

.encouragement-close__icon {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.encouragement-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-top: var(--space-sm);
}

.encouragement-icon__emoji {
  font-size: 48px;
}

.encouragement-icon--sparkle .encouragement-icon__emoji {
  animation: sparkle-rotate 2000ms ease-in-out infinite;
}

@keyframes sparkle-rotate {
  0%, 100% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(5deg) scale(1.1); }
}

.sparkle-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  pointer-events: none;
}

.sparkle-particle {
  position: absolute;
  width: var(--size, 6px);
  height: var(--size, 6px);
  background: #FFD700;
  border-radius: 50%;
  animation: sparkle-burst 800ms ease-out forwards;
  animation-delay: var(--delay, 0ms);
}

@keyframes sparkle-burst {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--dx), var(--dy)) scale(0);
    opacity: 0;
  }
}

.encouragement-message {
  font-size: var(--font-md);
  font-weight: var(--weight-medium);
  color: var(--color-text-primary);
  text-align: center;
  line-height: var(--leading-relaxed);
  max-width: 240px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.encouragement-dream-bar {
  width: 120px;
}

.encouragement-dream-bar__track {
  height: 6px;
  background: var(--color-gray-200);
  border-radius: 3px;
  overflow: hidden;
}

.encouragement-dream-bar__fill {
  height: 100%;
  background: var(--color-gold-400);
  border-radius: 3px;
  transition: width 400ms ease-out;
}

.encouragement-bonus {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.encouragement-bonus__text {
  font-size: 18px;
  font-weight: var(--weight-bold);
  color: var(--color-gold-400);
}

.encouragement-cta {
  margin-top: auto;
  width: 100%;
  height: 44px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.encouragement-cta__text {
  font-size: var(--font-sm);
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}
</style>
