"""HTTP API (all routes are under /api).  Thin layer: validation + calling services."""
import random
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import services as svc
from .database import get_db
from .models import (Achievement, Course, Exercise, Lesson, Skill, StudySession, User,
                     UserAchievement, UserSkillProgress)

router = APIRouter(prefix="/api")


# ------------------------------------------------------------------- dependencies
def current_user(db: Session = Depends(get_db), x_user_id: int = Header(default=1)) -> User:
    """Auth is simplified: everyone is the default learner (id 1) unless X-User-Id says otherwise."""
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


# ---------------------------------------------------------------------- schemas
class SettingsIn(BaseModel):
    daily_goal_xp: int | None = Field(default=None, ge=5, le=100)
    display_name: str | None = Field(default=None, min_length=1, max_length=40)


class CheckIn(BaseModel):
    answer: str = ""
    mode: str = "lesson"          # 'lesson' costs hearts; anything else is free


class PairIn(BaseModel):
    left_id: int
    right_id: int


class LessonCompleteIn(BaseModel):
    mistakes: int = Field(ge=0)
    correct: int = Field(ge=0)
    duration_sec: int = Field(default=0, ge=0)


class SessionCompleteIn(BaseModel):
    kind: str
    skill_id: int | None = None
    correct: int = Field(ge=0)
    mistakes: int = Field(ge=0)
    duration_sec: int = Field(default=0, ge=0)


class DayIn(BaseModel):
    days: int = Field(default=1, ge=1, le=30)


# ------------------------------------------------------------------------- user
@router.get("/me")
def get_me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    state = svc.user_state(db, user)
    db.commit()    # persists lazy heart regeneration / streak expiry
    course = db.scalar(select(Course))
    state["course"] = {"title": course.title, "from_language": course.from_language,
                       "to_language": course.to_language}
    return state


@router.patch("/me")
def update_settings(body: SettingsIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.daily_goal_xp is not None:
        user.daily_goal_xp = body.daily_goal_xp
    if body.display_name is not None:
        user.display_name = body.display_name.strip()
    db.commit()
    return svc.user_state(db, user)


# ------------------------------------------------------------------------- path
@router.get("/path")
def get_path(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return svc.build_path(db, user)


# ---------------------------------------------------------------------- lessons
@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if not svc.skill_unlocked(db, user, lesson.skill):
        raise HTTPException(403, "This skill is locked")
    return {"id": lesson.id, "skill_id": lesson.skill_id, "skill_title": lesson.skill.title,
            "position": lesson.position, "exercises": [svc.serialize_exercise(e) for e in lesson.exercises]}


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, body: LessonCompleteIn, user: User = Depends(current_user),
                    db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    skill = lesson.skill
    if not svc.skill_unlocked(db, user, skill):
        raise HTTPException(403, "This skill is locked")

    perfect = body.mistakes == 0
    xp = svc.XP_LESSON + (svc.XP_LESSON_PERFECT_BONUS if perfect else 0)
    result = svc.record_session(db, user, kind="lesson", xp=xp, gems=5, correct=body.correct,
                                mistakes=body.mistakes, duration=body.duration_sec,
                                lesson_id=lesson.id, skill_id=skill.id)

    # Only the *next* lesson of a skill advances progress; replays just give XP.
    prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=skill.id))
    if prog is None:
        prog = UserSkillProgress(user_id=user.id, skill_id=skill.id, lessons_completed=0)
        db.add(prog)
    if lesson.position == prog.lessons_completed + 1:
        prog.lessons_completed += 1
    db.flush()
    result["skill_completed"] = prog.lessons_completed >= len(skill.lessons)
    result["perfect"] = perfect
    db.commit()
    result["user"] = svc.user_state(db, user)
    return result


# -------------------------------------------------------------------- exercises
def _get_exercise(db: Session, exercise_id: int) -> Exercise:
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(404, "Exercise not found")
    return ex


@router.post("/exercises/{exercise_id}/check")
def check_answer(exercise_id: int, body: CheckIn, user: User = Depends(current_user),
                 db: Session = Depends(get_db)):
    ex = _get_exercise(db, exercise_id)
    correct = svc.is_correct(ex, body.answer)
    if not correct and body.mode == "lesson":
        svc.lose_heart(user)
    else:
        svc.refresh_hearts(user)
    db.commit()
    return {"correct": correct, "correct_answer": ex.answer, "hearts": user.hearts,
            "next_heart_in_sec": svc.next_heart_in_sec(user)}


@router.post("/exercises/{exercise_id}/pair")
def check_pair(exercise_id: int, body: PairIn, db: Session = Depends(get_db),
               user: User = Depends(current_user)):
    ex = _get_exercise(db, exercise_id)
    ids = {o.id for o in ex.options}
    return {"correct": body.left_id == body.right_id and body.left_id in ids}


