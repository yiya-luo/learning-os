<template>
  <view class="profile-page">
    <!-- Loading -->
    <view v-if="isLoading" class="profile-skeleton">
      <view class="profile-skeleton__avatar" />
      <view class="profile-skeleton__name" />
      <view class="profile-skeleton__level" />
      <view class="profile-skeleton__stats" />
      <view v-for="i in 6" :key="i" class="profile-skeleton__menu" />
    </view>

    <!-- Error -->
    <view v-else-if="hasError" class="profile-error">
      <text class="profile-error__text">{{ error }}</text>
      <view class="profile-error__retry" @tap="loadProfile">
        <text>重试</text>
      </view>
    </view>

    <!-- Normal -->
    <scroll-view v-else class="profile-content" scroll-y>
      <!-- Avatar + nickname -->
      <view class="profile-header">
        <view class="profile-avatar" @tap="handleAvatarTap">
          <text class="profile-avatar__emoji">{{ avatarEmoji }}</text>
        </view>
        <text class="profile-nickname">{{ userStore.nickname }}</text>
        <text class="profile-handle">@learner_{{ userStore.id?.slice(0, 6) || 'xxxxxx' }}</text>
      </view>

      <!-- Level card -->
      <view class="profile-level-section">
        <LevelCard
          :level="userStore.level"
          :title="userStore.computedLevelTitle"
          :xp="userStore.xp"
          :xpToNext="userStore.xpToNextLevel"
          variant="compact"
        />
      </view>

      <!-- Stats row -->
      <view class="profile-stats">
        <view class="profile-stat">
          <text class="profile-stat__value">{{ userStore.streak }}</text>
          <text class="profile-stat__label">连续打卡</text>
        </view>
        <view class="profile-stat">
          <text class="profile-stat__value">{{ projectStore.projects.length }}</text>
          <text class="profile-stat__label">进行中项目</text>
        </view>
        <view class="profile-stat">
          <text class="profile-stat__value">{{ completionRate }}%</text>
          <text class="profile-stat__label">完成率</text>
        </view>
      </view>

      <!-- Menu list -->
      <view class="profile-menu">
        <view class="profile-menu__group">
          <text class="profile-menu__group-title">学习</text>
          <view class="profile-menu__item" @tap="goTimeline">
            <text class="profile-menu__icon">📅</text>
            <text class="profile-menu__title">成长时间线</text>
            <text class="profile-menu__arrow">→</text>
          </view>
          <view class="profile-menu__item" @tap="goAnalytics">
            <text class="profile-menu__icon">📊</text>
            <text class="profile-menu__title">数据洞察</text>
            <text class="profile-menu__arrow">→</text>
          </view>
          <view class="profile-menu__item" @tap="goImport">
            <text class="profile-menu__icon">📥</text>
            <text class="profile-menu__title">导入学习计划</text>
            <text class="profile-menu__arrow">→</text>
          </view>
        </view>

        <view class="profile-menu__group">
          <text class="profile-menu__group-title">设置</text>
          <view class="profile-menu__item" @tap="handleThemeToggle">
            <text class="profile-menu__icon">🎨</text>
            <text class="profile-menu__title">深色模式</text>
            <view
              class="theme-toggle"
              :class="{ 'theme-toggle--on': isDarkMode }"
              @tap.stop="handleThemeToggle"
            >
              <view class="theme-toggle__knob" />
            </view>
          </view>
          <view class="profile-menu__item" @tap="handleReminder">
            <text class="profile-menu__icon">🔔</text>
            <text class="profile-menu__title">每日提醒</text>
            <view class="profile-menu__right">
              <text class="profile-menu__value">{{ reminderLabel }}</text>
              <text class="profile-menu__arrow">→</text>
            </view>
          </view>
        </view>

        <view class="profile-menu__group">
          <view class="profile-menu__item" @tap="handleAbout">
            <text class="profile-menu__icon">ℹ️</text>
            <text class="profile-menu__title">关于 Learning OS</text>
            <text class="profile-menu__arrow">→</text>
          </view>
          <view class="profile-menu__item profile-menu__item--danger" @tap="handleLogout">
            <text class="profile-menu__icon">🚪</text>
            <text class="profile-menu__title profile-menu__title--danger">退出登录</text>
          </view>
        </view>
      </view>

      <!-- Footer -->
      <view class="profile-footer">
        <text class="profile-footer__text">Version 1.0.0 · Build 42</text>
      </view>

      <view class="profile-bottom-spacer" />
    </scroll-view>

    <!-- Logout confirmation modal -->
    <view v-if="showLogoutModal" class="modal-overlay" @tap="showLogoutModal = false">
      <view class="modal-dialog" @tap.stop>
        <text class="modal-dialog__title">确认退出?</text>
        <text class="modal-dialog__desc">退出后需要重新登录才能使用。</text>
        <view class="modal-dialog__actions">
          <view class="modal-dialog__btn modal-dialog__btn--cancel" @tap="showLogoutModal = false">
            <text>取消</text>
          </view>
          <view class="modal-dialog__btn modal-dialog__btn--danger" @tap="confirmLogout">
            <text>退出</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Avatar picker modal -->
    <view v-if="showAvatarPicker" class="modal-overlay" @tap="showAvatarPicker = false">
      <view class="modal-dialog" @tap.stop>
        <text class="modal-dialog__title">选择头像</text>
        <view class="avatar-picker-grid">
          <view
            v-for="emoji in avatarOptions"
            :key="emoji"
            class="avatar-picker__item"
            :class="{ 'avatar-picker__item--active': avatarEmoji === emoji }"
            @tap="selectAvatar(emoji)"
          >
            <text class="avatar-picker__emoji">{{ emoji }}</text>
          </view>
        </view>
        <view class="modal-dialog__actions">
          <view class="modal-dialog__btn modal-dialog__btn--cancel" @tap="showAvatarPicker = false">
            <text>关闭</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useProjectStore } from '@/store/project'
