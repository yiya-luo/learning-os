<template>
  <view class="reward-page">
    <!-- Nav header -->
    <view class="reward-nav">
      <text class="reward-nav__back" @tap="goBack">← 返回</text>
      <text class="reward-nav__title">梦想奖励</text>
      <view />
    </view>

    <!-- Loading -->
    <view v-if="isLoading" class="reward-skeleton">
      <view class="reward-skeleton__image" />
      <view class="reward-skeleton__bar" />
      <view class="reward-skeleton__stats" />
    </view>

    <!-- Error -->
    <view v-else-if="hasError" class="reward-error">
      <text class="reward-error__text">{{ error }}</text>
      <view class="reward-error__retry" @tap="loadReward">
        <text>重试</text>
      </view>
    </view>

    <!-- Empty / No reward set -->
    <view v-else-if="!rewardStore.rewardTitle" class="reward-empty">
      <EmptyState
        icon="🎁"
        title="还没有设置梦想奖励"
        description="在创建学习计划时设置你的梦想奖励"
        action-text="创建学习计划"
        @action="goImport"
      />
    </view>

    <!-- Normal -->
    <scroll-view v-else class="reward-content" scroll-y>
      <!-- Reward Image -->
      <view class="reward-image-wrapper">
        <view class="reward-image" @tap="handleImageTap">
          <image
            v-if="rewardImage"
            :src="rewardImage"
            class="reward-image__img"
            mode="aspectFill"
          />
          <template v-else>
            <view class="reward-image__placeholder">
              <text class="reward-image__placeholder-icon">🎁</text>
              <text class="reward-image__placeholder-name">{{ rewardStore.rewardTitle }}</text>
              <text class="reward-image__placeholder-hint">点击上传图片</text>
            </view>
          </template>
          <view v-if="rewardImage" class="reward-image__change-btn">
            <text>📷 更换</text>
          </view>
        </view>
      </view>

      <!-- Reward name & target -->
      <text class="reward-name">{{ rewardStore.rewardTitle }}</text>
      <text class="reward-target">¥{{ rewardStore.rewardPrice }}</text>

      <!-- Progress bar -->
      <view class="reward-progress-section">
        <ProgressBar
          :value="rewardStore.progressPercent"
          :max="100"
          size="large"
          color="gold"
          showLabel
        />
      </view>

      <!-- Stats -->
      <view class="reward-stats">
        <view class="reward-stat">
          <text class="reward-stat__value">¥{{ rewardStore.rewardPrice }}</text>
          <text class="reward-stat__label">总计</text>
        </view>
        <view class="reward-stat">
          <text class="reward-stat__value">¥{{ rewardStore.accumulatedValue }}</text>
          <text class="reward-stat__label">已积攒</text>
        </view>
        <view class="reward-stat">
          <text class="reward-stat__value">¥{{ rewardStore.remainingAmount }}</text>
          <text class="reward-stat__label">还需</text>
        </view>
      </view>

      <!-- AI Explanation -->
      <view class="reward-ai-section">
        <view class="reward-ai-card">
          <view class="reward-ai__header" @tap="aiExpanded = !aiExpanded">
            <text class="reward-ai__title">🤖 AI 分析</text>
            <text class="reward-ai__arrow">{{ aiExpanded ? '▼' : '▶' }}</text>
          </view>
          <view v-if="aiExpanded" class="reward-ai__body">
            <text class="reward-ai__analysis">
              按当前每天 +{{ dailyRate }} 的速度，你将在 {{ rewardStore.etaDate }} 达成目标。
            </text>
            <text v-if="rewardStore.remainingAmount > 0" class="reward-ai__tip">
              如果每天多做一个任务，可以提前达成目标！💪
            </text>
          </view>
        </view>
      </view>

      <!-- ETA -->
      <text v-if="rewardStore.etaDate" class="reward-eta">
        预计完成: {{ rewardStore.etaDate }}
      </text>

      <view class="reward-bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '@/store/project'
import { useRewardStore } from '@/store/reward'
import { api } from '@/utils/api'
import ProgressBar from '@/components/ProgressBar.vue'
import EmptyState from '@/components/EmptyState.vue'

const projectStore = useProjectStore()
const rewardStore = useRewardStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const aiExpanded = ref(true)
const rewardImage = ref('')

const dailyRate = computed(() => {
  if (rewardStore.estimatedDaysRemaining && rewardStore.estimatedDaysRemaining > 0) {
    return Math.ceil(rewardStore.remainingAmount / rewardStore.estimatedDaysRemaining)
  }
  return 30
})

