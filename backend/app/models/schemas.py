"""Pydantic request/response schemas matching API Contract v1.0."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Request Schemas ───────────────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    reward: Optional[str] = Field(default=None, max_length=200)
    reward_price: Optional[int] = Field(default=0, ge=0)
    deadline: Optional[str] = Field(default=None)


class ImportRequest(BaseModel):
    markdown: str = Field(default="")


class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = Field(default=None, min_length=1, max_length=50)
    avatar: Optional[str] = Field(default=None, max_length=500)


# ─── Response Schemas ──────────────────────────────────────────────────────────

class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str = ""
    reward: Optional[str] = None
    reward_price: Optional[int] = None
    deadline: Optional[str] = None
    progress: float = 0.0
    created_at: str

    class Config:
        from_attributes = True


class StageSummary(BaseModel):
    id: str
    title: str
    sort_order: int
    progress: float
    task_count: int
    done_count: int


class ProjectDetailResponse(ProjectResponse):
    stages: list[StageSummary] = []


class ImportResponse(BaseModel):
    project_id: str
    title: str
    stage_count: int
    task_count: int


class TaskSummary(BaseModel):
    id: str
    stage_id: str
    title: str
    type: str
    xp: int
    status: str
    sort_order: int

    class Config:
        from_attributes = True


class TaskDetail(BaseModel):
    id: str
    stage_id: str
    stage_title: str = ""
    project_id: str
    title: str
    type: str
    xp: int
    estimate: Optional[int] = None
    status: str
    depends: list[str] = []
    check: Optional[str] = None
    resource: Optional[str] = None
    sort_order: int
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True


class TodayTask(TaskSummary):
    stage_title: str = ""
    depends: list[str] = []
    blocked: bool = False
    check: Optional[str] = None


class TaskStatusResponse(BaseModel):
    id: str
    status: str
    previous_status: str
    started_at: str


class CheckinResponse(BaseModel):
    id: str
    status: str
    previous_status: str
    completed_at: str
    xp_earned: int
    dream_value_earned: float
    new_total_xp: int
    new_level: int
    xp_to_next_level: int
    streak: int
    easter_egg: Optional["EasterEgg"] = None
    achievement_unlocked: Optional["AchievementUnlockedSchema"] = None
    encouragement: Optional["EncouragementResponse"] = None


class XpResponse(BaseModel):
    total_xp: int
    level: int
    xp_to_next_level: int
    total_tasks_completed: int
    total_dream_value: float


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    checked_in_today: bool
    last_checkin_date: Optional[str] = None


class RewardResponse(BaseModel):
    project_id: str
    reward_name: Optional[str] = None
    reward_price: int = 0
    dream_value_earned: float = 0.0
    progress_percent: float = 0.0
    estimated_days_remaining: Optional[int] = None


class UserResponse(BaseModel):
    id: str
    nickname: str
    avatar: Optional[str] = None
    xp: int
    level: int
    streak: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


class TaskListResponse(BaseModel):
    tasks: list[TaskSummary]


class TodayTaskListResponse(BaseModel):
    date: str
    tasks: list[TodayTask]


# ─── Error Schemas ─────────────────────────────────────────────────────────────

class NotFoundError(BaseModel):
    detail: str


# ─── Phase 2 Schemas ──────────────────────────────────────────────────────────


class HeatmapCell(BaseModel):
    date: str
    count: int
    xp: int


class HeatmapStats(BaseModel):
    total_days_active: int
    longest_streak: int
    current_streak: int
    average_xp_per_day: float
    total_checkins: int
    best_day: Optional[dict] = None


class HeatmapResponse(BaseModel):
    heatmap: list[HeatmapCell]
    stats: HeatmapStats


class DagNode(BaseModel):
    id: str
    title: str
    type: str
    status: str
    xp: int
    stage_id: str
    stage_title: str
    sort_order: int


class DagEdge(BaseModel):
    source: str = Field(serialization_alias="from")
    target: str = Field(serialization_alias="to")

    class Config:
        populate_by_name = True


class DagStage(BaseModel):
    title: str
    progress: float
    task_count: int
    done_count: int


class DagResponse(BaseModel):
    nodes: list[DagNode]
    edges: list[DagEdge]
    stages: list[DagStage]


class StageTask(BaseModel):
    id: str
    title: str
    type: str
    status: str
    xp: int
    sort_order: int
    blocked: bool = False


class StageDetailResponse(BaseModel):
    id: str
    title: str
    sort_order: int
    progress: float
    task_count: int
    done_count: int
    tasks: list[StageTask]
    next_stage_id: Optional[str] = None
    next_stage_title: Optional[str] = None
    prev_stage_id: Optional[str] = None
    prev_stage_title: Optional[str] = None


class AchievementItem(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    earned_at: Optional[str] = None
    xp_bonus: Optional[int] = None


class AchievementsResponse(BaseModel):
    achievements: list[AchievementItem]
    total_earned: int
    total_available: int


class ThemeUpdate(BaseModel):
    theme: str = Field(..., pattern="^(dark|light)$")


class ThemeResponse(BaseModel):
    theme: str


class RewardImageResponse(BaseModel):
    image_url: str


class EasterEgg(BaseModel):
    triggered: bool = True
    type: str
    message: str
    bonus_xp: Optional[int] = None


class AchievementUnlockedSchema(BaseModel):
    id: str
    name: str
    xp_bonus: int


# ─── Phase 3: Analytics Schemas ───────────────────────────────────────────────

class AnalyticsPeriodData(BaseModel):
    tasks_completed: int = 0
    xp_earned: int = 0
    average_xp_per_day: float = 0.0
    most_productive_day: Optional[str] = None
    streak_days: Optional[int] = None
    completion_rate: float = 0.0


class AnalyticsChanges(BaseModel):
    tasks_completed_pct: Optional[float] = None
    xp_earned_pct: Optional[float] = None
    completion_rate_pct: float = 0.0


class TrendPoint(BaseModel):
    date: str
    tasks: int = 0
    xp: int = 0


class TaskTypeDistribution(BaseModel):
    count: int = 0
    percent: float = 0.0


class TaskTypeBreakdown(BaseModel):
    theory: TaskTypeDistribution
    practice: TaskTypeDistribution
    output: TaskTypeDistribution


class StageProgressItem(BaseModel):
    stage_title: str
    done: int = 0
    doing: int = 0
    pending: int = 0
    total: int = 0
    percent: float = 0.0


class RadarScores(BaseModel):
    completion: int = 0
    efficiency: int = 0
    streak: int = 0
    quality: int = 0
    speed: int = 0


class AnalyticsSummary(BaseModel):
    total_tasks_completed: int = 0
    total_xp: int = 0
    total_days_active: int = 0
    longest_streak: int = 0
    current_streak: int = 0
    favorite_type: str = "theory"
    projects_completed: int = 0
    stages_completed: int = 0
    first_checkin_date: Optional[str] = None


class AnalyticsResponse(BaseModel):
    period: str
    current: AnalyticsPeriodData
    previous: AnalyticsPeriodData
    changes: AnalyticsChanges
    trend: list[TrendPoint]
    task_type_distribution: TaskTypeBreakdown
    stage_progress: list[StageProgressItem]
    radar: RadarScores
    summary: AnalyticsSummary


# ─── Phase 3: Encouragement Schemas ─────────────────────────────────────────────


class EncouragementBonus(BaseModel):
    xp: int = Field(..., ge=0)
    dream_multiplier: float = Field(..., ge=1.0)


class EncouragementResponse(BaseModel):
    type: str
    icon: str
    color: str
    message: str
    bonus: Optional[EncouragementBonus] = None


class EncouragementRequest(BaseModel):
    project_id: str
    trigger_event: str
    task_id: Optional[str] = None


# ─── Phase 3: Milestone Schemas ─────────────────────────────────────────────────


class MilestoneItem(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    achieved: bool
    achieved_at: Optional[str] = None
    xp_bonus: int = 0


class MilestonesResponse(BaseModel):
    milestones: list[MilestoneItem]
    achieved_count: int
    total_count: int


# ─── Phase 3: Timeline Schemas ──────────────────────────────────────────────────


class TimelinePagination(BaseModel):
    page: int
    page_size: int
    total: int
    has_more: bool


class _TimelineEventBase(BaseModel):
    type: str
    date: str
    title: str


class TimelineCheckinEvent(_TimelineEventBase):
    type: str = "checkin"
    xp_earned: int = 0
    task_type: str = "theory"


class TimelineMilestoneEvent(_TimelineEventBase):
    type: str = "milestone"
    description: str = ""
    icon: str = "🏆"
    color: str = "#FFD700"
    xp_bonus: int = 0


class TimelineAchievementEvent(_TimelineEventBase):
    type: str = "achievement"
    description: str = ""
    icon: str = "⭐"
    color: str = "#8B5CF6"
    xp_bonus: int = 0


class TimelineStageEvent(_TimelineEventBase):
    type: str = "stage"
    description: str = ""
    stage_progress: float = 100.0
    tasks_completed: int = 0


TimelineEventType = (
    TimelineCheckinEvent
    | TimelineMilestoneEvent
    | TimelineAchievementEvent
    | TimelineStageEvent
)


class TimelineResponse(BaseModel):
    events: list[dict]
    pagination: TimelinePagination
