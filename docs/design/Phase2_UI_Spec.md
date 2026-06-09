# Learning OS — Phase 2 UI Specification

> Extends UI_Spec_v1.0 and Animation_Spec_v1.0. Same design principles: 长期主义 / 成长 / 游戏化 / 科技感 / 陪伴 / 温暖 / 极简

---

## Table of Contents
1. [Learning Map Enhancement](#1-learning-map-enhancement)
2. [Growth Heatmap Page](#2-growth-heatmap-page)
3. [Dream Value Fly-in Animation](#3-dream-value-fly-in-animation)
4. [Theme Toggle](#4-theme-toggle)
5. [Reward Image Upload](#5-reward-image-upload)
6. [Updated Data Types](#6-updated-data-types)
7. [Updated Component Tree](#7-updated-component-tree)

---

## 1. Learning Map Enhancement

### 1.1 Layout Structure (revised from v1.0)

```
┌─────────────────────────────┐
│  Status Bar                 │
├─────────────────────────────┤
│  ← 返回    学习地图          │  ← nav header, 44px sticky
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │ 操作系统 学习路径       │  │  ← SubjectBadge (unchanged)
│  │ ████████░░░░ 62% 总体  │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│                             │
│       ● Stage 5 已完成      │  ← StageNode (with progress ring)
│       │                     │     node: 48×48px circle (up from 44)
│    ╭──┴──╮                  │
│    │ ◐   │ Stage 4 进行中   │  ← expanded: shows child tasks
│    │ ┌──────────────┐      │
│    │ │ ✅ 任务 4.1   │      │  ← Task child row, slide-down
│    │ │ ○ 任务 4.2   │      │
│    │ │ ○ 任务 4.3   │      │
│    │ └──────────────┘      │
│    ╰─────╯                  │
│       │   (animated dash)   │  ← DependencyLine: dash pattern
│       │                     │
│       ○ Stage 3 未开始      │
│       │                     │
│       │   (solid grey)      │
│       │                     │
│       ○ Stage 2 未开始      │
│       │                     │
│       │                     │
│       ○ Stage 1 未开始      │
│                             │
│       底部留白 120px         │
├─────────────────────────────┤
│  [Tab Bar]                  │
└─────────────────────────────┘
```

### 1.2 StageNode Component — Revised Props

```typescript
interface StageNodeProps {
  stage: {
    id: string
    title: string
    status: 'locked' | 'open' | 'complete'
    order: number
    progress: number              // 0–100, tasks completed percentage
    taskCount: number             // total tasks in this stage
    completedTaskCount: number    // completed tasks in this stage
    tasks: StageTask[]            // child tasks for expand/collapse
  }
  isLast: boolean
  isExpanded: boolean             // controlled by parent StageTree
}

interface StageTask {
  id: string
  title: string
  done: boolean
  xp: number
  type: 'theory' | 'practice' | 'output'
  estimate: string                // e.g. "30min"
  checkCriteria?: string          // e.g. "完成习题并提交"
  resourceLink?: string           // optional URL
  dependencies: string[]          // task IDs this task depends on
}
```

### 1.3 Node States — Visual Specification

| State | Icon | Circle | Border | Background | Glow |
|-------|------|--------|--------|------------|------|
| **locked** | 🔒 (16px, `#636E7A`) | 48×48px, `radius: 50%` | `2px dashed #444A54` | `#1A1D22` (muted) | none |
| **open** | ▶ (14px, `#4A9EFF`) | 48×48px, `radius: 50%` | `2.5px solid #4A9EFF` | `rgba(74,158,255,0.08)` | `box-shadow: 0 0 12px rgba(74,158,255,0.3)` |
| **complete** | ✓ (18px bold, `#FFFFFF`) | 48×48px, `radius: 50%` | `2.5px solid #22C55E` | `#22C55E` (filled) | `box-shadow: 0 0 8px rgba(34,197,94,0.2)` |

Locked nodes also have `opacity: 0.55` on the title text and `grayscale(100%)` on the circle.

### 1.4 Progress Ring

Each StageNode circle has an SVG progress ring layered on top:

```
SVG viewBox="0 0 48 48"
  circle r="22" cx="24" cy="24"
    stroke: #1A1D22 (track)
    stroke-width: 3
    fill: none

  circle r="22" cx="24" cy="24"      (overlay, same center)
    stroke: #22C55E (complete portion)
    stroke-width: 3
    fill: none
    stroke-dasharray: 138.2           (circumference = 2*π*22)
    stroke-dashoffset: 138.2 * (1 - progress/100)
    stroke-linecap: round
    transform: rotate(-90, 24, 24)    (start from top)
    transition: stroke-dashoffset 600ms var(--anim-ease-in-out)
```

Only visible when `status === 'open'`. Hidden (opacity 0) when `locked` or `complete`.

### 1.5 Dependency Lines

| Connection | Visual | CSS |
|------------|--------|-----|
| locked → locked | solid `#444A54`, 2px | `border-left` or SVG line |
| locked → open | gradient `#444A54`→`#4A9EFF` top→bottom | SVG `<linearGradient>` |
| open → open | dashed `#4A9EFF`, 2px, animated | `stroke-dasharray: 6 4` with `animation: dash-move 1s linear infinite` |
| open → complete | gradient `#4A9EFF`→`#22C55E` | SVG `<linearGradient>` |
| complete → complete | solid `#22C55E`, 2px | `border-left` |

Dependency lines are rendered as SVG `<line>` elements within a dedicated SVG overlay, NOT as CSS borders. This enables gradients and dash animations that CSS borders cannot do cleanly.

**Animated dash keyframes:**
```css
@keyframes dash-move {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -10; }
}
```

Line height: 40px between nodes (increased from 32px to accommodate the larger node size).

### 1.6 Expand/Collapse Behavior

**Trigger**: Tap a StageNode circle or title area.

**Expand animation** (300ms `ease-out`):
```
1. Child task container slides down: max-height 0 → 500px
2. Child tasks fade in with staggered delay (each task +50ms)
3. Stage circle scales 1 → 1.05 → 1 (150ms spring bounce)
```

**Collapse animation** (200ms `ease-in`):
```
1. Child tasks fade out immediately
2. Container slides up: max-height 500px → 0
```

**Child task row layout:**
```
┌─────────────────────────────────────┐
│ ○  任务名称     📖理论  ⚡30XP  ⏱30min │  ← 56px height
├─────────────────────────────────────┤
│ ✅ 任务名称     ✏️练习  ⚡50XP  ⏱45min │  ← strikethrough + muted
└─────────────────────────────────────┘
```

Each task row: 56px height, `padding: 0 var(--space-md)`, left-aligned with the Stage circle + 32px indent. Background: `var(--color-bg-card-light)`, rounded 8px, subtle bottom border `1px solid var(--color-gray-100)`.

### 1.7 Task Detail Bottom Sheet

**Trigger**: Tap a child task row.

**Visual**: A bottom sheet slides up from the bottom of the screen.

```
┌─────────────────────────────────────┐
│  ━━━━━━━━━━━━  (drag handle, 32px) │
├─────────────────────────────────────┤
│                                     │
│  📖 阅读《现代操作系统》第3.1节       │  ← title: 16px bold
│                                     │
│  ┌──────┐                           │
│  │ 理论  │  type badge              │  ← 12px tag, pill shape
│  └──────┘                           │
│                                     │
│  ⚡ +50 XP                          │  ← XP: 14px, gold
│  ⏱ 预计 30 分钟                     │  ← estimate: 14px, secondary
│                                     │
│  ────────────────────────────────   │
│                                     │
│  📋 检查标准                         │  ← section label: 12px, muted
│  完成第3.1节的所有阅读并理解核心     │
│  概念，能用自己的话复述。             │
│                                     │
│  ────────────────────────────────   │
│                                     │
│  📎 资源链接                         │
│  → 电子版教材第3章                   │
│                                     │
│  ────────────────────────────────   │
│                                     │
│  🔗 前置依赖 (1)                     │
│  ○ 完成第2章习题                      │
│                                     │
│  ────────────────────────────────   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      🚀 开始任务             │   │  ← CTA button, 52px height
│  └─────────────────────────────┘   │     gold gradient pill
│                                     │
│  ── Safe Area ──                    │
└─────────────────────────────────────┘
```

**Bottom sheet specs:**
- Max height: 65vh
- Border-radius: `16px 16px 0 0` (top corners)
- Background: `var(--color-bg-card-light)`
- Shadow: `var(--shadow-modal)`
- Entrance: slide-up 300ms `cubic-bezier(0.32, 0.72, 0, 1)` (iOS-style)
- Exit: slide-down 250ms `ease-in`
- Backdrop: `rgba(0,0,0,0.4)`, tap to dismiss
- Drag handle: 32px wide, 4px tall, `#C4CBD3`, radius 2px, centered

### 1.8 Empty State (revised)

```
┌─────────────────────────────────────┐
│                                     │
│            🗺️ (48px)               │
│                                     │
│      还没有学习计划                  │  ← 16px bold, secondary
│      先去导入一份AI生成的学习计划吧   │  ← 14px, muted
│                                     │
│  ┌─────────────────────────────┐   │
│  │      📥 导入学习计划          │   │  ← gold pill button, 44px
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

The empty state button navigates to `/pages/import/index`.

---

## 2. Growth Heatmap Page (成长热力图)

### 2.1 Route & Tab Placement

- Route: `/pages/heatmap/index`
- Tab bar position: **4th tab** (between 今日任务 and 梦想奖励)
- Tab config:
  ```
  Tab order: 首页 | 学习地图 | 今日任务 | 成长 | 梦想奖励 | 我的
             home    map       task     heatmap  reward    profile
  ```
- Icon: 📈 (outlined) / 📊 (filled/active context)
- Label: "成长"

### 2.2 Page Layout

```
┌─────────────────────────────────────┐
│  Status Bar                         │
├─────────────────────────────────────┤
│                                     │
│          2026 年                     │  ← year: 20px bold, centered
│        共 187 次打卡                  │  ← total checkins: 14px, secondary
│                                     │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 一                          │  │  ← weekday labels (Mon–Sun)
│   │ 二                          │  │     12px, muted, left column
│   │ 三                          │  │     row height: 14px
│   │ 四                          │  │     cell size: 12×12px
│   │ 五                          │  │     cell gap: 2px
│   │ 六                          │  │
│   │ 日                          │  │
│   │                             │  │
│   │ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │  ← heatmap grid
│   │ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │     7 rows × 52 cols
│   │ ░░░░░░▒▒▒░░░░░░░░░░░░░░░░░ │  │
│   │ ░░░░░▒▓▓░░░░░░░░░░░░░░░░░░ │  │
│   │ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │
│   │ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │
│   │ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  │
│   └─────────────────────────────┘  │
│   ┌─────────────────────────────┐  │
│   │ 1月  2月  3月  ...  12月    │  │  ← month labels, 10px, muted
│   └─────────────────────────────┘  │
│                                     │
│  ────────────────────────────────   │
│                                     │
│  ┌─────────────── 统计 ───────────┐ │
│  │                                │ │
│  │  活跃天数       最长连续         │ │
│  │    187          42 天          │ │  ← stats row
│  │                                │ │
│  │  总 XP          日均 XP         │ │
│  │   12,850        68.7           │ │
│  │                                │ │
│  │  色阶说明:                      │ │
│  │  ░ 无  ▒ 1次  ▓ 2次  ▓ 3次  █ 4+│ │  ← legend
│  │                                │ │
│  └────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│  [Tab Bar]                          │
└─────────────────────────────────────┘
```

### 2.3 Heatmap Grid Specs

**Cell dimensions:**
- Size: 12×12px
- Border-radius: 2px
- Gap between cells: 2px
- Row height: 14px (12px cell + 2px gap)
- Total grid width: 52 columns × 14px = 728px (horizontally scrollable)

**Horizontal scroll**: The grid is wider than a 375px screen. The month labels and grid scroll together inside a `<scroll-view scroll-x>`. The weekday labels (left column) are sticky.

**Color scale:**
| Checkins | Color | CSS Variable |
|----------|-------|-------------|
| 0 | `#1A1D22` | `--heatmap-0` |
| 1 | `#0e4429` | `--heatmap-1` |
| 2 | `#006d32` | `--heatmap-2` |
| 3 | `#26a641` | `--heatmap-3` |
| 4+ | `#39d353` | `--heatmap-4` |

**CSS for cells:**
```css
.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  transition: transform 150ms var(--anim-ease-out);
}

.heatmap-cell:active {
  transform: scale(1.5);
}

.heatmap-cell--0 { background: var(--heatmap-0); }
.heatmap-cell--1 { background: var(--heatmap-1); }
.heatmap-cell--2 { background: var(--heatmap-2); }
.heatmap-cell--3 { background: var(--heatmap-3); }
.heatmap-cell--4 { background: var(--heatmap-4); }
```

**Grid data structure:**
```typescript
interface HeatmapData {
  year: number
  totalCheckins: number
  days: Record<string, DayStats>  // key: "2026-06-08"
}

interface DayStats {
  date: string
  checkins: number           // 0–4+
  tasksCompleted: number
  xpEarned: number
}
```

### 2.4 Day Cell Tooltip

**Trigger**: Tap a day cell.

**Visual**: A small popover appears above the tapped cell.

```
     ┌──────────────────┐
     │  6月8日 周一       │  ← date: 12px bold
     │  完成任务: 3       │  ← 12px
     │  获得 XP: 150      │  ← 12px
     └────┬─────────────┘
          ▼
       [cell]
```

**Tooltip specs:**
- Background: `rgba(0,0,0,0.85)`
- Text: white, 12px
- Padding: 8px 12px
- Border-radius: 8px
- Max width: 160px
- Auto-position: above the cell, or below if near top edge
- Entrance: opacity 0→1, translateY(-4px)→0, 150ms `ease-out`
- Dismiss: tap anywhere else, or auto-dismiss after 3s
- Z-index: `var(--z-tooltip)`

### 2.5 Stats Section

```
┌────────────────────────────────────┐
│  活跃天数      最长连续             │
│  ┌──────┐    ┌──────┐             │
│  │ 187  │    │  42  │             │  ← stat card: 80px wide
│  │ 天   │    │  天  │             │     bg: var(--color-bg-card-light)
│  └──────┘    └──────┘             │     radius: 8px
│                                    │     padding: 12px
│  总 XP         日均 XP             │
│  ┌──────┐    ┌──────┐             │
│  │12,850│    │ 68.7 │             │
│  │ XP   │    │ XP   │             │
│  └──────┘    └──────┘             │
└────────────────────────────────────┘
```

Stat cards in a 2×2 grid, 8px gap.

### 2.6 Legend

```
色阶: ░  ▒  ▓  ▓  █
      0  1次 2次 3次 4+
```

Shown as a row of 5 colored squares with labels below. Each square: 12×12px, same colors as heatmap.

### 2.7 States

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton: 7 rows of 52 grey pulsing squares + stats area skeleton |
| **Empty** | "还没有打卡记录，完成今日任务来点亮第一格吧!" message centered, with link to tasks |
| **Error** | Inline error + retry button |
| **Normal** | Full heatmap rendered; current day cell has a subtle ring highlight (1px `#4A9EFF` border) |

---

## 3. Dream Value Fly-in Animation

### 3.1 Overview

- **Trigger**: After successful check-in API call completes (on task page)
- **Location**: Home page (and optionally task page)
- **Duration**: 1500ms total
- **Overrides**: Replaces the standalone XP/dream text flight in Phase 1's CheckinAnimation for the home page context

### 3.2 Animation Timeline

```
0ms          300ms              900ms          1500ms
├─────────────┼──────────────────┼──────────────┤
│  Fade in    │  Fly toward      │  Nearing     │  Fade out
│  Scale up   │  dream progress  │  destination │  Progress
│             │  area (top-right)│              │  bar fills
└─────────────┴──────────────────┴──────────────┘
```

### 3.3 "+XP" Text Animation

```
Start position: center-bottom of screen (checkin button area)
End position:   top-right area (dream mini-progress card on home page)

Keyframes:
  @keyframes fly-xp {
    0% {
      opacity: 0;
      transform: translate(0, 0) scale(0.5);
    }
    15% {
      opacity: 1;
      transform: translate(0, -10px) scale(1);
    }
    70% {
      opacity: 0.8;
      transform: translate(
        calc(var(--fly-target-x, 120px)),
        calc(var(--fly-target-y, -300px))
      ) scale(0.7);
    }
    100% {
      opacity: 0;
      transform: translate(
        calc(var(--fly-target-x, 140px)),
        calc(var(--fly-target-y, -340px))
      ) scale(0.4);
    }
  }

  animation: fly-xp 1500ms cubic-bezier(0.4, 0, 0.6, 1) forwards;
```

**Text style:**
- Content: `+{xp} XP`
- Font: 20px → 12px (shrinks during flight)
- Color: `#3B82F6` (blue)
- Weight: `bold`
- Text shadow: `0 1px 4px rgba(59,130,246,0.4)`

### 3.4 "+梦想值" Text Animation

```
Same keyframe structure, but:
- Delayed by 100ms (stagger effect)
- Content: "+{dream_value} 梦想值"
- Color: #FFD700 (gold)
- Text shadow: 0 1px 4px rgba(255,215,0,0.4)
- End position: 20px below the XP text end position
```

### 3.5 Dream Progress Bar Fill

```
After the fly-in texts reach their destination (at ~900ms):
  → dream progress bar animates from old% to new%
  → duration: 400ms ease-out
  → color: gold gradient

CSS:
  .dream-bar {
    transition: width 400ms cubic-bezier(0.25, 0.1, 0.25, 1);
  }

  .dream-bar--filling {
    box-shadow: 0 0 8px rgba(230, 185, 61, 0.6);  /* gold glow at fill tip */
    transition: box-shadow 300ms ease-out;
  }
```

**Overall sequence:**
1. Texts appear at checkin origin
2. Both fly toward dream area (top-right), XP leads, dream value follows
3. At ~900ms, texts near destination, opacity starts decreasing
4. At ~1100ms, dream progress bar begins filling (400ms)
5. At ~1500ms, everything complete, texts gone, bar at new value

### 3.6 Implementation Notes

- The fly-in animation uses CSS custom properties (`--fly-target-x`, `--fly-target-y`) set by JavaScript measuring the actual positions of the source button and target dream card
- On the home page, the target is the DreamMiniProgress component's progress bar
- On the task page, if the dream card is not visible, the texts fly toward a ghost target position (top-right corner of the screen)
- Particles from Phase 1's CheckinAnimation are NOT included in this home-page fly-in (the checkin happened on the task page)
- Haptic feedback: `light` pulse at 0ms and another at 1100ms (when bar starts filling)

### 3.7 CSS Custom Properties for Fly-in

Set dynamically via JavaScript before animation starts:
```css
.fly-container {
  --fly-target-x: 0px;      /* horizontal distance to target */
  --fly-target-y: 0px;      /* vertical distance to target */
  --fly-target-x-dream: 0px;
  --fly-target-y-dream: 0px;
}
```

---

## 4. Theme Toggle (主题切换)

### 4.1 Location

On the Profile page (`/pages/profile/index`), replace the current "主题设置" menu item behavior.

### 4.2 Toggle Design

```
┌─────────────────────────────────────┐
│  🎨  深色模式                        │
│       ┌──────────┐                  │
│       │ ●────────│───  toggle ON    │  ← custom toggle switch
│       └──────────┘                  │
└─────────────────────────────────────┘
```

**Toggle switch specs:**
- Width: 48px, Height: 28px
- Track: `border-radius: 14px` (fully rounded)
- Knob: 22×22px circle, white
- ON state: track `#22C55E` (green), knob right (translateX: 22px)
- OFF state: track `#444A54` (dark grey), knob left (translateX: 2px)
- Transition: `transform 200ms var(--anim-ease-out)`, `background 200ms var(--anim-ease-out)`

**CSS:**
```css
.theme-toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  background: var(--color-gray-600);
  position: relative;
  transition: background 200ms var(--anim-ease-out);
  cursor: pointer;
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
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.theme-toggle--on .theme-toggle__knob {
  transform: translateX(22px);
}
```

### 4.3 Theme Application

**Storage**: `localStorage.setItem('learning-os-theme', 'dark' | 'light')`

**Application**: Set `data-theme` attribute on `<html>` element:
```javascript
document.documentElement.setAttribute('data-theme', theme)
```

**Transition**: All themed properties transition over 300ms:
```css
*, *::before, *::after {
  transition:
    background-color 300ms ease,
    color 200ms ease,
    border-color 300ms ease,
    box-shadow 300ms ease;
}
```

This must be scoped to not affect animations — exclude `transform`, `opacity` from the global transition.

**Dark theme colors (extending Design_Tokens.css):**
```css
[data-theme="dark"] {
  --color-bg-dark:        #0D1117;
  --color-bg-card-dark:   #161B22;
  --color-bg-light:       #0D1117;
  --color-bg-card-light:  #161B22;
  --color-text-primary:   #F0F3F6;
  --color-text-secondary: #8B949E;
  --color-text-muted:     #6E7681;
  --color-gray-100:       #21262D;
  --color-gray-200:       #30363D;

  --heatmap-0:            #161B22;
  --heatmap-1:            #0e4429;
  --heatmap-2:            #006d32;
  --heatmap-3:            #26a641;
  --heatmap-4:            #39d353;

  --shadow-card:          0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
}
```

### 4.4 Profile Menu Integration

Replace the current `handleThemeToggle` function:

```typescript
const isDarkMode = ref(
  localStorage.getItem('learning-os-theme') === 'dark'
)

function handleThemeToggle() {
  isDarkMode.value = !isDarkMode.value
  const theme = isDarkMode.value ? 'dark' : 'light'
  localStorage.setItem('learning-os-theme', theme)
  document.documentElement.setAttribute('data-theme', theme)
}
```

The menu item shows a toggle switch instead of text + arrow:
```
🎨 深色模式    [Toggle Switch]
```

---

## 5. Reward Image Upload

### 5.1 Layout Revision

Replace the current placeholder on the reward page:

```
┌─────────────────────────────────────┐
│                                     │
│    ┌─────────────────────────┐     │
│    │                         │     │
│    │    [Reward Image]       │     │  ← 200×200px, radius 16px
│    │     or gradient         │     │
│    │    placeholder          │     │
│    │                         │     │
│    │    ┌──────────┐        │     │  ← camera icon overlay
│    │    │ 📷 更换  │        │     │     only on image state
│    │    └──────────┘        │     │     32px height, semi-transparent
│    └─────────────────────────┘     │
│        Switch OLED                  │
│        ¥2,099                       │
│                                     │
└─────────────────────────────────────┘
```

### 5.2 States

**No image (placeholder state):**
```
┌─────────────────────────────┐
│                             │
│       ╱╲                    │
│      ╱  ╲    🎁            │  ← gradient background + emoji
│     ╱    ╲                  │
│    ╱ Switch╲                │
│   ╱  OLED   ╲               │  ← reward name overlaid on gradient
│  ╱           ╲              │
│ ╱  点击上传图片 ╲             │  ← hint text, 12px, muted
│ ╲             ╱              │
│  ╲           ╱              │
│                             │
└─────────────────────────────┘
```

**Gradient placeholder specs:**
- Background: `linear-gradient(135deg, #1A1D22 0%, #2D3239 50%, #1E2A3A 100%)`
- Reward name: centered, 20px bold, white with 0.85 opacity
- Emoji: centered above name, 48px
- Hint text: below name, "点击上传图片", 12px, `rgba(255,255,255,0.4)`

**With image (normal state):**
- Image fills 200×200px container, `object-fit: cover`, `border-radius: 16px`
- Small "📷 更换" button overlay at bottom-right
- Stored as base64 data URL in the project/dream data

### 5.3 Upload Flow

```
Tap placeholder / "更换" button
  → UniApp chooseImage action sheet:
      ┌──────────────────────────┐
      │  选择图片来源              │
      │                          │
      │  📷  拍照                 │
      │  🖼️  从相册选择           │
      │                          │
      │  取消                     │
      └──────────────────────────┘
```

**Implementation:**
```typescript
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
          // Convert to base64
          uni.getFileSystemManager().readFile({
            filePath: tempPath,
            encoding: 'base64',
            success(readRes) {
              const base64 = `data:image/jpeg;base64,${readRes.data}`
              rewardImage.value = base64
              // Save to store
              rewardStore.updateRewardImage(base64)
            }
          })
        }
      })
    }
  })
}
```

**Image constraints:**
- Max file size: 2MB
- Compressed to max 800px width/height
- Format: JPEG (compressed) stored as base64 data URL
- On upload success: placeholder cross-fades to image (300ms)

### 5.4 RewardImage Component — Revised Props

```typescript
interface RewardImageProps {
  src: string                    // base64 data URL or empty string
  name: string                   // reward name for placeholder overlay
  size?: number                  // default: 200
  editable?: boolean             // default: true, shows upload UI
}

// Emits
interface RewardImageEmits {
  (e: 'update', base64: string): void
  (e: 'tap'): void               // full-screen preview when image exists
}
```

**States:**
| State | Visual |
|-------|--------|
| empty | Gradient placeholder with name + "点击上传" hint |
| uploading | Placeholder with spinner overlay |
| loaded | Image displayed with "更换" button overlay |
| error | Placeholder with ⚠️ icon + "上传失败，点击重试" |

---

## 6. Updated Data Types

### 6.1 New Types for Phase 2

```typescript
// Stage — extended with task children
interface StageTask {
  id: string
  title: string
  done: boolean
  xp: number
  type: 'theory' | 'practice' | 'output'
  estimate: string
  checkCriteria?: string
  resourceLink?: string
  dependencies: string[]
}

// Updated Stage includes tasks
interface Stage {
  id: string
  title: string
  status: 'locked' | 'open' | 'complete'
  order: number
  progress: number
  taskCount: number
  completedTaskCount: number
  description: string
  tasks: StageTask[]
}

// Heatmap
interface HeatmapData {
  year: number
  totalCheckins: number
  days: Record<string, DayStats>
}

interface DayStats {
  date: string             // "2026-06-08"
  checkins: number
  tasksCompleted: number
  xpEarned: number
}

// Updated Dream (adds image field)
interface Dream {
  id: string
  name: string
  icon: string
  image: string            // base64 data URL, empty string if no image
  target: number
  earned: number
  unit: string
  eta: string
  aiAnalysis: string
  aiSuggestions: string[]
}
```

### 6.2 Updated UI Store

```typescript
interface UIState {
  theme: 'light' | 'dark'       // removed 'system' — simplified to binary toggle
  encouragement: string
  encouragementLoading: boolean
}
```

---

## 7. Updated Component Tree

```
App.vue
├── pages/
│   ├── home/index.vue
│   │   ├── LevelCard.vue
│   │   ├── MainQuestProgress.vue
│   │   │   └── ProgressBar.vue
│   │   ├── TodayTaskPreview.vue
│   │   │   └── TaskCard.vue (×3)
│   │   ├── DreamMiniProgress.vue
│   │   │   └── ProgressBar.vue
│   │   ├── EncouragementCard.vue
│   │   └── FlyInAnimation.vue          ← NEW: overlay for dream value fly-in
│   │
│   ├── map/index.vue
│   │   └── StageTree.vue
│   │       ├── StageNode.vue (×N)       ← UPDATED: expand/collapse, progress ring
│   │       │   └── StageTaskRow.vue (×M) ← NEW: child task rows
│   │       ├── DependencyLineSVG.vue     ← NEW: SVG dependency lines
│   │       └── TaskDetailSheet.vue       ← NEW: bottom sheet
│   │
│   ├── task/index.vue                   (unchanged from Phase 1)
│   │   ├── TaskDetailCard.vue
│   │   │   └── TaskCard.vue
│   │   ├── RewardPreview.vue
│   │   ├── CheckinButton.vue
│   │   └── CheckinAnimation.vue
│   │
│   ├── heatmap/index.vue                ← NEW PAGE
│   │   ├── HeatmapGrid.vue
│   │   ├── DayTooltip.vue
│   │   └── HeatmapStats.vue
│   │
│   ├── reward/index.vue
│   │   ├── RewardImage.vue              ← UPDATED: upload + base64 support
│   │   ├── ProgressBar.vue
│   │   ├── RewardStats.vue
│   │   └── AIExplanation.vue
│   │
│   ├── profile/index.vue
│   │   ├── Avatar.vue
│   │   ├── LevelCard.vue
│   │   ├── StatsRow.vue
│   │   ├── MenuItem.vue (×8)
│   │   └── ThemeToggle.vue              ← NEW: standalone toggle component
│   │
│   └── import/index.vue                 (unchanged)
│       ├── MarkdownInput.vue
│       └── ParsePreview.vue
│
└── components/ (shared)
    ├── TaskCard.vue
    ├── ProgressBar.vue
    ├── CheckinAnimation.vue
    ├── StageNode.vue                    ← UPDATED
    ├── EmptyState.vue
    ├── BottomSheet.vue                  ← NEW: reusable bottom sheet wrapper
    └── FlyInAnimation.vue               ← NEW: reusable fly-in overlay
```

---

## 8. New CSS Design Tokens (add to Design_Tokens.css)

```css
:root {
  /* Heatmap */
  --heatmap-0:            #1A1D22;
  --heatmap-1:            #0e4429;
  --heatmap-2:            #006d32;
  --heatmap-3:            #26a641;
  --heatmap-4:            #39d353;

  --heatmap-cell-size:    12px;
  --heatmap-cell-gap:     2px;
  --heatmap-cell-radius:  2px;

  /* Theme Toggle */
  --toggle-width:         48px;
  --toggle-height:        28px;
  --toggle-knob-size:     22px;

  /* Bottom Sheet */
  --sheet-handle-width:   32px;
  --sheet-handle-height:   4px;
  --sheet-max-height:     65vh;
  --sheet-radius:         16px;

  /* Fly-in Animation */
  --fly-duration:         1500ms;
  --fly-xp-color:         #3B82F6;
  --fly-dream-color:      #FFD700;

  /* Stage Node (updated) */
  --stage-node-size:      48px;          /* up from 44px */
  --stage-line-height:    40px;          /* up from 32px */
  --stage-node-glow-blue: 0 0 12px rgba(74, 158, 255, 0.3);
  --stage-node-glow-green: 0 0 8px rgba(34, 197, 94, 0.2);
}

[data-theme="dark"] {
  --heatmap-0:            #161B22;
  /* heatmap-1 through heatmap-4 remain same (greens work in dark mode) */
}
```

---

## 9. Animation Summary

| Animation | Duration | Curve | Trigger |
|-----------|----------|-------|---------|
| Stage expand | 300ms | `ease-out` | Tap stage node |
| Stage collapse | 200ms | `ease-in` | Tap expanded stage |
| Task row stagger | 50ms each | `ease-out` | Stage expand |
| Bottom sheet enter | 300ms | `cubic-bezier(0.32,0.72,0,1)` | Tap task |
| Bottom sheet exit | 250ms | `ease-in` | Tap backdrop / swipe down |
| Day tooltip | 150ms | `ease-out` | Tap heatmap cell |
| Fly-in animation | 1500ms | `cubic-bezier(0.4,0,0.6,1)` | After checkin success |
| Dream bar fill | 400ms | `cubic-bezier(0.25,0.1,0.25,1)` | Fly-in reaches target |
| Theme transition | 300ms | `ease` | Toggle switch |
| Progress ring fill | 600ms | `var(--anim-ease-in-out)` | On stage data change |
