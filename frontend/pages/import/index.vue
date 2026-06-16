<template>
  <view class="import-page">
    <!-- Nav header -->
    <view class="import-nav">
      <view class="import-nav__back" @tap="goBack">
        <text class="import-nav__back-text">← 返回</text>
      </view>
      <text class="import-nav__title">导入学习计划</text>
      <view class="import-nav__spacer" />
    </view>

    <scroll-view class="import-content" scroll-y>
      <!-- Textarea -->
      <view class="import-section">
        <text class="import-label">粘贴AI生成的学习计划 (Markdown DSL)</text>
        <textarea
          class="import-textarea"
          v-model="markdown"
          :placeholder="placeholder"
          :maxlength="50000"
          auto-height
        />
      </view>

      <!-- Preview button -->
      <view class="import-actions">
        <view
          class="import-btn import-btn--preview"
          :class="{ 'import-btn--disabled': !markdown.trim() || previewLoading }"
          @tap="handlePreview"
        >
          <text v-if="previewLoading" class="import-btn__spinner" />
          <text v-else class="import-btn__text">预览</text>
        </view>
      </view>

      <!-- Preview Error -->
      <view v-if="previewError" class="import-preview import-preview--error">
        <text class="import-preview__error-title">解析失败</text>
        <text class="import-preview__error-msg">{{ previewError }}</text>
      </view>

      <!-- Preview Loading -->
      <view v-if="previewLoading" class="import-preview">
        <view class="import-preview__skeleton">
          <view class="import-preview__skeleton-row" />
          <view class="import-preview__skeleton-row" />
          <view class="import-preview__skeleton-row" />
        </view>
      </view>

      <!-- Preview Result -->
      <view v-if="previewData && !previewLoading" class="import-preview import-preview--success">
        <text class="import-preview__title">📋 解析结果</text>
        <view class="import-preview__info">
          <text class="import-preview__name">项目：{{ previewData.title || '未命名' }}</text>
          <text class="import-preview__stat">
            {{ previewData.stage_count || 0 }} 个阶段 · {{ previewData.task_count || previewData.total_tasks || 0 }} 个任务
          </text>
        </view>
        <view v-if="previewData.stages" class="import-preview__stages">
          <view
            v-for="stage in previewData.stages"
            :key="stage.id"
            class="import-preview__stage"
          >
            <text class="import-preview__stage-title">{{ stage.title }}</text>
            <text class="import-preview__stage-count">{{ stage.task_count }} 个任务</text>
          </view>
        </view>
      </view>

      <!-- Import button -->
      <view v-if="previewData && !previewLoading" class="import-actions">
        <view
          class="import-btn import-btn--confirm"
          :class="{ 'import-btn--disabled': importLoading }"
          @tap="handleImport"
        >
          <text v-if="importLoading" class="import-btn__spinner" />
          <text v-else class="import-btn__text">确认导入</text>
        </view>
      </view>

      <view class="import-hint">
        <text class="import-hint__title">格式示例</text>
        <text class="import-hint__code"># 项目标题\n项目描述\n\n## 阶段一标题\n阶段描述\n\n### T001 theory 30 任务标题\n任务详情\n> 完成标准\n* 资源链接</text>
      </view>

      <view class="import-bottom-spacer" />
    </scroll-view>

    <!-- Import success modal -->
    <view v-if="importSuccess" class="import-modal-overlay" @tap="navigateHome">
      <view class="import-modal" @tap.stop>
        <text class="import-modal__icon">🎉</text>
        <text class="import-modal__title">导入成功!</text>
        <text class="import-modal__desc">{{ importResult }}</text>
        <view class="import-modal__btn" @tap="navigateHome">
          <text class="import-modal__btn-text">返回首页</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/utils/api'
import { useProjectStore } from '@/store/project'

const projectStore = useProjectStore()

const markdown = ref('')
const previewLoading = ref(false)
const previewData = ref(null)
const previewError = ref('')
const importLoading = ref(false)
const importSuccess = ref(false)
const importResult = ref('')

const placeholder = `# 30天 Python 入门
从零开始掌握 Python 基础。

## 第一阶段：基础语法
掌握 Python 基本语法和数据类型。

### T001 theory 20 变量与数据类型
学习 Python 的变量命名规则和基本数据类型。
> 阅读《Python编程》第2章
* https://docs.python.org/3/tutorial/

### T002 practice 30 编写第一个计算器
实现加减乘除功能。

### T003 output 50 学习笔记
整理第一阶段的知识点。
`

async function handlePreview() {
  if (!markdown.value.trim() || previewLoading.value) return

  previewLoading.value = true
  previewError.value = ''
  previewData.value = null

  try {
    const data = await api.parseProject(markdown.value)
    previewData.value = data
  } catch (err) {
    previewError.value = err.message || '解析失败，请检查格式'
    uni.showToast({ title: previewError.value, icon: 'none' })
  } finally {
    previewLoading.value = false
  }
}

