export type WeekDay = { date: string; label: string; xp: number; active: boolean; is_today: boolean };

export type UserState = {
  id: number; username: string; display_name: string; avatar_color: string;
  total_xp: number; gems: number; hearts: number; max_hearts: number; next_heart_in_sec: number;
  streak: number; longest_streak: number; streak_active_today: boolean;
  daily_goal_xp: number; daily_xp: number; week: WeekDay[]; day_offset: number; refill_cost: number;
  course?: { title: string; from_language: string; to_language: string };
};

export type SkillNodeData = {
  id: number; title: string; icon: string; state: "locked" | "available" | "completed";
  lessons_total: number; lessons_completed: number; legendary: boolean; is_current: boolean;
  next_lesson_id: number | null;
};
export type UnitData = { id: number; title: string; description: string; color: string; position: number; skills: SkillNodeData[] };

export type ExerciseType = "multiple_choice" | "translate" | "match_pairs" | "fill_blank" | "type_answer";
export type Option = { id: number; text: string };
export type Exercise = {
  id: number; type: ExerciseType; prompt: string; source_text: string | null; hint: string | null;
  options?: Option[]; pairs?: { left: Option[]; right: Option[] };
};
export type LessonData = { id: number; skill_id: number; skill_title: string; position: number; exercises: Exercise[] };
export type SessionData = {
  kind: "practice" | "timed" | "legendary"; skill_id: number | null;
  time_limit_sec: number | null; max_mistakes: number | null; exercises: Exercise[];
};

export type CheckResult = { correct: boolean; correct_answer: string | null; hearts: number; next_heart_in_sec: number };

export type NewAchievement = { title: string; icon: string; description: string; gem_reward: number };
export type CompleteResult = {
  xp_earned: number; gems_earned: number; passed?: boolean; perfect?: boolean; skill_completed?: boolean;
  streak: { before: number; after: number; increased: boolean };
  daily_goal_reached: boolean; new_achievements: NewAchievement[]; user: UserState;
};

export type LeaderboardEntry = {
  rank: number; user_id: number; display_name: string; avatar_color: string; xp: number;
  is_me: boolean; zone: "promotion" | "demotion" | "safe";
};
export type Leaderboard = { league: string; ends_in_days: number; entries: LeaderboardEntry[] };

export type Badge = {
  id: number; code: string; title: string; description: string; icon: string; gem_reward: number;
  threshold: number; progress: number; unlocked: boolean; unlocked_at: string | null;
};
export type Profile = {
  user: UserState; joined: string; accuracy: number; achievements: Badge[];
  stats: Record<string, number>;
};
