"""Creates tables and seeds the course, achievements, a demo learner and leaderboard rivals.

Idempotent: does nothing if a course already exists.  Run manually with:  python -m app.seed
"""
import random
import re
from datetime import date, timedelta

from sqlalchemy import select

from . import content, services
from .database import Base, SessionLocal, engine
from .models import (Achievement, Course, Exercise, ExerciseOption, Lesson, Skill, StudySession,
                     Unit, User, UserSkillProgress)

TOKEN = re.compile(r"[A-Za-z]+")


def _options(ex_pos, texts, correct=None):
    return [ExerciseOption(position=i, text=t, is_correct=(t == correct)) for i, t in enumerate(texts)]


def build_lesson_exercises(skill_def: dict, li: int) -> list[Exercise]:
    """Expand a skill's vocabulary + sentences into 8 varied exercises for lesson #li."""
    rng = random.Random(f"{skill_def['title']}-{li}")
    words, sentences = skill_def["words"], skill_def["sentences"]
    rot = words[li * 3 % len(words):] + words[:li * 3 % len(words)]
    sa, sb = sentences[(2 * li) % len(sentences)], sentences[(2 * li + 1) % len(sentences)]
    all_tokens = {t for s in sentences for t in TOKEN.findall(s[1])}

    def mcq(word, to_native: bool) -> Exercise:
        en, native = word
        pool = [w for w in words if w != word]
        wrong = rng.sample(pool, 3)
        if to_native:   # English word shown, pick Punjabi meaning
            opts, ans = [native] + [w[1] for w in wrong], native
            ex = Exercise(type="multiple_choice", prompt="ਸਹੀ ਮਤਲਬ ਚੁਣੋ", source_text=en, answer=ans)
        else:          # Punjabi word shown, pick English word
            opts, ans = [en] + [w[0] for w in wrong], en
            ex = Exercise(type="multiple_choice", prompt="ਇਸਦਾ ਅੰਗਰੇਜ਼ੀ ਮਤਲਬ ਚੁਣੋ", source_text=native, answer=ans)
        rng.shuffle(opts)
        ex.options = _options(0, opts, ans)
        return ex

    def match() -> Exercise:
        chosen = rot[:5]
        ex = Exercise(type="match_pairs", prompt="ਸਹੀ ਜੋੜੇ ਮਿਲਾਓ")
        ex.options = [ExerciseOption(position=i, text=en, pair_text=native, is_correct=True)
                      for i, (en, native) in enumerate(chosen)]
        return ex

    def translate(s) -> Exercise:
        native, en = s[0], s[1]
        own = TOKEN.findall(en)
        extra = [t for t in sorted(all_tokens) if t.lower() not in {o.lower() for o in own}]
        tiles = own + rng.sample(extra, min(3, len(extra)))
        rng.shuffle(tiles)
        ex = Exercise(type="translate", prompt="ਇਸ ਵਾਕ ਦਾ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਅਨੁਵਾਦ ਕਰੋ", source_text=native,
                      answer=en, alt_answers="|".join(s[3]) if len(s) > 3 else None)
        ex.options = _options(0, tiles)
        return ex

    def fill(s) -> Exercise:
        native, en, blank = s[0], s[1], s[2]
        sentence = re.sub(rf"\b{re.escape(blank)}\b", "____", en, count=1)
        extra = [t for t in sorted(all_tokens) if t.lower() != blank.lower() and t.lower() not in
                 {o.lower() for o in TOKEN.findall(en)}]
        opts = [blank] + rng.sample(extra, min(3, len(extra)))
        rng.shuffle(opts)
        ex = Exercise(type="fill_blank", prompt="ਖਾਲੀ ਥਾਂ ਭਰੋ", source_text=sentence, hint=native, answer=blank)
        ex.options = _options(0, opts, blank)
        return ex

    def type_answer(word) -> Exercise:
        return Exercise(type="type_answer", prompt="ਇਸਨੂੰ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਟਾਈਪ ਕਰੋ", source_text=word[1], answer=word[0])

    return [mcq(rot[0], True), mcq(rot[1], False), match(), translate(sa), fill(sb),
            type_answer(rot[2]), translate(sb), fill(sa)]


def seed_content(db) -> None:
    course = Course(**content.COURSE)
    db.add(course)
    for upos, u in enumerate(content.UNITS, start=1):
        unit = Unit(position=upos, title=u["title"], description=u["description"], color=u["color"])
        course.units.append(unit)       # append from the parent side so the session cascades the save
        for spos, sk in enumerate(u["skills"], start=1):
            skill = Skill(position=spos, title=sk["title"], icon=sk["icon"])
            unit.skills.append(skill)
            for li in range(content.LESSONS_PER_SKILL):
                lesson = Lesson(position=li + 1)
                skill.lessons.append(lesson)
                for pos, ex in enumerate(build_lesson_exercises(sk, li), start=1):
                    ex.position = pos
                    lesson.exercises.append(ex)
    for code, title, desc, icon, metric, threshold, gems in content.ACHIEVEMENTS:
        db.add(Achievement(code=code, title=title, description=desc, icon=icon, metric=metric,
                           threshold=threshold, gem_reward=gems))


def seed_demo_learner(db) -> None:
    """Sample learner 'You': two finished skills and one lesson of the third, 4-day streak."""
    today = date.today()
    user = User(username="learner", display_name="You", avatar_color="#58cc02", total_xp=0, gems=500,
                hearts=4, streak=4, longest_streak=4, last_active_date=today, daily_goal_xp=20)
    db.add(user)
    db.flush()
    skills = services.ordered_skills(db)
    # (skill index, lesson position, days ago, mistakes)
    history = [(0, 1, 3, 1), (0, 2, 3, 0), (0, 3, 2, 0), (1, 1, 2, 2), (1, 2, 1, 0), (1, 3, 1, 0), (2, 1, 0, 0)]
    for si, pos, ago, mistakes in history:
        lesson = skills[si].lessons[pos - 1]
        xp = services.XP_LESSON + (services.XP_LESSON_PERFECT_BONUS if mistakes == 0 else 0)
        db.add(StudySession(user_id=user.id, kind="lesson", lesson_id=lesson.id, skill_id=skills[si].id,
                            xp_earned=xp, gems_earned=5, correct_count=8, mistakes=mistakes,
                            duration_sec=150, activity_date=today - timedelta(days=ago)))
        user.total_xp += xp
        prog = db.scalar(select(UserSkillProgress).filter_by(user_id=user.id, skill_id=skills[si].id))
        if prog is None:
            db.add(UserSkillProgress(user_id=user.id, skill_id=skills[si].id, lessons_completed=pos))
        else:
            prog.lessons_completed = pos
        db.flush()
    services.check_achievements(db, user)
    user.gems = 500   # badge rewards are not applied to the seeded starting balance

    for username, name, color, weekly_xp in content.RIVALS:
        rival = User(username=username, display_name=name, avatar_color=color, total_xp=weekly_xp * 3,
                     streak=0, daily_goal_xp=20)
        db.add(rival)
        db.flush()
        for ago, share in ((3, 0.4), (1, 0.6)):
            db.add(StudySession(user_id=rival.id, kind="practice", xp_earned=round(weekly_xp * share),
                                activity_date=today - timedelta(days=ago)))


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Course.id)) is not None:
            return
        seed_content(db)
        db.flush()
        seed_demo_learner(db)
        db.commit()


if __name__ == "__main__":
    seed()
    print("Database seeded.")
