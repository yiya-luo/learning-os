# Learning OS — Component Tree & API Reference

## Project Structure (UniApp + Vue 3 + Pinia)

```
src/
├── App.vue
├── pages/
│   ├── home/index.vue
│   ├── map/index.vue
│   ├── task/index.vue
│   ├── reward/index.vue
│   ├── profile/index.vue
│   └── import/index.vue
├── components/
│   ├── TaskCard.vue
│   ├── ProgressBar.vue
│   ├── CheckinAnimation.vue
│   └── StageNode.vue
├── stores/
│   ├── user.ts
│   ├── task.ts
│   ├── map.ts
│   ├── reward.ts
│   └── ui.ts
└── types/
    └── index.ts
```

---

## Component Hierarchy

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
│   │   └── EncouragementCard.vue
│   │
│   ├── map/index.vue
│   │   └── StageTree.vue
│   │       ├── StageNode.vue (×N)
│   │       └── DependencyLine.vue (×N-1)
│   │
│   ├── task/index.vue
│   │   ├── TaskDetailCard.vue
│   │   │   └── TaskCard.vue (×N)
│   │   ├── RewardPreview.vue
│   │   ├── CheckinButton.vue
│   │   └── CheckinAnimation.vue
│   │
│   ├── reward/index.vue
│   │   ├── RewardImage.vue
│   │   ├── ProgressBar.vue (large variant)
│   │   ├── RewardStats.vue
│   │   └── AIExplanation.vue
│   │
│   ├── profile/index.vue
│   │   ├── Avatar.vue
│   │   ├── LevelCard.vue (reused)
│   │   ├── StatsRow.vue
│   │   └── MenuItem.vue (×8)
│   │
│   └── import/index.vue
│       ├── MarkdownInput.vue
│       └── ParsePreview.vue
│
└── components/ (shared)
    ├── TaskCard.vue
    ├── ProgressBar.vue
    ├── CheckinAnimation.vue
    └── StageNode.vue
```

---

## Page Components

### `pages/home/index.vue` — 首页
No props (root page). Uses stores: `user`, `task`, `reward`.

### `pages/map/index.vue` — 学习地图
No props (root page). Uses stores: `map`, `user`.

### `pages/task/index.vue` — 今日任务
No props (root page). Uses stores: `task`, `user`, `reward`.

### `pages/reward/index.vue` — 梦想奖励
No props (root page). Uses stores: `reward`.

### `pages/profile/index.vue` — 我的
No props (root page). Uses stores: `user`.

### `pages/import/index.vue` — 导入学习DSL
No props (root page). Uses stores: `map`, `task`.

---

## Shared Components

### `components/TaskCard.vue`

```typescript
// Props
interface TaskCardProps {
  task: {
    id: string
    title: string
    done: boolean
    xp?: number           // XP reward for completing this task
    category?: 'theory' | 'practice' | 'output'
  }
  variant?: 'checkbox' | 'readonly'  // default: 'checkbox'
  size?: 'compact' | 'normal'        // default: 'normal'
}

// Emits
interface TaskCardEmits {
  (e: 'toggle', taskId: string): void         // user taps checkbox
  (e: 'longpress', taskId: string): void      // user long-presses
  (e: 'swipe', taskId: string, action: 'skip'): void
}

// Store used
// task store — calls task.toggleTask(id) on toggle emit
```

| Slot | Description |
|------|-------------|
| `default` | Replaces title area |
| `actions` | Extra action buttons after checkbox |

**States**: default (unchecked), checked (green check + strikethrough), skipped (greyed out + skip icon)

---

### `components/ProgressBar.vue`

```typescript
// Props
interface ProgressBarProps {
  value: number          // current value
  max: number            // max value (default: 100)
  size?: 'small' | 'normal' | 'large'   // default: 'normal'
  // small = 4px height, normal = 8px, large = 16px
  color?: 'gold' | 'blue' | 'green'     // default: 'gold'
  showLabel?: boolean    // show "value/max" text, default: false
  animated?: boolean     // animate on mount, default: true
}

// No emits — display-only component
// No store dependency — pure presentational
```

| Size | Height | Radius |
|------|--------|--------|
| small | 4px | 2px |
| normal | 8px | 4px |
| large | 16px | 8px |

**Colors**: gold (`#E6B93D`), blue (`#4A9EFF`), green (`#22C55E`)

---

### `components/CheckinAnimation.vue`

