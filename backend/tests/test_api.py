"""API smoke tests.  Run from backend/:  pytest -q"""
import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_full_learner_flow():
    with TestClient(app) as c:                       # lifespan seeds the DB
        me = c.get("/api/me").json()
        assert me["streak"] == 4 and me["hearts"] == 4 and me["daily_xp"] == 15

        path = c.get("/api/path").json()["units"]
        food = path[1]["skills"][0]
        assert food["state"] == "available" and food["lessons_completed"] == 1
        assert path[1]["skills"][1]["state"] == "locked"

        # locked skill can't be opened
        locked_lesson = c.get("/api/path").json()["units"][2]["skills"][0]
        assert c.get("/api/lessons/19").status_code == 403 or locked_lesson["state"] == "locked"

        lesson = c.get(f"/api/lessons/{food['next_lesson_id']}").json()
        assert len(lesson["exercises"]) == 8
        assert "answer" not in str(lesson).lower().replace("type_answer", "")   # no answer leaks
        ex = lesson["exercises"][0]

        wrong = c.post(f"/api/exercises/{ex['id']}/check", json={"answer": "zzz"}).json()
        assert wrong["correct"] is False and wrong["hearts"] == 3
        free = c.post(f"/api/exercises/{ex['id']}/check", json={"answer": "zzz", "mode": "practice"}).json()
        assert free["hearts"] == 3                       # practice mode costs no hearts

        done = c.post(f"/api/lessons/{food['next_lesson_id']}/complete",
                      json={"mistakes": 1, "correct": 8, "duration_sec": 100}).json()
        assert done["xp_earned"] == 10 and done["user"]["total_xp"] == me["total_xp"] + 10
        assert done["streak"]["increased"] is False      # already active today
        assert c.get("/api/path").json()["units"][1]["skills"][0]["lessons_completed"] == 2

        # streak: next day active -> 5, skipping two days -> reset
        c.post("/api/dev/advance-day", json={"days": 1})
        d2 = c.post(f"/api/lessons/{food['next_lesson_id'] + 1}/complete",
                    json={"mistakes": 0, "correct": 8}).json()
        assert d2["streak"]["after"] == 5 and d2["streak"]["increased"] is True
        assert c.post("/api/dev/advance-day", json={"days": 3}).json()["streak"] == 0

        # legendary needs a finished skill; practice earns a heart
        assert c.get("/api/sessions/start?kind=legendary&skill_id=4").status_code == 403
        assert c.get("/api/sessions/start?kind=legendary&skill_id=1").status_code == 200
        before = c.get("/api/me").json()["hearts"]
        p = c.post("/api/sessions/complete", json={"kind": "practice", "correct": 8, "mistakes": 0}).json()
        assert p["user"]["hearts"] == before + 1
        leg = c.post("/api/sessions/complete",
                     json={"kind": "legendary", "skill_id": 1, "correct": 9, "mistakes": 1}).json()
        assert leg["passed"] and any(a["title"] == "Legend" for a in leg["new_achievements"])

        assert c.get("/api/leaderboard").json()["entries"][0]["rank"] == 1
        assert len(c.get("/api/profile").json()["achievements"]) == 10
        assert c.post("/api/hearts/refill").json()["hearts"] == 5