async function handleImport() {
  if (!previewData.value || importLoading.value) return

  importLoading.value = true

  try {
    const data = await projectStore.importDSL(markdown.value)
    importResult.value = `已创建 "${data.title || '学习计划'}"\n${data.stage_count || 0} 个阶段 · ${data.task_count || 0} 个任务`
    importSuccess.value = true
  } catch (err) {
    uni.showToast({ title: err.message || '导入失败，请重试', icon: 'none' })
  } finally {
    importLoading.value = false
  }
}

function navigateHome() {
  importSuccess.value = false
  uni.switchTab({ url: '/pages/home/index' })
}

function goBack() {
  uni.navigateBack()
}
</script>

<style scoped>
.import-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.import-nav {
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

.import-nav__back {
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-sm);
}

.import-nav__back-text {
  font-size: var(--font-sm);
  color: var(--color-blue-400);
}

.import-nav__spacer {
  min-width: 44px;
}

.import-nav__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
}

.import-content {
  padding: var(--space-md) var(--page-padding-h);
}

.import-section {
  margin-bottom: var(--space-lg);
}

.import-label {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
  display: block;
}

.import-textarea {
  width: 100%;
  min-height: 240px;
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  font-size: var(--font-sm);
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  line-height: var(--leading-relaxed);
  box-sizing: border-box;
}

.import-actions {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.import-btn {
  flex: 1;
  height: var(--btn-height-md);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--anim-duration-fast) ease-out;
}

.import-btn--preview {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-blue-400);
}

.import-btn--preview .import-btn__text {
  color: var(--color-blue-400);
}

.import-btn--confirm {
  background: var(--color-gold-gradient);
  box-shadow: var(--shadow-button);
}

.import-btn--confirm .import-btn__text {
  color: var(--color-white);
}

.import-btn--disabled {
  opacity: 0.4;
  pointer-events: none;
}

.import-btn__text {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
}

.import-btn__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: var(--color-blue-400);
  border-radius: 50%;
  animation: spin 600ms linear infinite;
}

.import-preview {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  margin-bottom: var(--space-lg);
  box-shadow: var(--shadow-card);
}

.import-preview--error {
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.import-preview--success {
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.import-preview__title {
  font-size: var(--font-md);
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-sm);
  display: block;
}

.import-preview__info {
  margin-bottom: var(--space-sm);
}

.import-preview__name {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
  display: block;
}

.import-preview__stat {
  font-size: var(--font-xs);
  color: var(--color-text-secondary);
}

.import-preview__stages {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.import-preview__stage {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xs) 0;
  border-bottom: 1px solid var(--color-gray-100);
}

.import-preview__stage:last-child {
  border-bottom: none;
}

.import-preview__stage-title {
  font-size: var(--font-sm);
  color: var(--color-text-primary);
}

.import-preview__stage-count {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.import-preview__error-title {
  font-size: var(--font-sm);
  color: var(--color-error);
  font-weight: var(--weight-semibold);
  display: block;
  margin-bottom: var(--space-xs);
}

.import-preview__error-msg {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
}

.import-preview__skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.import-preview__skeleton-row {
  height: 14px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.import-preview__skeleton-row:nth-child(2) { width: 70%; }
.import-preview__skeleton-row:nth-child(3) { width: 50%; }

.import-hint {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  margin-top: var(--space-lg);
}

.import-hint__title {
  font-size: var(--font-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  display: block;
  margin-bottom: var(--space-sm);
}

.import-hint__code {
  font-size: var(--font-xs);
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  word-break: break-all;
  display: block;
  background: var(--color-gray-100);
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
}

.import-bottom-spacer {
  height: 80px;
}

/* Success Modal */
.import-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-bg-overlay);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-modal {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl);
  max-width: 320px;
  width: 85%;
  text-align: center;
  box-shadow: var(--shadow-modal);
  animation: modal-enter 300ms var(--anim-ease-out);
}

@keyframes modal-enter {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.import-modal__icon {
  font-size: 48px;
  display: block;
  margin-bottom: var(--space-md);
}

.import-modal__title {
  font-size: var(--font-xl);
  font-weight: var(--weight-bold);
  display: block;
  margin-bottom: var(--space-sm);
}

.import-modal__desc {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  display: block;
  margin-bottom: var(--space-lg);
  line-height: var(--leading-relaxed);
}

.import-modal__btn {
  background: var(--color-gold-gradient);
  border-radius: var(--radius-full);
  padding: var(--space-sm) var(--space-2xl);
  height: var(--btn-height-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-modal__btn-text {
  font-size: var(--font-sm);
  color: var(--color-white);
  font-weight: var(--weight-semibold);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