# --------------------------------------------- practice / timed / legendary sessions
@router.get("/sessions/start")
def start_session(kind: str, skill_id: int | None = None, user: User = Depends(current_user),
                  db: Session = Depends(get_db)):
    if kind not in ("practice", "timed", "legendary"):
        raise HTTPException(400, "Unknown session kind")
    if kind == "legendary":
        prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=skill_id))
        skill = db.get(Skill, skill_id) if skill_id else None
        if not skill or not prog or prog.lessons_completed < len(skill.lessons):
            raise HTTPException(403, "Finish every lesson of the skill to unlock its legendary challenge")
    pool = svc.practice_pool(db, user, skill_id if kind in ("legendary", "practice") else None)
    if not pool:
        raise HTTPException(400, "Complete a lesson first to unlock practice")
    size = {"practice": 8, "timed": 30, "legendary": 10}[kind]
    # Match-pairs is awkward under a clock, so timed mode skips it.
    if kind == "timed":
        pool = [e for e in pool if e.type != "match_pairs"]
    exercises = random.sample(pool, min(size, len(pool)))
    return {"kind": kind, "skill_id": skill_id, "time_limit_sec": svc.TIMED_SECONDS if kind == "timed" else None,
            "max_mistakes": svc.LEGENDARY_MAX_MISTAKES if kind == "legendary" else None,
            "exercises": [svc.serialize_exercise(e) for e in exercises]}


@router.post("/sessions/complete")
def complete_session(body: SessionCompleteIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.kind not in ("practice", "timed", "legendary"):
        raise HTTPException(400, "Unknown session kind")
    passed, xp, gems = True, 0, 0
    if body.kind == "practice":
        xp = svc.XP_PRACTICE
        svc.gain_heart(user)               # practising earns a heart back
    elif body.kind == "timed":
        xp, gems = min(body.correct * 2, 40), (5 if body.correct >= 10 else 0)
    else:
        passed = body.mistakes <= svc.LEGENDARY_MAX_MISTAKES
        xp, gems = (svc.XP_LEGENDARY, 20) if passed else (0, 0)

    if xp == 0:      # nothing earned (failed legendary / empty timed run): no streak credit
        db.commit()
        return {"passed": passed, "xp_earned": 0, "gems_earned": 0, "new_achievements": [],
                "streak": {"before": user.streak, "after": user.streak, "increased": False},
                "daily_goal_reached": False, "user": svc.user_state(db, user)}

    result = svc.record_session(db, user, kind=body.kind, xp=xp, gems=gems, correct=body.correct,
                                mistakes=body.mistakes, duration=body.duration_sec, skill_id=body.skill_id)
    if body.kind == "legendary" and body.skill_id:
        prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=body.skill_id))
        if prog:
            prog.legendary = True
            db.flush()
            # legendary count changed -> re-check badges
            for a in svc.check_achievements(db, user):
                result["new_achievements"].append({"title": a.title, "icon": a.icon,
                                                   "description": a.description, "gem_reward": a.gem_reward})
    db.commit()
    result["passed"] = passed
    result["user"] = svc.user_state(db, user)
    return result


# ----------------------------------------------------------------------- hearts
@router.post("/hearts/refill")
def refill_hearts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Mock shop: spend gems to restore all hearts."""
    svc.refresh_hearts(user)
    if user.hearts >= svc.MAX_HEARTS:
        raise HTTPException(400, "Hearts are already full")
    if user.gems < svc.REFILL_COST_GEMS:
        raise HTTPException(400, "Not enough gems")
    user.gems -= svc.REFILL_COST_GEMS
    user.hearts = svc.MAX_HEARTS
    user.hearts_updated_at = svc.utcnow()
    db.commit()
    return svc.user_state(db, user)


# ------------------------------------------------------- leaderboard / profile
@router.get("/leaderboard")
def get_leaderboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return svc.leaderboard(db, user)


@router.get("/profile")
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    state = svc.user_state(db, user)
    metrics = svc.metrics_for_user(db, user)
    unlocked = dict(db.execute(select(UserAchievement.achievement_id, UserAchievement.unlocked_at)
                               .where(UserAchievement.user_id == user.id)).all())
    badges = [svc.achievement_out(a, metrics, unlocked.get(a.id)) for a in db.scalars(select(Achievement))]
    totals = db.execute(select(StudySession.correct_count, StudySession.mistakes)
                        .where(StudySession.user_id == user.id)).all()
    answered = sum(c + m for c, m in totals)
    accuracy = round(100 * sum(c for c, _ in totals) / answered) if answered else 0
    db.commit()
    return {"user": state, "joined": user.created_at.date().isoformat(), "accuracy": accuracy,
            "stats": metrics, "achievements": badges}


# -------------------------------------------------------------------- dev tools
@router.post("/dev/advance-day")
def advance_day(body: DayIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Testing aid: pretend N days have passed so streak logic can be exercised."""
    user.day_offset += body.days
    svc.refresh_streak(user)
    db.commit()
    return svc.user_state(db, user)


@router.post("/dev/reset")
def reset_progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Wipe this learner's progress (keeps the account)."""
    for model in (StudySession, UserSkillProgress, UserAchievement):
        for row in db.scalars(select(model).filter_by(user_id=user.id)):
            db.delete(row)
    user.total_xp, user.gems, user.hearts, user.streak, user.longest_streak = 0, 500, svc.MAX_HEARTS, 0, 0
    user.last_active_date, user.day_offset = None, 0
    db.commit()
    return svc.user_state(db, user)
