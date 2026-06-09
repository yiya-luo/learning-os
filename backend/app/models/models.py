import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex[:16]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    nickname = Column(String, nullable=False, default="Learner")
    avatar = Column(String, nullable=True)
    xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_checkin_date = Column(String, nullable=True)
    theme = Column(String, nullable=False, default="dark")
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now, onupdate=_now)

    checkins = relationship("Checkin", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    reward = Column(String, nullable=True)
    reward_price = Column(Integer, default=0)
    reward_image = Column(Text, nullable=True)
    deadline = Column(Integer, nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    created_at = Column(String, nullable=False, default=_now)

    stages = relationship("Stage", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Stage(Base):
    __tablename__ = "stages"

    id = Column(String, primary_key=True, default=_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    progress = Column(Float, nullable=False, default=0.0)

    project = relationship("Project", back_populates="stages")
    tasks = relationship("Task", back_populates="stage", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=_uuid)
    dsl_id = Column(String, nullable=True)
    stage_id = Column(String, ForeignKey("stages.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    xp = Column(Integer, nullable=False, default=10)
    estimate = Column(Integer, nullable=False, default=30)
    status = Column(String, nullable=False, default="pending")
    depends = Column(String, default="[]")
    check = Column(String, default="")
    resource = Column(String, default="")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(String, nullable=False, default=_now)
    completed_at = Column(String, nullable=True)

    stage = relationship("Stage", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    checkins = relationship("Checkin", back_populates="task")


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(String, primary_key=True, default=_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, default="u1")
    xp_earned = Column(Integer, nullable=False, default=0)
    dream_value_earned = Column(Integer, nullable=False, default=0)
    checked_at = Column(String, nullable=False, default=_now)

    task = relationship("Task", back_populates="checkins")
    user = relationship("User", back_populates="checkins")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_key = Column(String, nullable=False)
    unlocked_at = Column(String, nullable=False, default=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_key", name="uq_user_achievement"),
    )

    user = relationship("User", back_populates="achievements")


# Composite indexes
Index("idx_tasks_project_id", Task.project_id)
Index("idx_tasks_stage_id", Task.stage_id)
Index("idx_tasks_status", Task.project_id, Task.status)
Index("idx_tasks_dsl_id", Task.project_id, Task.dsl_id)
Index("idx_tasks_sort_order", Task.stage_id, Task.sort_order)
Index("idx_stages_project_id", Stage.project_id)
Index("idx_stages_sort_order", Stage.project_id, Stage.sort_order)
Index("idx_checkins_user_id", Checkin.user_id)
Index("idx_checkins_task_id", Checkin.task_id)
Index("idx_checkins_checked_at", Checkin.user_id, Checkin.checked_at)