import LevelCard from '@/components/LevelCard.vue'

const userStore = useUserStore()
const projectStore = useProjectStore()

const isLoading = ref(true)
const hasError = ref(false)
const error = ref('')
const theme = ref('light')
const isDarkMode = ref(false)
const reminderEnabled = ref(true)
const showLogoutModal = ref(false)
const showAvatarPicker = ref(false)
const avatarEmoji = ref('🦊')

const avatarOptions = ['🦊', '🐱', '🐶', '🐼', '🐨', '🦁', '🐰', '🐙']

const themeLabel = ref('light')
const reminderLabel = ref('开启')
const completionRate = ref(89)

function applyTheme() {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light')
  }
}

function loadProfile() {
  isLoading.value = true
  hasError.value = false

  try {
    const savedTheme = uni.getStorageSync('learning-os-theme')
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
      applyTheme()
    }
  } catch {}

  Promise.all([
    userStore.fetchUser(),
    userStore.fetchXP(),
    userStore.fetchStreak(),
    projectStore.fetchProjects()
  ])
    .then(() => {
      if (userStore.avatar) {
        avatarEmoji.value = userStore.avatar
      }
    })
    .catch(err => {
      hasError.value = true
      error.value = err.message
    })
    .finally(() => {
      isLoading.value = false
    })
}

function handleAvatarTap() {
  showAvatarPicker.value = true
}

function selectAvatar(emoji) {
  avatarEmoji.value = emoji
  userStore.updateProfile({ avatar: emoji })
  showAvatarPicker.value = false
}

function goImport() {
  uni.navigateTo({ url: '/pages/import/index' })
}

function goTimeline() {
  uni.navigateTo({ url: '/pages/timeline/index' })
}

function goAnalytics() {
  uni.navigateTo({ url: '/pages/analytics/index' })
}

function handleThemeToggle() {
  isDarkMode.value = !isDarkMode.value
  try {
    uni.setStorageSync('learning-os-theme', isDarkMode.value ? 'dark' : 'light')
  } catch {}
  applyTheme()
}

function handleReminder() {
  reminderEnabled.value = !reminderEnabled.value
  reminderLabel.value = reminderEnabled.value ? '开启' : '关闭'
  uni.showToast({ title: `每日提醒: ${reminderLabel.value}`, icon: 'none' })
}

function handleAbout() {
  uni.showToast({ title: 'Learning OS v1.0.0', icon: 'none' })
}

function handleLogout() {
  showLogoutModal.value = true
}

function confirmLogout() {
  showLogoutModal.value = false
  uni.showToast({ title: '已退出登录', icon: 'none' })
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--color-bg-light);
}

.profile-content {
  padding: var(--space-xl) var(--page-padding-h);
}

