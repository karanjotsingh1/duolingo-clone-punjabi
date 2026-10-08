"""Business logic: hearts, streaks, XP, answer checking, path unlocking, achievements.

Routes (routes.py) stay thin and call into these functions.
"""
import random
import unicodedata
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import utcnow
from .models import (Achievement, Exercise, Lesson, Skill, StudySession, Unit, User,
                     UserAchievement, UserSkillProgress)

MAX_HEARTS = 5
HEART_REGEN_SEC = 30 * 60          # one heart every 30 minutes
REFILL_COST_GEMS = 350
XP_LESSON = 10
XP_LESSON_PERFECT_BONUS = 5
XP_PRACTICE = 5
XP_LEGENDARY = 40
LEGENDARY_MAX_MISTAKES = 1
TIMED_SECONDS = 120


# --------------------------------------------------------------------------- time
def effective_today(user: User) -> date:
    """'Today' for this learner. day_offset lets us simulate days passing."""
    return date.today() + timedelta(days=user.day_offset)


# ------------------------------------------------------------------------- hearts
def refresh_hearts(user: User) -> None:
    """Lazily apply time-based regeneration whenever hearts are read."""
    now = utcnow()
    if user.hearts >= MAX_HEARTS:
        user.hearts, user.hearts_updated_at = MAX_HEARTS, now
        return
    gained = int((now - user.hearts_updated_at).total_seconds() // HEART_REGEN_SEC)
    if gained > 0:
        user.hearts = min(MAX_HEARTS, user.hearts + gained)
        user.hearts_updated_at = now if user.hearts >= MAX_HEARTS else (
            user.hearts_updated_at + timedelta(seconds=gained * HEART_REGEN_SEC))


def lose_heart(user: User) -> None:
    refresh_hearts(user)
    if user.hearts <= 0:
        return
    if user.hearts == MAX_HEARTS:          # regeneration timer starts at the first lost heart
        user.hearts_updated_at = utcnow()
    user.hearts -= 1


def gain_heart(user: User) -> None:
    refresh_hearts(user)
    user.hearts = min(MAX_HEARTS, user.hearts + 1)


def next_heart_in_sec(user: User) -> int:
    if user.hearts >= MAX_HEARTS:
        return 0
    elapsed = (utcnow() - user.hearts_updated_at).total_seconds()
    return max(0, int(HEART_REGEN_SEC - elapsed))


# ------------------------------------------------------------------------ streak
def refresh_streak(user: User) -> None:
    """A streak survives only if the learner was active today or yesterday."""
    if user.last_active_date and user.last_active_date < effective_today(user) - timedelta(days=1):
        user.streak = 0


def daily_xp_by_date(db: Session, user: User) -> dict[date, int]:
    rows = db.execute(
        select(StudySession.activity_date, func.sum(StudySession.xp_earned))
        .where(StudySession.user_id == user.id).group_by(StudySession.activity_date)).all()
    return {d: int(x or 0) for d, x in rows}


def xp_today(db: Session, user: User) -> int:
    return daily_xp_by_date(db, user).get(effective_today(user), 0)


def week_activity(db: Session, user: User) -> list[dict]:
    today, by_date = effective_today(user), daily_xp_by_date(db, user)
    days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append({"date": d.isoformat(), "label": d.strftime("%a"), "xp": by_date.get(d, 0),
                     "active": by_date.get(d, 0) > 0, "is_today": i == 0})
    return days


def user_state(db: Session, user: User) -> dict:
    refresh_hearts(user)
    refresh_streak(user)
    today = effective_today(user)
    return {
        "id": user.id, "username": user.username, "display_name": user.display_name,
        "avatar_color": user.avatar_color, "total_xp": user.total_xp, "gems": user.gems,
        "hearts": user.hearts, "max_hearts": MAX_HEARTS, "next_heart_in_sec": next_heart_in_sec(user),
        "streak": user.streak, "longest_streak": user.longest_streak,
        "streak_active_today": user.last_active_date == today,
        "daily_goal_xp": user.daily_goal_xp, "daily_xp": xp_today(db, user),
        "week": week_activity(db, user), "day_offset": user.day_offset,
        "refill_cost": REFILL_COST_GEMS,
    }


# ------------------------------------------------------------------------ answers
def normalize(text: str) -> str:
    """Case/punctuation/whitespace-insensitive form used to compare answers."""
    text = unicodedata.normalize("NFC", text or "").lower()
    text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return " ".join(text.split())


def is_correct(ex: Exercise, answer: str) -> bool:
    if not ex.answer:          # match-pairs exercises are verified pair by pair instead
        return False
    accepted = [ex.answer or ""] + [a for a in (ex.alt_answers or "").split("|") if a]
    return normalize(answer) in {normalize(a) for a in accepted}


def serialize_exercise(ex: Exercise) -> dict:
    """Exercise payload for the client. Never includes the correct answer."""
    out = {"id": ex.id, "type": ex.type, "prompt": ex.prompt, "source_text": ex.source_text, "hint": ex.hint}
    if ex.type == "match_pairs":
        left = [{"id": o.id, "text": o.text} for o in ex.options]
        right = [{"id": o.id, "text": o.pair_text} for o in ex.options]
        random.Random(ex.id).shuffle(right)
        out["pairs"] = {"left": left, "right": right}
    else:
        out["options"] = [{"id": o.id, "text": o.text} for o in ex.options]
    return out


# --------------------------------------------------------------------------- path
def ordered_skills(db: Session) -> list[Skill]:
    return list(db.scalars(select(Skill).join(Unit).order_by(Unit.position, Skill.position)))


def progress_map(db: Session, user: User) -> dict[int, UserSkillProgress]:
    return {p.skill_id: p for p in db.scalars(
        select(UserSkillProgress).where(UserSkillProgress.user_id == user.id))}


def skill_unlocked(db: Session, user: User, skill: Skill) -> bool:
    prog = progress_map(db, user)
    for s in ordered_skills(db):
        if s.id == skill.id:
            return True
        p = prog.get(s.id)
        if not p or p.lessons_completed < len(s.lessons):   # previous skill unfinished
            return False
    return False


def build_path(db: Session, user: User) -> dict:
    prog = progress_map(db, user)
    prev_done, current_marked = True, False
    units_out = []
    units = list(db.scalars(select(Unit).order_by(Unit.position)))
    for unit in units:
        skills_out = []
        for s in unit.skills:
            p = prog.get(s.id)
            done_count = p.lessons_completed if p else 0
            total = len(s.lessons)
            completed = done_count >= total
            state = "completed" if completed else ("available" if prev_done else "locked")
            is_current = state == "available" and not current_marked
            current_marked = current_marked or is_current
            skills_out.append({
                "id": s.id, "title": s.title, "icon": s.icon, "state": state,
                "lessons_total": total, "lessons_completed": done_count,
                "legendary": bool(p and p.legendary), "is_current": is_current,
                "next_lesson_id": s.lessons[done_count].id if state == "available" else None,
            })
            prev_done = completed
        units_out.append({"id": unit.id, "title": unit.title, "description": unit.description,
                          "color": unit.color, "position": unit.position, "skills": skills_out})
    return {"units": units_out}


# --------------------------------------------------------------- practice pools
def practice_pool(db: Session, user: User, skill_id: int | None = None) -> list[Exercise]:
    """Exercises from lessons the learner has already completed."""
    prog = progress_map(db, user)
    pool: list[Exercise] = []
    for s in ordered_skills(db):
        p = prog.get(s.id)
        if not p or p.lessons_completed == 0 or (skill_id and s.id != skill_id):
            continue
        for lesson in s.lessons[:p.lessons_completed]:
            pool.extend(lesson.exercises)
    return pool


# ------------------------------------------------------------------ achievements
def metrics_for_user(db: Session, user: User) -> dict[str, int]:
    uid = user.id
    sessions = select(func.count()).select_from(StudySession).where(StudySession.user_id == uid)
    totals = dict(db.execute(select(Skill.id, func.count(Lesson.id)).join(Lesson).group_by(Skill.id)).all())
    progress = db.scalars(select(UserSkillProgress).where(UserSkillProgress.user_id == uid)).all()
    best_timed = db.scalar(select(func.max(StudySession.correct_count)).where(
        StudySession.user_id == uid, StudySession.kind == "timed")) or 0
    return {
        "lessons_completed": db.scalar(sessions.where(StudySession.kind == "lesson")) or 0,
        "perfect_lessons": db.scalar(sessions.where(StudySession.kind == "lesson", StudySession.mistakes == 0)) or 0,
        "total_xp": user.total_xp,
        "streak": max(user.streak, user.longest_streak),
        "skills_completed": sum(1 for p in progress if p.lessons_completed >= totals.get(p.skill_id, 99)),
        "legendary_count": sum(1 for p in progress if p.legendary),
        "best_timed_correct": best_timed,
        "goal_days": sum(1 for x in daily_xp_by_date(db, user).values() if x >= user.daily_goal_xp),
    }


def check_achievements(db: Session, user: User) -> list[Achievement]:
    metrics = metrics_for_user(db, user)
    owned = set(db.scalars(select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)))
    unlocked = []
    for a in db.scalars(select(Achievement)):
        if a.id not in owned and metrics.get(a.metric, 0) >= a.threshold:
            db.add(UserAchievement(user_id=user.id, achievement_id=a.id))
            user.gems += a.gem_reward
            unlocked.append(a)
    return unlocked


