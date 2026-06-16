<template>
  <view class="goal-page">
    <!-- Nav -->
    <view class="goal-nav">
      <view class="goal-nav__back" @tap="handleBack">
        <text class="goal-nav__back-text">← 返回</text>
      </view>
      <text class="goal-nav__title">设置目标</text>
      <text class="goal-nav__step">{{ step }}/4</text>
    </view>

    <!-- Progress bar -->
    <view class="goal-progress">
      <view class="goal-progress__bar" :style="{ width: (step / 4 * 100) + '%' }" />
    </view>

    <!-- Step 1: Goal -->
    <view v-if="step === 1" class="goal-step">
      <text class="goal-step__title">你想学什么？</text>
      <text class="goal-step__desc">描述你的学习目标</text>
      <input
        class="goal-input"
        v-model="goal"
        placeholder="例如：量化交易、iOS开发、日语N2"
        maxlength="50"
      />
      <text class="goal-step__subtitle">期望周期</text>
      <view class="goal-tags">
        <view
          v-for="d in durations"
          :key="d"
          class="goal-tag"
          :class="{ 'goal-tag--active': duration === d }"
          @tap="duration = d"
        >
          <text class="goal-tag__text">{{ d }}</text>
        </view>
      </view>
    </view>

    <!-- Step 2: Identity -->
    <view v-if="step === 2" class="goal-step">
      <text class="goal-step__title">你现在是什么水平？</text>
      <text class="goal-step__desc">帮助AI生成适合你的难度</text>
      <input
        class="goal-input"
        v-model="identity"
        placeholder="例如：算法工程师、大三学生、零基础"
        maxlength="50"
      />
      <text class="goal-step__subtitle">快捷选择</text>
      <view class="goal-tags">
        <view
          v-for="tag in levelTags"
          :key="tag"
          class="goal-tag"
          :class="{ 'goal-tag--active': identity === tag }"
          @tap="identity = tag"
        >
          <text class="goal-tag__text">{{ tag }}</text>
        </view>
      </view>
    </view>

<!-- PLACEHOLDER_STEPS -->

    <!-- Step 3: Reward (skippable) -->
    <view v-if="step === 3" class="goal-step">
      <text class="goal-step__title">设置梦想奖励</text>
      <text class="goal-step__desc">完成计划后给自己的奖励（可跳过）</text>
      <input
        class="goal-input"
        v-model="reward"
        placeholder="例如：AirPods Pro、一次旅行"
        maxlength="30"
      />
      <input
        class="goal-input"
        v-model="price"
        type="digit"
        placeholder="目标金额（元）"
      />
    </view>

    <!-- Step 4: Generated Prompt -->
    <view v-if="step === 4" class="goal-step">
      <text class="goal-step__title">Prompt 已生成</text>
      <text class="goal-step__desc">复制到任意AI助手（ChatGPT、Claude、Kimi等）生成学习计划</text>
      <scroll-view class="goal-prompt-box" scroll-y>
        <text class="goal-prompt__text">{{ generatedPrompt }}</text>
      </scroll-view>
    </view>

    <!-- Bottom actions -->
    <view class="goal-actions">
      <template v-if="step < 4">
        <view
          v-if="step === 3"
          class="goal-btn goal-btn--skip"
          @tap="step = 4"
        >
          <text class="goal-btn__text goal-btn__text--skip">跳过</text>
        </view>
        <view
          class="goal-btn goal-btn--primary"
          :class="{ 'goal-btn--disabled': !canNext }"
          @tap="nextStep"
        >
          <text class="goal-btn__text">下一步</text>
        </view>
      </template>
      <template v-else>
        <view class="goal-btn goal-btn--primary" @tap="copyPrompt">
          <text class="goal-btn__text">📋 复制 Prompt</text>
        </view>
        <view class="goal-btn goal-btn--secondary" @tap="goImport">
          <text class="goal-btn__text goal-btn__text--secondary">生成后去导入 →</text>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const step = ref(1)
const goal = ref('')
const duration = ref('1个月')
const identity = ref('')
const reward = ref('')
const price = ref('')

const durations = ['2周', '1个月', '3个月']
const levelTags = ['零基础', '有一定基础', '进阶']

const canNext = computed(() => {
  if (step.value === 1) return goal.value.trim().length > 0
  if (step.value === 2) return identity.value.trim().length > 0
  if (step.value === 3) return true
  return false
})

