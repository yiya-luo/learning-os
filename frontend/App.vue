<template>
  <view class="app" :data-theme="theme" :style="{ '--safe-top': statusBarHeight + 'px' }">
    <slot />
    <EncouragementModal
      :visible="encouragementStore.visible"
      :type="encouragementStore.encouragementData?.type"
      :icon="encouragementStore.encouragementData?.icon"
      :color="encouragementStore.encouragementData?.color"
      :message="encouragementStore.encouragementData?.message"
      :bonus="encouragementStore.encouragementData?.bonus"
      @close="encouragementStore.dismiss"
    />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onLaunch } from '@dcloudio/uni-app'
import { silentLogin } from '@/utils/auth'
import { useEncouragementStore } from '@/store/encouragement'
import EncouragementModal from '@/components/EncouragementModal.vue'

const encouragementStore = useEncouragementStore()
const theme = ref('light')
const statusBarHeight = ref(20)

onLaunch(async () => {
  await silentLogin()
})

onMounted(() => {
  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    if (menuButton) {
      statusBarHeight.value = menuButton.top + menuButton.height
    }
  } catch {
    try {
      const info = uni.getSystemInfoSync()
      statusBarHeight.value = (info.statusBarHeight || 20) + 50
    } catch {}
  }
})
</script>

<style>
@import '@/docs/design/Design_Tokens.css';

page {
  background-color: var(--color-bg-light);
  font-family: var(--font-sans);
  font-size: var(--font-md);
  color: var(--color-text-primary);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
}

.app {
  min-height: 100vh;
  padding-top: var(--safe-top, 70px);
  padding-bottom: calc(var(--tab-bar-height) + env(safe-area-inset-bottom, 0px));
}
</style>
