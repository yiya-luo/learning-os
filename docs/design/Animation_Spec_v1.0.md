# Learning OS — Animation Specification v1.0

> Principle: animations are fast, purposeful, and celebratory. No decorative looping.

---

## 1. Check-in Animation (完成打卡)

### Overview
- **Trigger**: User taps "✨ 完成打卡" button
- **Total duration**: 2300ms
- **Overlay**: Semi-transparent dark overlay covers the entire page during animation
- **Dismiss**: Auto-dismisses after completion; tap anywhere to skip after 1500ms

### Timeline

```
0ms          300ms                   2300ms
├─────────────┼──────────────────────┤
│  Button     │    Animation         │
│  Loading    │    Sequence          │
│             │                      │
│  spinner    │  particles burst      │
│  150ms      │  XP text fly up       │
│  fade-in    │  Dream text fly up    │
│             │  Progress bar fills   │
│             │  Haptic feedback      │
└─────────────┴──────────────────────┘
```

---

## 2. Phase Details

### Phase 1: Button Loading (0ms – 300ms)

| Property | Value |
|----------|-------|
| Button text | "✨ 完成打卡" → spinner icon (20×20px) |
| Transition | 150ms `ease-out` text fade out, spinner fade in |
| Spinner | Simple ring spinner, gold color, 20×20px, rotates ∞ |
| Rotation speed | 600ms per full rotation |
| Button scale | `scale(1)` → `scale(0.96)` on press (50ms) → `scale(1)` on release |
| Background | Gold gradient slightly darkened (opacity 0.9) |

### Phase 2: Animation Sequence (300ms – 2300ms)

#### 2a. Particle Burst (300ms – 800ms)
- **Count**: 10 small gold circles, 6×6px each
- **Origin**: Center point of the check-in button
- **Trajectory**: Random angle (0°–360°), random distance (40–120px from origin)
- **Duration**: 500ms, `ease-out` curve
- **Opacity**: 1 → 0 over 500ms
- **Color**: `#E6B93D` (gold) with slight variance (±10° hue)
- **Scale**: 1 → 0.3 over duration

```
Particle trajectory pseudo-code:
  for 10 particles:
    angle = random(0, 2π)
    distance = random(40, 120)
    dx = cos(angle) × distance
    dy = sin(angle) × distance
    translate(dx, dy) over 500ms ease-out
    opacity: 1 → 0
    scale: 1 → 0.3
```

#### 2b. "+XP" Text Flight (300ms – 1800ms)
| Property | Value |
|----------|-------|
| Text | `+120 XP` |
| Font | 24px, bold, `#E6B93D` (gold) |
| Start position | Center of button |
| End position | 80px above button |
| Duration | 1500ms |
| Curve | Ease-out for Y, linear for opacity |
| Opacity timeline | 0–300ms: fade in 0→1; 300–1200ms: hold 1; 1200–1800ms: fade out 1→0 |
| Scale | 0.6 → 1.0 over first 200ms, then hold |

#### 2c. "+梦想值" Text Flight (350ms – 1850ms)
| Property | Value |
|----------|-------|
| Text | `+30 梦想值` |
| Font | 18px, `#E6B93D` (gold), regular weight |
| Start position | Center of button, offset 20px right from XP text |
| End position | 60px above button, offset 20px right |
| Duration | 1500ms |
| Opacity timeline | 0–350ms: fade in 0→1; 350–1250ms: hold 1; 1250–1850ms: fade out 1→0 |
| Scale | 0.6 → 1.0 over first 250ms, then hold |
| Delay from XP text | 50ms stagger |

#### 2d. Progress Bar Transition (350ms – 750ms)
| Property | Value |
|----------|-------|
| Duration | 400ms |
| Curve | `cubic-bezier(0.25, 0.1, 0.25, 1)` (ease-out) |
| Behavior | Smooth fill from current % to new % |
| Width transition | CSS `transition: width 400ms cubic-bezier(0.25, 0.1, 0.25, 1)` |
| Color pulse | Brief gold glow at the fill tip, fades over 300ms |

#### 2e. Haptic Feedback
| Time | Type | Platform |
|------|------|----------|
| 300ms | `light` / `impactLight` | UniApp `uni.vibrateShort()` |
| Quick vibration, single pulse, ~15ms | | |

---

## 3. Checkmark Confirmation (2100ms – 2300ms)
- Large green checkmark (✓) appears at center of animation area
- 48px, `#22C55E` (green)
- Scale 0 → 1.2 → 1.0 over 200ms (spring-like)
- Opacity fades in over 100ms, holds 100ms
- After 2300ms: overlay fades out 200ms, page returns to normal

---

## 4. Micro-interactions

### Task Checkbox Toggle
| Property | Value |
|----------|-------|
| Duration | 150ms |
| Curve | `ease-out` |
| Animation | Checkbox fill from left 0% → 100% (for check); reverse for uncheck |
| Check icon | Scale 0 → 1 over 100ms, slight bounce |
| Task text | Strikethrough slides in from left, 150ms, color fades to muted |
| Haptic | None (too frequent) |

### Tab Switch
| Property | Value |
|----------|-------|
| Duration | 200ms |
| Animation | Icon: outlined → filled, cross-fade 150ms |
| Label color: transition 150ms |
| No page sliding — content cross-fades 200ms |

### Progress Bar Fill (any page)
| Property | Value |
|----------|-------|
| Duration | 600ms |
| Curve | `cubic-bezier(0.4, 0, 0.2, 1)` (Material standard) |
| Behavior | Animate width property |
| On load | Animates from 0% to current value (entrance) |
| On update | Animates from previous value to new value |

### Skeleton Loading
| Property | Value |
|----------|-------|
| Animation | Pulsing opacity: 0.4 → 0.8 → 0.4 |
| Duration | 1.5s per cycle, infinite loop |
| Curve | `ease-in-out` |

### Stage Node State Change
| Property | Value |
|----------|-------|
| Locked → Open | 300ms, circle border color changes, lock → play icon cross-fade |
| Open → Complete | 400ms, circle fills from bottom (like water), play → check icon, green particle burst × 4 |
| Haptic | `light` on complete |

---

## 5. CSS Animation Variables

```css
:root {
  --anim-duration-fast: 150ms;
  --anim-duration-normal: 300ms;
  --anim-duration-slow: 500ms;
  --anim-duration-celebration: 2000ms;
  --anim-ease-out: cubic-bezier(0, 0, 0.2, 1);
  --anim-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --anim-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## 6. Performance Notes
- All animations use `transform` and `opacity` only (GPU-composited) — no `top`/`left`/`height` animations
- Particles rendered via `canvas` or `requestAnimationFrame` loop (not CSS animations with many elements)
- Check-in overlay uses absolute positioning with `will-change: transform` hint
- Skeleton pulses use `animation: pulse` on pseudo-elements
- Respect `prefers-reduced-motion` — if set, skip all animations or reduce to simple opacity fades

---

## 7. Accessibility
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
- Skip particle effects entirely when reduced motion is preferred
- Haptic feedback respects system vibration settings
