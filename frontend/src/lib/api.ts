import type {
  CheckResult, CompleteResult, LeaderboardEntry, Leaderboard, LessonData, Profile, SessionData, UnitData, UserState,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch { /* non-JSON error body */ }
    throw new ApiError(res.status, typeof detail === "string" ? detail : "Request failed");
  }
  return res.json();
}

const post = <T,>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

export const api = {
  me: () => request<UserState>("/me"),
  updateSettings: (b: { daily_goal_xp?: number; display_name?: string }) =>
    request<UserState>("/me", { method: "PATCH", body: JSON.stringify(b) }),
  path: () => request<{ units: UnitData[] }>("/path"),
  lesson: (id: number) => request<LessonData>(`/lessons/${id}`),
  completeLesson: (id: number, b: { mistakes: number; correct: number; duration_sec: number }) =>
    post<CompleteResult>(`/lessons/${id}/complete`, b),
  check: (exerciseId: number, answer: string, mode: string) =>
    post<CheckResult>(`/exercises/${exerciseId}/check`, { answer, mode }),
  checkPair: (exerciseId: number, left_id: number, right_id: number) =>
    post<{ correct: boolean }>(`/exercises/${exerciseId}/pair`, { left_id, right_id }),
  startSession: (kind: string, skillId?: number) =>
    request<SessionData>(`/sessions/start?kind=${kind}${skillId ? `&skill_id=${skillId}` : ""}`),
  completeSession: (b: { kind: string; skill_id?: number | null; correct: number; mistakes: number; duration_sec: number }) =>
    post<CompleteResult>("/sessions/complete", b),
  refillHearts: () => post<UserState>("/hearts/refill"),
  leaderboard: () => request<Leaderboard>("/leaderboard"),
  profile: () => request<Profile>("/profile"),
  advanceDay: (days = 1) => post<UserState>("/dev/advance-day", { days }),
  resetProgress: () => post<UserState>("/dev/reset"),
};
export type { LeaderboardEntry };