```typescript
// Props
interface CheckinAnimationProps {
  visible: boolean         // controls overlay visibility
  xpGained: number         // XP amount to display
  dreamGained: number      // Dream value amount to display
  onComplete?: () => void  // callback after animation finishes
}

// Emits
interface CheckinAnimationEmits {
  (e: 'complete'): void
  (e: 'dismiss'): void    // user taps to skip
}

// Internal: manages particle canvas, text flight animations
// Uses: `requestAnimationFrame` loop for particles
// Duration: 2300ms total (see Animation_Spec_v1.0.md)
// No store dependency
```

---

### `components/StageNode.vue`

```typescript
// Props
interface StageNodeProps {
  stage: {
    id: string
    title: string
    status: 'locked' | 'open' | 'complete'
    order: number         // 1-based order in tree
    progress?: number     // 0–100, only relevant when status='open'
  }
  isLast: boolean         // true if this is the last node in the tree
}

// Emits
interface StageNodeEmits {
  (e: 'tap', stageId: string): void
  (e: 'longpress', stageId: string): void
}

// Store used
// map store — reads stage status, navigates on tap
```

| State | Icon | Color | Border |
|-------|------|-------|--------|
| locked | lock (🔒) | `#444A54` | 2px solid, dashed |
| open | play (▶) | `#4A9EFF` | 2px solid |
| complete | check (✓) | `#22C55E` | 2px solid, filled bg |

---

## Page-Specific Components

### `LevelCard.vue` (used in home + profile)

```typescript
// Props
interface LevelCardProps {
  level: number
  xp: number
  xpToNext: number
  title: string            // level title, e.g. "知识学徒"
  variant?: 'full' | 'compact'   // default: 'full'
}

// No emits — display only (navigation handled by parent)
// Store used: user store
```

**full variant**: shows level icon, title, XP bar, "距离 LV.X 还需 N XP"
**compact variant** (profile): smaller, centered layout

---

### `MainQuestProgress.vue` (home)

```typescript
// Props
interface MainQuestProgressProps {
  quest: {
    name: string
    progress: number       // 0–100
    totalSteps: number
    completedSteps: number
  }
}

// No emits
// Store used: task store
```

---

### `TodayTaskPreview.vue` (home)

```typescript
// Props
interface TodayTaskPreviewProps {
  tasks: Task[]            // max 3 items
}

// Emits
interface TodayTaskPreviewEmits {
  (e: 'viewAll'): void
}

// Store used: task store
```

---

### `EncouragementCard.vue` (home)

```typescript
// Props
interface EncouragementCardProps {
  text: string
  loading?: boolean
}

// Emits
interface EncouragementCardEmits {
  (e: 'refresh'): void    // tap to get new encouragement
}

// Store used: ui store (for AI-generated text)
```

---

### `DreamMiniProgress.vue` (home)

```typescript
// Props
interface DreamMiniProgressProps {
  dream: {
    name: string
    icon: string
    target: number
    earned: number
    eta: string           // "2026-08-15"
  }
}

// Emits
interface DreamMiniProgressEmits {
  (e: 'tap'): void        // navigate to reward page
}
```

---

### `StageTree.vue` (map)

```typescript
// Props
interface StageTreeProps {
  stages: Stage[]
  currentStageId: string
}

// No emits
// Store used: map store
// Internal: renders StageNode + DependencyLine in a vertical chain
```

---

### `DependencyLine.vue` (map)

```typescript
// Props
interface DependencyLineProps {
  status: 'locked' | 'open' | 'complete'
}
// Renders a 2px wide, 32px tall vertical line
// Color: locked=#444A54, open=#4A9EFF, complete=#22C55E
```

---

### `TaskDetailCard.vue` (task)

```typescript
// Props
interface TaskDetailCardProps {
  sectionTitle: string
  sectionIcon: string     // emoji or icon name
  tasks: Task[]
}

// Emits
interface TaskDetailCardEmits {
  (e: 'toggle', taskId: string): void
}
```

---

### `CheckinButton.vue` (task)

```typescript
// Props
interface CheckinButtonProps {
  disabled: boolean
  allDone: boolean
  loading: boolean
}

// Emits
interface CheckinButtonEmits {
  (e: 'checkin'): void
}

// States: default, active (all tasks done), loading (spinner), disabled
```

---

### `RewardPreview.vue` (task)