const generatedPrompt = computed(() => {
  const rewardLine = reward.value
    ? `- 梦想奖励：${reward.value}（¥${price.value || '?'}）`
    : '- 梦想奖励：无'

  const rewardRule = reward.value && price.value
    ? `\n7. 每完成一个任务积累约 ¥${Math.ceil(Number(price.value) / 25)} 的奖励进度`
    : ''

  return `你是一个学习规划专家。请根据以下信息生成一份学习计划。

【学习者信息】
- 目标：${goal.value}
- 当前水平：${identity.value}
- 期望周期：${duration.value}
${rewardLine}

【输出格式要求 - 严格遵守】
请按以下 Markdown 格式输出，不要加任何额外说明文字：

# 计划标题
一句话描述

## 阶段名称
阶段目标描述

### T001 theory 20 任务标题
任务详细描述
> 完成标准
* 参考资源链接

【格式规则】
1. 任务编号：T001, T002... 全局递增
2. 类型只能是：theory（理论学习）、practice（动手练习）、output（输出总结）
3. 数字为预估分钟数（整数）
4. 每阶段 3-8 个任务，theory:practice:output 约 2:2:1
5. 总任务数 15-40 个，根据「${duration.value}」调整
6. 阶段间有递进关系（基础→应用→综合）${rewardRule}

请直接输出计划，不要输出其他内容。`
})

function nextStep() {
  if (!canNext.value) return
  step.value++
}

function handleBack() {
  if (step.value > 1) {
    step.value--
  } else {
    uni.navigateBack()
  }
}

function copyPrompt() {
  uni.setClipboardData({
    data: generatedPrompt.value,
    success() {
      uni.showToast({ title: '已复制到剪贴板', icon: 'success' })
    }
  })
}

function goImport() {
  uni.navigateTo({ url: '/pages/import/index' })
}
</script>

<style scoped>
.goal-page {
  min-height: 100vh;
  background: var(--color-bg-light);
  display: flex;
  flex-direction: column;
}

.goal-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-header-height);
  padding: 0 var(--page-padding-h);
  background: var(--color-bg-card-light);
}

.goal-nav__back {
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-sm);
}

.goal-nav__back-text {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.goal-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.goal-nav__step {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
}

.goal-progress {
  height: 3px;
  background: var(--color-gray-100);
}

.goal-progress__bar {
  height: 100%;
  background: var(--color-primary);
  transition: width 300ms ease-out;
  border-radius: 2px;
}

.goal-step {
  flex: 1;
  padding: var(--space-xl) var(--page-padding-h);
}

.goal-step__title {
  font-size: var(--font-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
  margin-bottom: var(--space-xs);
}

.goal-step__desc {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  display: block;
  margin-bottom: var(--space-xl);
}

.goal-step__subtitle {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  font-weight: var(--weight-medium);
  display: block;
  margin-top: var(--space-lg);
  margin-bottom: var(--space-sm);
}

.goal-input {
  width: 100%;
  height: 48px;
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: 0 var(--space-md);
  font-size: var(--font-sm);
  box-sizing: border-box;
  margin-bottom: var(--space-sm);
}

.goal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.goal-tag {
  padding: var(--space-xs) var(--space-md);
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-full);
  transition: all 150ms ease-out;
}

.goal-tag--active {
  background: rgba(37, 99, 235, 0.08);
  border-color: var(--color-primary);
}

.goal-tag__text {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
}

.goal-tag--active .goal-tag__text {
  color: var(--color-primary);
  font-weight: var(--weight-medium);
}

.goal-prompt-box {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  max-height: 360px;
}

.goal-prompt__text {
  font-size: var(--font-xs);
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  word-break: break-all;
}

.goal-actions {
  padding: var(--space-lg) var(--page-padding-h);
  padding-bottom: calc(var(--space-lg) + env(safe-area-inset-bottom, 0px));
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.goal-btn {
  height: var(--btn-height-lg);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms ease-out;
}

.goal-btn:active {
  transform: scale(0.97);
}

.goal-btn--primary {
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  box-shadow: var(--shadow-button);
}

.goal-btn--secondary {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-200);
}

.goal-btn--skip {
  background: transparent;
}

.goal-btn--disabled {
  opacity: 0.4;
  pointer-events: none;
}

.goal-btn__text {
  font-size: var(--font-md);
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}

.goal-btn__text--secondary {
  color: var(--color-text-primary);
}

.goal-btn__text--skip {
  color: var(--color-text-muted);
  font-size: var(--font-sm);
}
</style>