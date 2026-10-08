"""Database schema.

Content tree:   Course -> Unit -> Skill -> Lesson -> Exercise -> ExerciseOption
Learner data:   User, UserSkillProgress, StudySession, UserAchievement
Reference:      Achievement

XP/streak/daily-goal numbers are *derived* from StudySession rows (single source
of truth) instead of being duplicated in separate counter tables. Only the
values that need to be fast/mutable (total xp, gems, hearts, streak) live on User.
"""
from datetime import date, datetime

from sqlalchemy import (Boolean, Date, DateTime, ForeignKey, Integer, String,
                        Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, utcnow


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    from_language: Mapped[str] = mapped_column(String(50))   # learner speaks
    to_language: Mapped[str] = mapped_column(String(50))     # learner learns
    units: Mapped[list["Unit"]] = relationship(back_populates="course", order_by="Unit.position")


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(200))
    color: Mapped[str] = mapped_column(String(20))           # banner colour on the path
    course: Mapped[Course] = relationship(back_populates="units")
    skills: Mapped[list["Skill"]] = relationship(back_populates="unit", order_by="Skill.position")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(10))            # emoji shown on the node
    unit: Mapped[Unit] = relationship(back_populates="skills")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="skill", order_by="Lesson.position")


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    skill: Mapped[Skill] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(back_populates="lesson", order_by="Exercise.position")


class Exercise(Base):
    __tablename__ = "exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    # multiple_choice | translate | match_pairs | fill_blank | type_answer
    type: Mapped[str] = mapped_column(String(20))
    prompt: Mapped[str] = mapped_column(String(200))          # instruction line
    source_text: Mapped[str | None] = mapped_column(String(300), nullable=True)  # sentence shown to the learner
    hint: Mapped[str | None] = mapped_column(String(300), nullable=True)         # e.g. Punjabi translation for fill-blank
    answer: Mapped[str | None] = mapped_column(String(300), nullable=True)       # canonical answer
    alt_answers: Mapped[str | None] = mapped_column(Text, nullable=True)         # '|' separated alternatives
    lesson: Mapped[Lesson] = relationship(back_populates="exercises")
    options: Mapped[list["ExerciseOption"]] = relationship(
        back_populates="exercise", order_by="ExerciseOption.position", cascade="all, delete-orphan")


class ExerciseOption(Base):
    """Choices for multiple-choice / fill-blank, word-bank tiles for translate,
    and (text, pair_text) rows for match-pairs."""
    __tablename__ = "exercise_options"
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(100))
    pair_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    exercise: Mapped[Exercise] = relationship(back_populates="options")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_color: Mapped[str] = mapped_column(String(20), default="#1cb0f6")
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    gems: Mapped[int] = mapped_column(Integer, default=500)
    hearts: Mapped[int] = mapped_column(Integer, default=5)
    hearts_updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_goal_xp: Mapped[int] = mapped_column(Integer, default=20)
    # Lets us *simulate* future days to test streak logic without waiting.
    day_offset: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class UserSkillProgress(Base):
    __tablename__ = "user_skill_progress"
    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    legendary: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class StudySession(Base):
    """One finished lesson / practice / timed / legendary run. Everything XP-related
    (daily goal, weekly leaderboard, streak calendar) is computed from these rows."""
    __tablename__ = "study_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))            # lesson | practice | timed | legendary
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    gems_earned: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    mistakes: Mapped[int] = mapped_column(Integer, default=0)
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)
    activity_date: Mapped[date] = mapped_column(Date, index=True)   # *effective* date (see User.day_offset)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Achievement(Base):
    __tablename__ = "achievements"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(200))
    icon: Mapped[str] = mapped_column(String(10))
    metric: Mapped[str] = mapped_column(String(30))          # key in services.metrics_for_user()
    threshold: Mapped[int] = mapped_column(Integer)
    gem_reward: Mapped[int] = mapped_column(Integer, default=10)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id", ondelete="CASCADE"))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
