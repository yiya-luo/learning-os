# Learning OS — UI Specification v1.0

> Design principles: 长期主义 / 成长 / 游戏化 / 科技感 / 陪伴 / 温暖 / 极简

---

## Global Patterns

### Navigation Shell
- **Bottom Tab Bar**: 5 tabs, height 56px, fixed to bottom, `backdrop-filter: blur(20px)`
- Tab icons: outlined (inactive) / filled (active), 24×24px
- Active tab label: 12px, accent color. Inactive tab label: 10px, gray
- Safe area padding respected on all sides

### Page Transition
- Cross-fade 300ms `ease-in-out` between pages
- No sliding — minimal and calm

---

## Page 1: 首页 (Home)

### Layout Structure (top → bottom)
```
┌─────────────────────────────┐
│  Status Bar (native)        │
├─────────────────────────────┤
│  02:14               ☀️     │  ← header area: greeting + date
│  下午好，[昵称]               │     greeting: 24px bold
│  坚持的第 42 天 ✨           │     streak: 14px, amber
├─────────────────────────────┤
│  ╔═══════════════════════╗  │
│  ║  LV.8  知识学徒      ║  │  ← LevelCard
│  ║  ████████████░░ 78%  ║  │     XP bar inside card
│  ║  距离 LV.9 还需 220 XP║  │
│  ╚═══════════════════════╝  │
├─────────────────────────────┤
│  今日主线任务                 │  ← MainQuestProgress
│  ┌───────────────────────┐  │
│  │  📚 完成操作系统第 3 章  │  │     task name, 14px
│  │  ████████░░░░ 62%     │  │     progress bar: 8px height
│  │  2/3 小节已完成        │  │     sub-text: 12px, secondary
│  └───────────────────────┘  │
├─────────────────────────────┤
│  今日任务 (3)    查看全部 →  │  ← section header
│  ┌───┬───────────────────┐  │
│  │ ○ │ 阅读《现代操作系统》 │  │  ← TaskCard × 3
│  │ ○ │ 完成习题 3.1-3.5    │  │     checkbox 20×20px
│  │ ○ │ 输出学习笔记        │  │     title: 15px
│  └───┴───────────────────┘  │
├─────────────────────────────┤
│  梦想奖励                    │  ← DreamMiniProgress
│  🎁 Switch OLED ¥2,099     │
│  ████████░░ 45%  ¥945/¥2099│
│  预计 2026-08-15 完成       │
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │ 💡 每一次微小的坚持，    │  │  ← EncouragementCard
│  │ 都在重塑未来的你。      │  │     italic, 14px, accent
│  │ 昨天你完成了全部任务！  │  │     background: subtle gradient
│  └───────────────────────┘  │
├─────────────────────────────┤
│  [Tab Bar]                  │
└─────────────────────────────┘
```

### Component Breakdown
| # | Component | Props | Notes |
|---|-----------|-------|-------|
| 1 | LevelCard | `level: number, xp: number, xpToNext: number, title: string` | Card with gradient border |
| 2 | MainQuestProgress | `quest: { name, progress, totalSteps, completedSteps }` | Horizontal bar, 8px radius |
| 3 | TaskCard (×3) | `task: { id, title, done }` | Checkbox + title, tap to toggle |
| 4 | DreamMiniProgress | `dream: { name, icon, target, earned, eta }` | Compact horizontal layout |
| 5 | EncouragementCard | `text: string` | AI-generated, changes daily |

### States
| State | Behavior |
|-------|----------|
| **Loading** | Skeleton placeholders: 3 grey pulsing cards matching real layout |
| **Empty** | New user: LevelCard shows LV.1, encouragement card says "开始你的第一段旅程吧" |
| **Error** | Toast notification at top, retry button. Page content uses cached/last-known data |
| **Normal** | All sections rendered with live data |

