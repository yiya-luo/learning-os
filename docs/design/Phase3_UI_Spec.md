# Learning OS — Phase 3 UI Specification

> Extends UI_Spec_v1.0 and Phase2_UI_Spec.md. Same design principles: minimalist, gamified, warm, tech-forward.

---

## Table of Contents
1. [Encouragement Modal](#1-encouragement-modal)
2. [Timeline Page](#2-timeline-page)
3. [Analytics Dashboard](#3-analytics-dashboard)
4. [Updated Component Tree](#4-updated-component-tree)

---

## 1. Encouragement Modal

### 1.1 Overview

A popup card that appears after a checkin completes, triggered by the encouragement engine. Five visual styles, one per encouragement type. Auto-dismisses after 3.5s.

### 1.2 Card Dimensions

- Size: 280px x 360px
- Border-radius: 16px
- Centered on screen with backdrop overlay
- Backdrop: rgba(0,0,0,0.5), tap to dismiss

### 1.3 Five Visual Styles

#### Growth (seedling / blue)

```
+--------------------------+
|                    [x]   |  close button, 24px
|                          |
|         seedling         |  icon: 48px
|                          |
|   Today you improved     |  message: 16px, weight 500
|   a bit more. 7 days     |  max 3 lines
|   ago you hadn't started.|
|                          |
|   +------------------+   |
|   |   Continue       |   |  CTA: 44px height, pill
|   +------------------+   |  bg: #3B82F6, white text
|                          |
+--------------------------+
```

Accent color: #3B82F6 (blue). Top border: 4px solid accent. Background: card-light.

#### Reward (gift / gold)

Same layout with:
- Icon: gift emoji
- Accent: #F59E0B (gold)
- CTA button: gold gradient bg
- Dream progress mini-bar shown below message (120px wide, 6px height, rounded)

#### Future (crystal ball / purple)

Same layout with:
- Icon: crystal ball emoji
- Accent: #8B5CF6 (purple)
- CTA button: purple gradient bg
- Next milestone hint shown below message

#### Retrospective (chart / green)

Same layout with:
- Icon: chart emoji
- Accent: #10B981 (green)
- CTA button: green gradient bg
- Stats preview (2-3 key numbers) shown below message

#### Easter Egg (sparkles / pink)

```
+--------------------------+
|                    [x]   |
|                          |
|        sparkles          |  sparkle animation (rotate + scale)
|        sparkle           |
|                          |
|   Rare four-leaf clover! |
|   Extra +10 XP           |  bonus callout: gold, 18px bold
|   Dream value x1.1 bonus |
|                          |
|   +------------------+   |
|   |   Awesome!       |   |  CTA: pink gradient bg
|   +------------------+   |
|                          |
+--------------------------+
```

Accent: #EC4899 (pink). Has sparkle particle animation overlay. Top border: 4px solid accent with shimmer.

### 1.4 Animations

| Phase | Duration | Description |
|-------|----------|-------------|
| Enter | 350ms | Scale 0.8->1.05->1.0 (spring bounce), opacity 0->1 |
| Idle | — | Easter egg only: subtle shimmer on border, sparkle particles |
| Exit | 250ms | Scale 1.0->0.9, opacity 1->0 |

Auto-dismiss: 3.5s timer starts after enter animation completes. Tap backdrop or close button dismisses immediately.

### 1.5 Props

```typescript
interface EncouragementModalProps {
  visible: boolean
  type: 'growth' | 'reward' | 'future' | 'retrospective' | 'easter_egg'
  icon: string
  color: string
  message: string
  bonus?: {
    xp: number
    dream_multiplier: number
  }
}
```

### 1.6 Integration

- Store: encouragementStore — holds current encouragement data, triggered by checkin response
- When checkin API returns encouragement field, store sets it and modal opens
- After dismiss or auto-dismiss, store clears the data
- Modal renders at app root level (above tab bar)

---

## 2. Timeline Page

### 2.1 Route and Access

- Route: /pages/timeline/index
- Access: From Profile menu item "Growth Timeline" (between "Growth Heatmap" and "Settings")
- NOT in main tab bar — accessed via profile page

### 2.2 Page Layout

```
+-------------------------------------+
|  Status Bar                         |
+-------------------------------------+
|  < Back    Growth Timeline           |  nav header, 44px
+-------------------------------------+
|  [All] [Milestones] [Achieve] [Checkin] [Stage] |  filter tabs
+-------------------------------------+
|                                     |
|  o ---- Today ----                  |  date separator
|  |                                  |
|  +-- [trophy] Monthly Persistence   |  milestone event
|  |    30-day streak                 |  icon + title + description
|  |    +50 XP                  06-08 |  XP badge + date right-aligned
|  |                                  |
|  +-- [check] Done: Download AAPL    |  checkin event
|  |    theory  +30 XP          06-08 |  type badge + XP
|  |                                  |
|  o ---- Yesterday ----              |
|  |                                  |
|  +-- [star] Stage Completer         |  achievement event
|  |    Done Stage: Basics            |
|  |    +40 XP                  06-07 |
|  |                                  |
|  +-- [flag] Stage Complete          |  stage event
|  |    Basics                        |
|  |    4 tasks done  100%      06-07 |
|  |                                  |
|  o ---- June 6 ----                 |
|  |                                  |
|  +-- [check] Done: if-else          |
|  |    theory  +20 XP          06-06 |
|  |                                  |
|  ---------- Load More ----------     |  auto-load on scroll
|                                     |
+-------------------------------------+
```

### 2.3 Event Card Specs

Each event card:
- Left border: 3px timeline line, color varies by type
  - milestone: #FFD700 (gold)
  - achievement: #8B5CF6 (purple)
  - checkin: #4A9EFF (blue)
  - stage: #22C55E (green)
- Padding: 12px medium
- Background: card-light
- Border-radius: 8px
- Gap between cards: 8px
- Timeline dot: 10px circle at the line intersection, same color as border

### 2.4 Date Separator

```
o ---- Today ----
```

- Font: 13px, text-secondary
- Line: 1px gray-200, fills remaining width
- Sticky at top when scrolling

### 2.5 Filter Tabs

Horizontal scrollable tab bar below nav:

```
+----------------------------------------------+
| [All]  [Milestones]  [Achieve]  [Checkin]  [Stage] |  44px height
+----------------------------------------------+
```

- Active tab: primary color text + bottom indicator (2px, 20px wide)
- Inactive tab: text-secondary
- Tap switches filter, reloads from page 1

### 2.6 Infinite Scroll

- onReachBottom triggers: load page+1, append events
- Loading state: skeleton cards (3x) at bottom
- "No more" when has_more === false
- Error state: inline retry at bottom

### 2.7 States

| State | Visual |
|-------|--------|
| Loading | 3 skeleton event cards with pulsing grey placeholders |
| Empty (filtered) | "No {type} events yet" centered |
| Empty (all) | "Start learning! Your first checkin will appear here." + link to tasks |
| Error | Inline error message + retry button |
| Normal | Timeline feed with date separators |

---

## 3. Analytics Dashboard

### 3.1 Route and Access

- Route: /pages/analytics/index
- Access: From Profile menu item "Data Insights" (between "Growth Timeline" and "Settings")
- NOT in main tab bar

### 3.2 Page Layout

```
+-------------------------------------+
|  Status Bar                         |
+-------------------------------------+
|  < Back    Data Insights             |  nav header
+-------------------------------------+
|  [This Week] [This Month] [All Time]|  period selector
+-------------------------------------+
|                                     |
|  +-- Period Comparison -----------+ |
|  |  This Week   Last Week  Change | |
|  |  12 tasks    8 tasks    +50%   | |  comparison cards
|  |  285 XP      190 XP     +50%   | |  3-column layout
|  |  85% rate    65%        +30.8% | |
|  +--------------------------------+ |
|                                     |
|  +-- Daily Trend -----------------+ |
|  |  bar chart: tasks per day      | |  canvas, 343x120px
|  |  Mon Tue Wed Thu Fri Sat Sun   | |
|  +--------------------------------+ |
|                                     |
|  +-- Task Type Distribution ------+ |
|  |  theory   ==========  41.7% (5)| |  horizontal bars
|  |  practice ==========  41.7% (5)| |
|  |  output   ====        16.7% (2)| |
|  +--------------------------------+ |
|                                     |
|  +-- Ability Radar ---------------+ |
|  |          completion(85)         | |
|  |            /  \                 | |  radar chart
|  |   speed(55)|  |efficiency(72)   | |  echarts radar
|  |           |    |               | |  300x300px
|  |            \  /                 | |
|  |    quality(90)--streak(65)      | |
|  +--------------------------------+ |
|                                     |
|  +-- Stage Progress ---------------+ |
|  |  Basics     ============ 100%   | |  per-stage progress bars
|  |  Data       ========     66%   | |
|  |  Strategy   ===          20%   | |
|  +--------------------------------+ |
|                                     |
|  +-- Summary ---------------------+ |
|  |  120 tasks  2850 XP  45 active | |  summary stats grid
|  |  longest 30  favorite practice | |
|  +--------------------------------+ |
|                                     |
+-------------------------------------+
```

### 3.3 Period Selector

Segmented control:
```
+------------------------------+
| [This Week] | [Month] | [All]|
+------------------------------+
```

- Active segment: filled bg primary color, white text
- Inactive: transparent, text-secondary
- Width: 240px, centered
- Height: 36px
- Border-radius: 18px (pill-shaped container)

### 3.4 Comparison Cards

3-column layout:
```
+-------------------+
|   Tasks Done      |  label: 11px, muted
|   12 up 50%       |  current value: 20px bold
|   Last week 8     |  previous: 12px, secondary
+-------------------+
```

- Background: card-light
- Border-radius: 8px
- Padding: 12px
- Positive change: green up arrow
- Negative change: red down arrow
- Width: (screen - 32px) / 3

### 3.5 Trend Chart

Mini bar chart showing daily XP/tasks for the period:
- Canvas: 343x120px (screen width - 32px padding)
- Bars: rounded top corners (2px radius), 8px wide, gap adaptive
- Color: #4A9EFF with 80% opacity
- X-axis: Mon-Sun labels (week), simplified dates (month), months (all)
- Y-axis: auto-scaled
- Tooltip on tap: "Wed: 3 tasks, 70 XP"

### 3.6 Task Type Distribution

Horizontal bar chart:
```
theory    ==============    41.7%  5
practice  ============      41.7%  5
output    ====               16.7%  2
```

- Bar height: 24px
- Bar colors: theory=#4A9EFF, practice=#22C55E, output=#F59E0B
- Border-radius: 4px
- Gap between bars: 8px
- Label left: 40px width
- Percentage + count right: auto width

### 3.7 Radar Chart

Implementation: echarts radar chart type.

- Size: 300x300px, centered
- Fill: rgba(74, 158, 255, 0.15) (blue tint)
- Stroke: #4A9EFF, 2px
- Vertex dots: 6px, #4A9EFF, white fill
- Axis labels: Chinese
- Grid: 5 concentric pentagons
- Animation: 800ms ease-out on data load

### 3.8 Stage Progress

Per-stage progress bar list:
```
Basics    ====================  100%  4/4
Data      ==============        66%  2/3
Strategy  ====                   20%  1/5
```

- Bar height: 18px
- Bar color: green gradient
- Track: gray-100
- Border-radius: 9px (full round)
- Stage name: left, 14px
- Percentage + fraction: right, 12px, secondary

### 3.9 Summary Grid

```
+------------+------------+
| Tasks Done | Total XP   |
|   120      |   2,850    |
+------------+------------+
| Active Days| Longest    |
|   45 days  |   30 days  |
+------------+------------+
| Favorite   | First Day  |
|   practice |   04-25    |
+------------+------------+
```

2x3 grid of stat cards. Each: 8px border-radius, card-light background. Label: 11px, muted. Value: 18px bold.

### 3.10 States

| State | Visual |
|-------|--------|
| Loading | Full page skeleton: shimmer placeholders for each section |
| Empty | "Not enough data yet. Complete some tasks and come back!" centered |
| Error | Section-level errors with retry per section |
| Normal | All sections rendered with data |

---

## 4. Updated Component Tree

```
App.vue
+-- pages/
|   +-- home/index.vue                 (unchanged)
|   +-- map/index.vue                  (unchanged)
|   +-- task/index.vue                 (unchanged from Phase 2)
|   +-- heatmap/index.vue              (unchanged from Phase 2)
|   +-- reward/index.vue               (unchanged from Phase 2)
|   +-- profile/index.vue              (updated: add menu items)
|   +-- import/index.vue               (unchanged)
|   |
|   +-- timeline/index.vue             NEW PAGE
|   |   +-- TimelineFilter.vue
|   |   +-- TimelineDateSeparator.vue
|   |   +-- TimelineMilestoneCard.vue
|   |   +-- TimelineAchievementCard.vue
|   |   +-- TimelineCheckinCard.vue
|   |   +-- TimelineStageCard.vue
|   |
|   +-- analytics/index.vue            NEW PAGE
|       +-- PeriodSelector.vue
|       +-- ComparisonCards.vue
|       +-- TrendChart.vue
|       +-- TaskTypeDistribution.vue
|       +-- RadarChart.vue
|       +-- StageProgressList.vue
|       +-- SummaryGrid.vue
|
+-- components/
|   +-- EncouragementModal.vue          NEW: global modal overlay
|   +-- ... (existing shared components)
|
+-- stores/
    +-- encouragementStore.ts           NEW: encouragement state
    +-- analyticsStore.ts               NEW: analytics data
    +-- timelineStore.ts                NEW: timeline state
    +-- ... (existing stores)
```

---

## 5. New Design Tokens

```css
:root {
  /* Encouragement Modal */
  --encourage-card-width:      280px;
  --encourage-card-height:     360px;
  --encourage-card-radius:     16px;
  --encourage-auto-dismiss:    3500ms;
  --encourage-enter-duration:  350ms;
  --encourage-exit-duration:   250ms;

  /* Timeline */
  --timeline-line-width:       3px;
  --timeline-dot-size:         10px;
  --timeline-card-min-height:  64px;
  --timeline-date-separator-height: 32px;

  /* Analytics */
  --analytics-card-gap:        8px;
  --analytics-section-gap:     16px;
  --radar-chart-size:          300px;
  --period-selector-height:    36px;
  --period-selector-width:     240px;

  /* Encouragement Colors */
  --encourage-growth:          #3B82F6;
  --encourage-reward:          #F59E0B;
  --encourage-future:          #8B5CF6;
  --encourage-retrospective:   #10B981;
  --encourage-easter-egg:      #EC4899;
}
```

---

## 6. Animation Summary

| Animation | Duration | Curve | Trigger |
|-----------|----------|-------|---------|
| Encouragement modal enter | 350ms | cubic-bezier(0.34,1.56,0.64,1) | Checkin response has encouragement |
| Encouragement modal exit | 250ms | ease-in | Tap close or auto-dismiss (3.5s) |
| Easter egg sparkle | 2000ms loop | ease-in-out | Easter egg modal visible |
| Timeline filter tab switch | 200ms | ease-out | Tap filter |
| Timeline card entrance | 300ms | ease-out | Scroll into view (staggered) |
| Radar draw animation | 800ms | ease-out | Data load complete |
| Period comparison number count-up | 600ms | ease-out | Data load complete |
| Progress bar fill | 400ms | cubic-bezier(0.25,0.1,0.25,1) | Data load complete |
