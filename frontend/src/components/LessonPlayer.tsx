"use client";
// The lesson loop. One component drives every mode:
//   lesson     - normal lesson: wrong answers cost hearts and are repeated at the end
//   practice   - free practice (no hearts lost), earns one heart back
//   timed      - 2 minute countdown, answer as many as you can
//   legendary  - hard challenge on a finished skill: allowed mistakes are limited
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { play } from "@/lib/sound";
import type { CompleteResult, Exercise } from "@/lib/types";
import { useUser } from "@/lib/user-context";
import { ExerciseView } from "./exercises";
import { Heart } from "./Icons";
import { FailedModal, LessonComplete, OutOfHeartsModal, QuitModal, StreakScreen } from "./LessonEnd";
import { ProgressBar, mmss, useToast } from "./ui";

export type PlayerSource =
  | { kind: "lesson"; id: number }
  | { kind: "practice" | "timed" | "legendary"; skillId?: number };

type Status = "idle" | "correct" | "wrong";
const PRAISE = ["Amazing!", "Correct!", "Great job!", "Awesome!", "Nice one!", "Perfect!"];

export default function LessonPlayer({ source }: { source: PlayerSource }) {
  const router = useRouter();
  const toast = useToast();
  const { user, setUser, refresh } = useUser();
  const kind = source.kind;
  const requeueWrong = kind === "lesson" || kind === "practice";   // wrong answers come back at the end

  const [attempt, setAttempt] = useState(0);                 // bump to restart (retry after failing)
  const [phase, setPhase] = useState<"loading" | "error" | "playing" | "result" | "streak">("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [queue, setQueue] = useState<Exercise[]>([]);
  const [total, setTotal] = useState(0);
  const [maxMistakes, setMaxMistakes] = useState<number | null>(null);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [mistakes, setMistakes] = useState(0);
  const [hearts, setHearts] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const [modal, setModal] = useState<null | "quit" | "hearts" | "failed">(null);
  const [result, setResult] = useState<CompleteResult | null>(null);
  const [seconds, setSeconds] = useState(0);
  const startedAt = useRef(Date.now());
  const finishing = useRef(false);

  /* ---------------------------------------------------------------- load */
  useEffect(() => {
    let cancelled = false;
    setPhase("loading"); setIdx(0); setAnswer(null); setStatus("idle"); setCorrectCount(0); setMistakes(0);
    setModal(null); finishing.current = false; startedAt.current = Date.now();
    const load = source.kind === "lesson"
      ? api.lesson(source.id).then((l) => ({ exercises: l.exercises, time: null as number | null, max: null as number | null }))
      : api.startSession(source.kind, source.skillId).then((s) => ({ exercises: s.exercises, time: s.time_limit_sec, max: s.max_mistakes }));
    load.then((d) => {
      if (cancelled) return;
      setQueue(d.exercises); setTotal(d.exercises.length); setTimeLeft(d.time); setMaxMistakes(d.max);
      setPhase("playing");
    }).catch((e) => { if (!cancelled) { setErrorMsg(e.message || "Could not load the lesson"); setPhase("error"); } });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt, kind, source.kind === "lesson" ? source.id : source.skillId]);

  // take the heart count from the user once, then track it locally; block lessons at 0 hearts
  useEffect(() => {
    if (user && hearts === null) {
      setHearts(user.hearts);
      if (kind === "lesson" && user.hearts === 0) setModal("hearts");
    }
  }, [user, hearts, kind]);

  /* ------------------------------------------------------------- finishing */
  const finish = useCallback(async () => {
    if (finishing.current) return;
    finishing.current = true;
    const duration = Math.max(1, Math.round((Date.now() - startedAt.current) / 1000));
    try {
      const res = source.kind === "lesson"
        ? await api.completeLesson(source.id, { mistakes, correct: correctCount, duration_sec: duration })
        : await api.completeSession({ kind: source.kind, skill_id: source.skillId ?? null, correct: correctCount, mistakes, duration_sec: duration });
      setUser(res.user);
      if (res.passed === false) { setModal("failed"); return; }
      setResult(res); setSeconds(duration); setPhase("result"); play("finish");
      res.new_achievements.forEach((a) => toast({ icon: a.icon, title: `Achievement: ${a.title}`, text: `${a.description} · +${a.gem_reward} gems` }));
    } catch (e: any) {
      toast({ icon: "⚠️", title: "Could not save progress", text: e.message });
      router.push("/learn");
    }
  }, [source, mistakes, correctCount, setUser, toast, router]);

  // timed mode countdown
  useEffect(() => {
    if (phase !== "playing" || timeLeft === null) return;
    if (timeLeft <= 0) { finish(); return; }
    const t = setTimeout(() => setTimeLeft((s) => (s === null ? s : s - 1)), 1000);
    return () => clearTimeout(t);
  }, [phase, timeLeft, finish]);

  /* --------------------------------------------------------------- answers */
  const ex = queue[idx];

  const applyResult = (correct: boolean, correctText: string | null, heartsNow: number | null) => {
    setStatus(correct ? "correct" : "wrong");
    setCorrectAnswer(correctText);
    play(correct ? "correct" : "wrong");
    if (correct) setCorrectCount((c) => c + 1);
    else {
      setMistakes((m) => m + 1);
      if (requeueWrong) setQueue((q) => [...q, ex]);
    }
    if (heartsNow !== null) setHearts(heartsNow);
  };

  const check = async (forced?: string) => {
    if (!ex || status !== "idle" || busy || ex.type === "match_pairs" && forced === undefined) return;
    const given = forced ?? answer;
    if (given === null) return;
    setBusy(true);
    try {
      const res = await api.check(ex.id, given, kind === "lesson" ? "lesson" : "free");
      applyResult(res.correct, res.correct_answer, res.hearts);
    } catch { toast({ icon: "⚠️", title: "Connection problem", text: "Please try again." }); }
    finally { setBusy(false); }
  };

  const advance = () => {
    if (idx + 1 >= queue.length) { finish(); return; }
    setIdx(idx + 1); setAnswer(null); setStatus("idle"); setCorrectAnswer(null);
  };

  const next = () => {
    if (status === "idle") return;
    if (kind === "legendary" && maxMistakes !== null && mistakes > maxMistakes) { setModal("failed"); return; }
    if (kind === "lesson" && status === "wrong" && hearts === 0) { setModal("hearts"); return; }
    advance();
  };

  // Enter = Check / Continue
  const keyRef = useRef<() => void>(() => {});
  keyRef.current = () => (status === "idle" ? check() : next());
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Enter" || modal || phase !== "playing") return;
      e.preventDefault();
      keyRef.current();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [modal, phase]);

  const exit = () => { refresh(); router.push("/learn"); };

  /* ---------------------------------------------------------------- render */
  if (phase === "loading") return <div className="lesson-shell"><div className="loading" style={{ flex: 1 }}>Loading…</div></div>;
  if (phase === "error") {
    return (
      <div className="lesson-shell"><div className="loading" style={{ flex: 1, textAlign: "center", gap: 16 }}>
        <div><p style={{ marginBottom: 16 }}>{errorMsg}</p><button className="btn btn-primary" onClick={exit}>Back to learn</button></div>
      </div></div>
    );
  }
  if (phase === "result" && result) {
    const attemptsTotal = requeueWrong ? total : correctCount + mistakes;
    const accuracy = attemptsTotal > 0 ? Math.max(0, Math.round(100 * (requeueWrong ? total - mistakes : correctCount) / attemptsTotal)) : 100;
    return <LessonComplete result={result} kind={kind} accuracy={Math.min(100, accuracy)} seconds={seconds}
      onContinue={() => (result.streak.increased ? setPhase("streak") : exit())} />;
  }
  if (phase === "streak" && result) return <StreakScreen user={result.user} onContinue={exit} />;
  if (!ex) return null;

  const progress = requeueWrong ? correctCount : idx + (status !== "idle" ? 1 : 0);
  const lives = maxMistakes !== null ? maxMistakes + 1 - mistakes : 0;
  const canCheck = answer !== null && !busy;

  return (
    <div className="lesson-shell">
      <div className="lesson-top">
        <button className="icon-btn" aria-label="Quit" onClick={() => setModal("quit")}>✕</button>
        <ProgressBar value={progress} max={total} />
        {kind === "lesson" && <div className="hearts-chip"><Heart size={26} grey={hearts === 0} /> {hearts ?? "-"}</div>}
        {kind === "practice" && <div className="hearts-chip" title="No hearts are lost in practice"><Heart size={26} /> ∞</div>}
        {kind === "timed" && timeLeft !== null && <div className={`timer-chip ${timeLeft <= 15 ? "low" : ""}`}>⏱️ {mmss(timeLeft)}</div>}
        {kind === "legendary" && <div className="timer-chip" style={{ color: "var(--purple-d)" }}>👑 ×{Math.max(0, lives)}</div>}
      </div>

      <div className="lesson-body">
        <ExerciseView key={`${ex.id}-${idx}`} ex={ex} locked={status !== "idle"} status={status} correctAnswer={correctAnswer}
          onAnswer={setAnswer} onPairMistake={() => setMistakes((m) => m + 1)}
          onMatchDone={() => applyResult(true, null, null)} />
      </div>

      <div className={`lesson-footer ${status === "idle" ? "" : status}`}>
        <div className="footer-inner">
          {status === "idle" && (
            <>
              <button className="btn btn-secondary skip-btn" onClick={() => check("")} disabled={busy}>Skip</button>
              <button className="btn btn-primary btn-lg" style={{ minWidth: 160 }} disabled={!canCheck} onClick={() => check()}>Check</button>
            </>
          )}
          {status === "correct" && (
            <>
              <div className="feedback">
                <div className="feedback-icon">✅</div>
                <div><h3>{PRAISE[idx % PRAISE.length]}</h3></div>
              </div>
              <button className="btn btn-primary btn-lg" style={{ minWidth: 160 }} onClick={next}>Continue</button>
            </>
          )}
          {status === "wrong" && (
            <>
              <div className="feedback">
                <div className="feedback-icon">❌</div>
                <div>
                  <h3>{correctAnswer ? "Correct solution:" : "Not quite!"}</h3>
                  <p>{correctAnswer ?? "Keep practising — you'll get it."}</p>
                </div>
              </div>
              <button className="btn btn-danger btn-lg" style={{ minWidth: 160 }} onClick={next}>Continue</button>
            </>
          )}
        </div>
      </div>

      {modal === "quit" && <QuitModal onStay={() => setModal(null)} onQuit={exit} />}
      {modal === "hearts" && user && (
        <OutOfHeartsModal user={user} onExit={exit}
          onRefilled={(u) => { setUser(u); setHearts(u.hearts); setModal(null); if (status !== "idle") advance(); }} />
      )}
      {modal === "failed" && (
        <FailedModal
          message={kind === "legendary" ? "Too many mistakes. Legendary challenges allow only one slip." : "Something went wrong."}
          onRetry={() => setAttempt((a) => a + 1)} onExit={exit} />
      )}
    </div>
  );
}