/* Header */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.profile-avatar {
  width: var(--avatar-size-lg);
  height: var(--avatar-size-lg);
  border-radius: 50%;
  background: var(--color-bg-card-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-sm);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.profile-avatar__emoji {
  font-size: 40px;
}

.profile-nickname {
  font-size: var(--font-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
}

.profile-handle {
  font-size: var(--font-sm);
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* Level */
.profile-level-section {
  margin-bottom: var(--space-xl);
}

/* Stats */
.profile-stats {
  display: flex;
  background: var(--color-bg-card-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-xl);
  box-shadow: var(--shadow-card);
}

.profile-stat {
  flex: 1;
  text-align: center;
}

.profile-stat__value {
  font-size: var(--font-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  display: block;
}

.profile-stat__label {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* Menu */
.profile-menu {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.profile-menu__group {
  background: var(--color-bg-card-light);
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.profile-menu__group-title {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: var(--space-sm) var(--card-padding) 0;
  display: block;
}

.profile-menu__item {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 var(--card-padding);
  transition: background var(--anim-duration-fast);
}

.profile-menu__item:active {
  background: var(--color-gray-100);
}

.profile-menu__item--danger {
  background: transparent;
}

.profile-menu__icon {
  font-size: var(--font-md);
  margin-right: var(--space-sm);
}

.profile-menu__title {
  flex: 1;
  font-size: var(--font-sm);
  color: var(--color-text-primary);
}

.profile-menu__title--danger {
  color: var(--color-error);
}

.profile-menu__right {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.profile-menu__value {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.profile-menu__arrow {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

/* Footer */
.profile-footer {
  text-align: center;
  margin-top: var(--space-xl);
}

.profile-footer__text {
  font-size: var(--font-xs);
  color: var(--color-text-muted);
}

.profile-bottom-spacer {
  height: 80px;
}

/* Modals */
.modal-overlay {
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

.modal-dialog {
  background: var(--color-bg-card-light);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  max-width: 320px;
  width: 85%;
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

.modal-dialog__title {
  font-size: var(--font-lg);
  font-weight: var(--weight-bold);
  text-align: center;
  display: block;
  margin-bottom: var(--space-xs);
}

.modal-dialog__desc {
  font-size: var(--font-sm);
  color: var(--color-text-secondary);
  text-align: center;
  display: block;
  margin-bottom: var(--space-lg);
}

.modal-dialog__actions {
  display: flex;
  gap: var(--space-sm);
}

.modal-dialog__btn {
  flex: 1;
  height: var(--btn-height-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
  font-weight: var(--weight-medium);
}

.modal-dialog__btn--cancel {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.modal-dialog__btn--danger {
  background: var(--color-error);
  color: var(--color-white);
}

/* Avatar picker */
.avatar-picker-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  justify-content: center;
  margin-bottom: var(--space-lg);
}

.avatar-picker__item {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--anim-duration-fast);
}

.avatar-picker__item--active {
  background: rgba(230, 185, 61, 0.15);
  transform: scale(1.1);
}

.avatar-picker__emoji {
  font-size: 28px;
}

/* Skeleton */
.profile-skeleton {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xl) var(--page-padding-h);
}

.profile-skeleton__avatar {
  width: var(--avatar-size-lg);
  height: var(--avatar-size-lg);
  border-radius: 50%;
  background: var(--color-gray-200);
  margin-bottom: var(--space-md);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.profile-skeleton__name {
  width: 100px;
  height: 20px;
  background: var(--color-gray-200);
  border-radius: var(--radius-xs);
  margin-bottom: var(--space-md);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.profile-skeleton__level {
  width: 90%;
  height: 80px;
  background: var(--color-gray-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.profile-skeleton__stats {
  width: 100%;
  height: 60px;
  background: var(--color-gray-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.profile-skeleton__menu {
  width: 100%;
  height: 48px;
  background: var(--color-gray-200);
  border-radius: var(--radius-sm);
  margin-bottom: 1px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

/* Error */
.profile-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4xl);
}

.profile-error__text {
  font-size: var(--font-sm);
  color: var(--color-error);
  margin-bottom: var(--space-md);
}

.profile-error__retry {
  background: var(--color-bg-card-light);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-xs) var(--space-xl);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
}

/* Theme toggle */
.theme-toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  background: var(--color-gray-600);
  position: relative;
  transition: background 200ms var(--anim-ease-out);
}

.theme-toggle--on {
  background: var(--color-green-400);
}

.theme-toggle__knob {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 3px;
  left: 2px;
  transition: transform 200ms var(--anim-ease-out);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.theme-toggle--on .theme-toggle__knob {
  transform: translateX(22px);
}

/* Profile menu item with toggle */
.profile-menu__item .theme-toggle {
  margin-left: auto;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