function loadReward() {
  const pid = projectStore.currentProjectId
  if (!pid) {
    isLoading.value = false
    return
  }

  isLoading.value = true
  hasError.value = false

  rewardStore.fetchRewardProgress(pid)
    .then(() => { isLoading.value = false })
    .catch(err => {
      hasError.value = true
      error.value = err.message
      isLoading.value = false
    })
}

function handleImageTap() {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择'],
    success(res) {
      const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType,
        success(chooseRes) {
          const tempPath = chooseRes.tempFilePaths[0]
          uni.getFileSystemManager().readFile({
            filePath: tempPath,
            encoding: 'base64',
            success(readRes) {
              const base64 = `data:image/jpeg;base64,${readRes.data}`
              rewardImage.value = base64
              const pid = projectStore.currentProjectId
              if (pid) {
                api.uploadRewardImage(pid, tempPath).catch(() => {})
              }
            }
          })
        }
      })
    }
  })
}

function goBack() { uni.switchTab({ url: '/pages/home/index' }) }
function goImport() { uni.navigateTo({ url: '/pages/import/index' }) }

onMounted(() => {
  loadReward()
})
</script>

<style scoped>
.reward-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.reward-nav {
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

.reward-nav__back {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.reward-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.reward-content {
  padding: var(--space-lg) var(--page-padding-h);
}

.reward-image-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-lg);
}

.reward-image {
  width: var(--reward-image-size);
  height: var(--reward-image-size);
  border-radius: var(--radius-lg);
  background: var(--color-bg-card-light);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-card);
  overflow: hidden;
  position: relative;
}

.reward-image__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reward-image__placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1A1D22 0%, #2D3239 50%, #1E2A3A 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.reward-image__placeholder-icon {
  font-size: 48px;
  margin-bottom: var(--space-xs);
}

.reward-image__placeholder-name {
  font-size: var(--font-lg);
  font-weight: var(--weight-bold);
  color: rgba(255, 255, 255, 0.85);
  text-align: center;
}

.reward-image__placeholder-hint {
  font-size: var(--font-xs);
  color: rgba(255, 255, 255, 0.4);
  margin-top: var(--space-xs);
}

.reward-image__change-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: var(--radius-sm);
  padding: 4px 10px;
}

.reward-image__change-btn text {
  color: white;
  font-size: 12px;
}

.reward-name {
  font-size: var(--font-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  text-align: center;
  display: block;
  margin-bottom: 4px;
}

.reward-target {
  font-size: var(--font-md);
  color: var(--color-text-secondary);
  text-align: center;
  display: block;
  margin-bottom: var(--space-xl);
}

.reward-progress-section {
  margin-bottom: var(--space-xl);
  padding: 0 var(--space-md);
}

.reward-stats {
  display: flex;
  background: var(--color-bg-card-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-xl);
  box-shadow: var(--shadow-card);
}

.reward-stat {
  flex: 1;
  text-align: center;
}

.reward-stat__value {
  font-size: var(--font-lg);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.reward-stat__label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}

.reward-ai-section {
  margin-bottom: var(--space-lg);
}

.reward-ai-card {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-card);
}

.reward-ai__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reward-ai__title {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
}

.reward-ai__arrow {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.reward-ai__body {
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-gray-100);
}

.reward-ai__analysis {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

.reward-ai__tip {
  font-size: var(--font-sm);
  color: var(--color-gold-400);
  line-height: var(--leading-relaxed);
  display: block;
  margin-top: var(--space-xs);
}

.reward-eta {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  text-align: center;
  display: block;
  margin-bottom: var(--space-xl);
}

.reward-bottom-spacer {
  height: 80px;
}

/* Skeleton */
.reward-skeleton {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2xl) var(--page-padding-h);
}

.reward-skeleton__image {
  width: var(--reward-image-size);
  height: var(--reward-image-size);
  border-radius: var(--radius-lg);
  background: var(--color-gray-200);
  margin-bottom: var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.reward-skeleton__bar {
  width: 80%;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--color-gray-200);
  margin-bottom: var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.reward-skeleton__stats {
  width: 100%;
  height: 60px;
  border-radius: var(--radius-md);
  background: var(--color-gray-200);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

/* Error */
.reward-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.reward-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.reward-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}

.reward-empty {
  padding-top: var(--space-4xl);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