def achievement_out(a: Achievement, metrics: dict, unlocked_at: datetime | None = None) -> dict:
    return {"id": a.id, "code": a.code, "title": a.title, "description": a.description, "icon": a.icon,
            "gem_reward": a.gem_reward, "threshold": a.threshold,
            "progress": min(metrics.get(a.metric, 0), a.threshold),
            "unlocked": unlocked_at is not None, "unlocked_at": unlocked_at.isoformat() if unlocked_at else None}


# ----------------------------------------------------------- recording activity
def record_session(db: Session, user: User, *, kind: str, xp: int, gems: int = 0, correct: int = 0,
                   mistakes: int = 0, duration: int = 0, lesson_id: int | None = None,
                   skill_id: int | None = None) -> dict:
    """Persist a finished session and update XP, gems, streak, achievements.
    Returns the data the 'lesson complete' screens need."""
    refresh_streak(user)
    today = effective_today(user)
    xp_before = xp_today(db, user)
    streak_before = user.streak

    db.add(StudySession(user_id=user.id, kind=kind, lesson_id=lesson_id, skill_id=skill_id, xp_earned=xp,
                        gems_earned=gems, correct_count=correct, mistakes=mistakes, duration_sec=duration,
                        activity_date=today))
    user.total_xp += xp
    user.gems += gems

    first_activity_today = user.last_active_date != today
    if first_activity_today:
        yesterday = today - timedelta(days=1)
        user.streak = user.streak + 1 if user.last_active_date == yesterday else 1
        user.last_active_date = today
    user.longest_streak = max(user.longest_streak, user.streak)

    db.flush()   # so achievement metrics see the new session row
    new_achievements = check_achievements(db, user)
    return {
        "xp_earned": xp, "gems_earned": gems,
        "streak": {"before": streak_before, "after": user.streak, "increased": first_activity_today},
        "daily_goal_reached": xp_before < user.daily_goal_xp <= xp_before + xp,
        "new_achievements": [{"title": a.title, "icon": a.icon, "description": a.description,
                              "gem_reward": a.gem_reward} for a in new_achievements],
    }


# ------------------------------------------------------------------ leaderboard
def leaderboard(db: Session, user: User) -> dict:
    today = effective_today(user)
    since = today - timedelta(days=6)
    xp_sum = func.coalesce(func.sum(StudySession.xp_earned), 0)
    rows = db.execute(
        select(User, xp_sum.label("xp"))
        .outerjoin(StudySession, (StudySession.user_id == User.id) & (StudySession.activity_date >= since))
        .group_by(User.id).order_by(xp_sum.desc(), User.display_name)).all()
    n = len(rows)
    entries = []
    for i, (u, xp) in enumerate(rows, start=1):
        zone = "promotion" if i <= 5 else ("demotion" if i > n - 3 else "safe")
        entries.append({"rank": i, "user_id": u.id, "display_name": u.display_name,
                        "avatar_color": u.avatar_color, "xp": int(xp), "is_me": u.id == user.id, "zone": zone})
    return {"league": "Bronze League", "ends_in_days": 6 - today.weekday() + 1, "entries": entries}