```typescript
// Props
interface RewardPreviewProps {
  xp: number
  dreamValue: number
}
// Display-only: shows ⚡ +120 XP  💎 +30
```

---

### `RewardImage.vue` (reward)

```typescript
// Props
interface RewardImageProps {
  src: string
  name: string
  size?: number          // default: 200
}

// Emits
interface RewardImageEmits {
  (e: 'tap'): void       // open full-screen viewer
}

// States: loaded, loading (skeleton), error (placeholder with icon)
```

---

### `RewardStats.vue` (reward)

```typescript
// Props
interface RewardStatsProps {
  total: number
  earned: number
  remaining: number
  unit: string           // "¥" or "💎"
}
// 3-column grid layout
```

---

### `AIExplanation.vue` (reward)

```typescript
// Props
interface AIExplanationProps {
  analysis: string
  suggestions: string[]
  eta: string            // "2026-08-15"
  loading?: boolean
}

// Emits
interface AIExplanationEmits {
  (e: 'refresh'): void
}
// Collapsible card. Default: expanded.
```

---

### `Avatar.vue` (profile)

```typescript
// Props
interface AvatarProps {
  src: string
  size?: number          // default: 80
}

// Emits
interface AvatarEmits {
  (e: 'tap'): void       // open avatar picker
}
// Store used: user store
```

---

### `StatsRow.vue` (profile)

```typescript
// Props
interface StatsRowProps {
  streak: number
  activeProjects: number
  completionRate: number    // 0–100
}
// 3-column stat display
```

---

### `MenuItem.vue` (profile)

```typescript
// Props
interface MenuItemProps {
  icon: string
  title: string
  to?: string              // vue-router path
  danger?: boolean         // red text for destructive actions
}

// Emits
interface MenuItemEmits {
  (e: 'tap'): void
}
```

---

### `MarkdownInput.vue` (import)

```typescript
// Props
interface MarkdownInputProps {
  modelValue: string
  placeholder?: string
}

// Emits
interface MarkdownInputEmits {
  (e: 'update:modelValue', value: string): void
}
// Textarea with monospace font, syntax hints
```

---

### `ParsePreview.vue` (import)

```typescript
// Props
interface ParsePreviewProps {
  parsed: {
    stages: Stage[]
    tasks: Task[]
  } | null
  loading: boolean
  error: string | null
}

// No emits — display only
// States: empty (before parse), loading, error, preview (shows parsed data summary)
```

---

## Pinia Stores

### `stores/user.ts`
```typescript
interface UserState {
  id: string
  nickname: string
  avatar: string
  level: number
  xp: number
  xpToNextLevel: number
  levelTitle: string       // "知识学徒"
  streak: number           // consecutive check-in days
  activeProjects: number
  completionRate: number   // 0–100
}
// Actions: fetchUser(), updateProfile(), updateAvatar(), refreshStats()
```

### `stores/task.ts`
```typescript
interface TaskState {
  todayTasks: Task[]
  mainQuest: Quest | null
  isLoading: boolean
}
// Actions: fetchTodayTasks(), toggleTask(id), checkin(), skipTask(id)
// Getters: allDone, estimatedTime, completedCount, totalCount
```

### `stores/map.ts`
```typescript
interface MapState {
  stages: Stage[]
  currentStageId: string
  subject: string
}
// Actions: fetchStages(), getStageDetail(id)
// Getters: overallProgress, nextStage
```

### `stores/reward.ts`
```typescript
interface RewardState {
  dream: Dream
  isLoading: boolean
}
// Actions: fetchDream(), refreshAIExplanation()
```

### `stores/ui.ts`
```typescript
interface UIState {
  theme: 'light' | 'dark' | 'system'
  encouragement: string
  encouragementLoading: boolean
}
// Actions: refreshEncouragement(), setTheme(t)
```

---

## Type Definitions (`types/index.ts`)

```typescript
interface Task {
  id: string
  title: string
  done: boolean
  xp: number
  category: 'theory' | 'practice' | 'output'
  order: number
}

interface Quest {
  id: string
  name: string
  progress: number
  totalSteps: number
  completedSteps: number
}

interface Stage {
  id: string
  title: string
  status: 'locked' | 'open' | 'complete'
  order: number
  progress: number
  description: string
  tasks: Task[]
}

interface Dream {
  id: string
  name: string
  icon: string
  image: string
  target: number
  earned: number
  unit: string
  eta: string
  aiAnalysis: string
  aiSuggestions: string[]
}
```
