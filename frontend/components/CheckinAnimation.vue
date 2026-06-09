<template>
  <view v-if="visible" class="checkin-overlay" @tap="handleDismiss">
    <view class="checkin-overlay__content">
      <!-- Particle burst -->
      <view class="checkin-particles">
        <view
          v-for="p in particles"
          :key="p.id"
          class="checkin-particle"
          :style="p.style"
        />
      </view>

      <!-- XP text -->
      <text class="checkin-text checkin-text--xp" :style="xpTextStyle">
        +{{ xpGained }} XP
      </text>

      <!-- Dream value text -->
      <text class="checkin-text checkin-text--dream" :style="dreamTextStyle">
        +{{ dreamGained }} 梦想值
      </text>

      <!-- Checkmark -->
      <text v-if="showCheckmark" class="checkin-checkmark">✓</text>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  xpGained: { type: Number, default: 0 },
  dreamGained: { type: Number, default: 0 }
})

const emit = defineEmits(['complete', 'dismiss'])

const showCheckmark = ref(false)
const phase = ref('idle')
let timers = []

const particles = ref([])

const xpTextStyle = reactive({
  opacity: 0,
  transform: 'translateY(0) scale(0.6)'
})

const dreamTextStyle = reactive({
  opacity: 0,
  transform: 'translateY(0) scale(0.6)'
})

function generateParticles() {
  const items = []
  for (let i = 0; i < 10; i++) {
    const angle = (Math.PI * 2 * i) / 10 + (Math.random() - 0.5) * 0.5
    const distance = 40 + Math.random() * 80
    const dx = Math.cos(angle) * distance
    const dy = Math.sin(angle) * distance
    items.push({
      id: i,
      style: {
        '--dx': `${dx}px`,
        '--dy': `${dy}px`,
        '--delay': `${Math.random() * 100}ms`
      }
    })
  }
  particles.value = items
}

function startAnimation() {
  if (phase.value !== 'idle') return
  phase.value = 'running'
  showCheckmark.value = false
  generateParticles()

  // XP text: fade in 0→1 over 300ms
  xpTextStyle.opacity = 0
  xpTextStyle.transform = 'translateY(0) scale(0.6)'
  dreamTextStyle.opacity = 0
  dreamTextStyle.transform = 'translateY(0) scale(0.6)'

  const t1 = setTimeout(() => {
    xpTextStyle.opacity = 1
    xpTextStyle.transform = 'translateY(0) scale(1)'

    setTimeout(() => {
      xpTextStyle.transform = 'translateY(-80px) scale(1)'
    }, 200)
  }, 300)

  // Dream text: offset 50ms later
  const t2 = setTimeout(() => {
    dreamTextStyle.opacity = 1
    dreamTextStyle.transform = 'translateY(0) scale(1)'

    setTimeout(() => {
      dreamTextStyle.transform = 'translateY(-60px) scale(1)'
    }, 250)
  }, 350)

  // Fade out XP text
  const t3 = setTimeout(() => {
    xpTextStyle.opacity = 0
  }, 1500)

  // Fade out dream text
  const t4 = setTimeout(() => {
    dreamTextStyle.opacity = 0
  }, 1550)

  // Show checkmark
  const t5 = setTimeout(() => {
    showCheckmark.value = true
  }, 2100)

  // Complete animation
  const t6 = setTimeout(() => {
    phase.value = 'idle'
    showCheckmark.value = false
    emit('complete')
  }, 2300)

  timers = [t1, t2, t3, t4, t5, t6]
}

function handleDismiss() {
  timers.forEach(clearTimeout)
  timers = []
  phase.value = 'idle'
  showCheckmark.value = false
  emit('dismiss')
}

watch(() => props.visible, (val) => {
  if (val) {
    startAnimation()
  }
})

onBeforeUnmount(() => {
  timers.forEach(clearTimeout)
})
</script>

<style scoped>
.checkin-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: var(--z-animation);
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkin-overlay__content {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkin-particles {
  position: absolute;
  top: 50%;
  left: 50%;
}

.checkin-particle {
  position: absolute;
  width: var(--particle-size);
  height: var(--particle-size);
  background: var(--particle-color);
  border-radius: 50%;
  animation: particle-burst 500ms ease-out forwards;
  animation-delay: var(--delay, 0ms);
}

@keyframes particle-burst {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--dx), var(--dy)) scale(0.3);
    opacity: 0;
  }
}

.checkin-text {
  position: absolute;
  font-weight: var(--weight-bold);
  color: var(--color-gold-400);
  pointer-events: none;
  transition: opacity 300ms ease-out, transform 1500ms ease-out;
}

.checkin-text--xp {
  font-size: var(--xp-text-size);
}

.checkin-text--dream {
  font-size: var(--dream-text-size);
  font-weight: var(--weight-normal);
  margin-top: 28px;
}

.checkin-checkmark {
  font-size: 48px;
  color: var(--color-green-400);
  font-weight: var(--weight-bold);
  animation: checkmark-pop 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes checkmark-pop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  60% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