### Interactions
- Tap LevelCard → navigate to Profile page
- Tap "查看全部" → navigate to Today's Tasks page
- Tap TaskCard checkbox → optimistic toggle, synced to store
- Tap DreamMiniProgress → navigate to Dream Reward page
- Pull down → refresh all data (native pull-to-refresh)
- Tap EncouragementCard → refresh AI encouragement

---

## Page 2: 学习地图 (Learning Map)

### Layout Structure
```
┌─────────────────────────────┐
│  Status Bar                 │
├─────────────────────────────┤
│  ← 返回    学习地图          │  ← nav header, 44px
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │ 操作系统 学习路径       │  │  ← subject badge
│  │ ████████░░░░ 62% 总体  │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│                             │
│       ● Stage 5 已完成      │  ← StageNode (vertical chain)
│       │                     │     node: 44×44px circle
│       │   (DependencyLine)  │     line: 2px wide, 32px tall
│       │                     │
│       ◐ Stage 4 进行中      │
│       │                     │
│       │                     │
│       ○ Stage 3 未开始      │
│       │                     │
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

### Component Breakdown
| # | Component | Props | Notes |
|---|-----------|-------|-------|
| 1 | StageTree | `stages: Stage[], currentStageId: string` | ScrollView, vertical layout |
| 2 | StageNode (×N) | `stage: { id, title, status, order }` | 3 states: locked/open/complete |
| 3 | DependencyLine | `status: 'locked' \| 'open' \| 'complete'` | Color varies by status |
| 4 | SubjectBadge | `subject: string, overallProgress: number` | Fixed at top |

### Node States
| State | Visual | Icon | Color |
|-------|--------|------|-------|
| ○ 未开始 (locked) | Circle outline | lock | #444A54 |
| ◐ 进行中 (open) | Circle filled 50% | play | #4A9EFF (blue) |
| ● 已完成 (complete) | Circle filled 100% | check | #22C55E (green) |

### States
| State | Behavior |
|-------|----------|
| **Loading** | Vertical chain of 5 grey skeleton circles, pulsing |
| **Empty** | Single node: "Stage 1" unlocked, message "从这里开始你的学习之旅" |
| **Error** | Inline error message + retry button |
| **Normal** | Full tree rendered, scrollable. Current stage auto-scrolled to center |

### Interactions
- Tap StageNode (locked) → toast "先完成前置阶段"
- Tap StageNode (open/current) → navigate to stage detail page
- Tap StageNode (complete) → navigate to stage review page
- Horizontal pinch → does nothing (vertical only, intentional)
- Long press StageNode → quick preview popover (stage stats)

---

## Page 3: 今日任务 (Today's Tasks)

### Layout Structure
```
┌─────────────────────────────┐
│  Status Bar                 │
├─────────────────────────────┤
│  ← 返回   今日任务   2h 30m  │  ← nav header + estimated time
├─────────────────────────────┤
│  📖 理论 (2/3)              │  ← Theory section
│  ┌───────────────────────┐  │
│  │ ✅ 阅读第 3.1 节        │  │  ← TaskCard (checkable)
│  │ ✅ 阅读第 3.2 节        │  │
│  │ ○ 阅读第 3.3 节        │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│  ✏️ 练习 (1/2)              │  ← Practice section
│  ┌───────────────────────┐  │
│  │ ✅ 完成习题 3.1-3.3    │  │
│  │ ○ 完成习题 3.4-3.6    │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│  💬 输出 (0/1)              │  ← Output section
│  ┌───────────────────────┐  │
│  │ ○ 写学习笔记并分享      │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │ 完成后可获得            │  │  ← Reward display
│  │ ⚡ +120 XP  💎 +30     │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│                             │
│    ┌─────────────────┐     │
│    │    ✨ 完成打卡 ✨  │     │  ← CheckinButton
│    └─────────────────┘     │     full-width, 52px height
│                             │     pill shape, gold gradient
├─────────────────────────────┤
│  [Tab Bar]                  │
└─────────────────────────────┘
```

### Component Breakdown
| # | Component | Props | Notes |
|---|-----------|-------|-------|
| 1 | TaskDetailCard | `tasks: Task[], sectionTitle: string, sectionIcon: string` | Grouped task list |
| 2 | TaskCard (reusable) | `task: { id, title, done, xp }` | Checkbox variant: interactive |
| 3 | CheckinButton | `disabled: boolean, allDone: boolean` | Triggers animation |
| 4 | CheckinAnimation | `visible: boolean` | Overlay, 2.3s total duration |
| 5 | RewardPreview | `xp: number, dreamValue: number` | Icon + number display |

### CheckinButton States
| State | Visual | Condition |
|-------|--------|-----------|
| Default | Gold gradient pill, text "✨ 完成打卡" | Tasks incomplete |
| Active | Slightly darker gold, text "✅ 全部完成,打卡!" | All tasks done |
| Disabled | Greyed out, opacity 0.4 | No tasks loaded |
| Loading | Spinner replaces text, 300ms | During check-in API call |
| Success | Green checkmark flash, then back to default | After animation completes |

### States
| State | Behavior |
|-------|----------|
| **Loading** | Skeleton list: 3 sections each with 2-3 grey rows |
| **Empty** | Illustration + "今天没有任务，去学习地图添加吧" + CTA button |
| **Error** | Inline error + retry. Stale data shown if available |
| **Normal** | Full task list with real-time checkbox state |

### Interactions
- Tap TaskCard checkbox → toggle done/undone, 150ms animation
- Swipe task left → quick action "跳过" (skip)
- Tap CheckinButton → 300ms loading → trigger CheckinAnimation overlay → call API
- CheckinAnimation plays automatically, dismisses on tap after 2.3s

---

## Page 4: 梦想奖励 (Dream Reward)

### Layout Structure
```
┌─────────────────────────────┐
│  Status Bar                 │
├─────────────────────────────┤
│  ← 返回    梦想奖励          │  ← nav header
├─────────────────────────────┤
│                             │
│    ┌─────────────────┐     │
│    │                 │     │  ← RewardImage
│    │   [Reward Img]  │     │     200×200px, rounded 16px
│    │                 │     │     centered, shadow
│    └─────────────────┘     │
│        Switch OLED          │  ← reward name, 20px bold
│        ¥2,099               │  ← target amount, 16px secondary
│                             │
├─────────────────────────────┤
│  ██████████░░░░░░░░  45%   │  ← ProgressBar (large)
│                             │     16px height, 12px radius
├─────────────────────────────┤
│  ┌─────────┬─────────┬─────┐│
│  │  总计    │  已积攒  │ 还需││  ← RewardStats
│  │ ¥2,099  │  ¥945   │¥1154││     3-column grid
│  └─────────┴─────────┴─────┘│
├─────────────────────────────┤
│  ┌───────────────────────┐  │
│  │ 🤖 AI 分析             │  │  ← AI explanation card
│  │                        │  │
│  │ 按当前每天 +30 的速度，  │  │
│  │ 你将在 2026-08-15       │  │
│  │ 达成目标。              │  │
│  │                        │  │
│  │ 如果每天多做 1 个任务，  │  │
│  │ 可以提前 12 天！💪      │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│  预计完成: 2026年8月15日     │  ← estimated date, centered, 14px
├─────────────────────────────┤
│  [Tab Bar]                  │
└─────────────────────────────┘
```

### Component Breakdown
| # | Component | Props | Notes |
|---|-----------|-------|-------|
| 1 | RewardImage | `src: string, name: string` | Placeholder if no image |
| 2 | ProgressBar | `value: number, max: number, size: 'large'` | Large variant: 16px height |
| 3 | RewardStats | `total: number, earned: number, remaining: number, unit: string` | 3-column stat grid |
| 4 | AIExplanation | `analysis: string, suggestions: string[]` | Expandable card |

### States
| State | Behavior |
|-------|----------|
| **Loading** | Skeleton: grey circle 200px, grey bar, 3 grey stat boxes |
| **Empty** | (never empty — always show default dream) |
| **Error** | Inline error + retry |
| **Normal** | Full dream reward display |

### Interactions
- Tap RewardImage → full-screen image viewer
- Tap AIExplanation → expand/collapse detailed analysis
- Long press ProgressBar → show tooltip with exact numbers

---

## Page 5: 我的 (Profile)

### Layout Structure
```
┌─────────────────────────────┐
│  Status Bar                 │
├─────────────────────────────┤
│                             │
│        ┌─────────┐         │
│        │  Avatar │         │  ← Avatar: 80×80px circle
│        │   🦊    │         │     tap to change
│        └─────────┘         │
│       知识学徒               │  ← nickname: 20px bold
│       @learner_42          │  ← handle: 14px secondary
│                             │
│  LV.8  ██████████░░ 78%    │  ← Level + XP bar
│  距离 LV.9 还需 220 XP      │
├─────────────────────────────┤
│  ┌───────┬───────┬───────┐ │
│  │  42   │   3   │  89%  │ │  ← Stats row
│  │连续打卡│进行中项目│完成率  │ │     numbers: 24px bold
│  └───────┴───────┴───────┘ │     labels: 12px secondary
├─────────────────────────────┤
│  ┌───────────────────────┐ │
│  │ 📥  导入学习 DSL       →│ │  ← MenuItem × 8
│  │ 📤  导出学习数据       →│ │     48px height
│  │ 📋  提示词模板          →│ │     16px icon + 15px title + arrow
│  │ 🎨  主题设置           →│ │
│  │ 💾  数据备份与恢复      →│ │
│  │ 🔔  每日提醒           →│ │
│  │ ℹ️  关于 Learning OS  →│ │
│  │ 🚪  退出登录           →│ │
│  └───────────────────────┘ │
├─────────────────────────────┤
│  Version 1.0.0  ·  Build 42│  ← footer, 12px, muted
├─────────────────────────────┤
│  [Tab Bar]                  │
└─────────────────────────────┘
```

### Component Breakdown
| # | Component | Props | Notes |
|---|-----------|-------|-------|
| 1 | Avatar | `src: string, size: number` | Tap to pick from presets |
| 2 | LevelCard (reused) | Same as Home page | Compact centered variant |
| 3 | StatsRow | `stats: { streak, activeProjects, completionRate }` | 3 numbers in row |
| 4 | MenuItem (×8) | `icon: string, title: string, to?: string, onClick?: fn` | Uniform row style |

### States
| State | Behavior |
|-------|----------|
| **Loading** | Skeleton: grey circle, grey text lines, 8 grey menu rows |
| **Empty** | N/A — always has user data |
| **Error** | Toast on action failure. Profile data uses cache |
| **Normal** | Full profile rendered |

### Interactions
- Tap Avatar → preset avatar picker (8 options)
- Tap nickname → inline edit mode
- Tap MenuItem → navigate or trigger action
- Tap "退出登录" → confirmation modal (danger style)
- Tap stats → navigate to detailed stats page
- Pull down → refresh profile data

---

## Shared UI Patterns

### Toast Notification
- Position: top center, 16px from safe area
- Height: 44px, pill shape (radius 9999px)
- Background: `rgba(0,0,0,0.85)`, text white 14px
- Auto-dismiss: 2s, swipe to dismiss
- Types: success (green icon), error (red icon), info (blue icon)

### Modal (Dialog)
- Centered, max-width 320px, radius 16px
- Background: card color, shadow modal
- Backdrop: `rgba(0,0,0,0.5)`, tap to dismiss
- 300ms scale-fade entrance: `scale(0.95)→scale(1)` + `opacity 0→1`

### Empty State
- Illustration (simple line drawing, 120×120px)
- Title: 16px bold, secondary color
- Description: 14px, muted
- CTA button: gold, pill shape, 44px height

---

## Responsive Notes
- Design is mobile-first (375–428px width baseline)
- Tablet: max-width 480px centered, subtle shadow on sides
- Desktop web: not a priority — mobile app focus
