"use client";
// Page chrome: left Sidebar, StatsBar (streak / XP / gems / hearts), and the right rail.
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useUser } from "@/lib/user-context";
import { Bolt, Flame, Gem, Heart } from "./Icons";
import Mascot from "./Mascot";
import { ProgressBar, mmss, useToast } from "./ui";

const NAV = [
  { href: "/learn", icon: "🏠", label: "Learn" },
  { href: "/session/timed", icon: "⏱️", label: "Practice" },
  { href: "/leaderboard", icon: "🏆", label: "Leaderboards" },
  { href: "/profile", icon: "👤", label: "Profile" },
  { href: "/settings", icon: "⚙️", label: "More" },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <nav className="sidebar">
      <Link href="/learn" className="logo"><Mascot size={36} /> lingua</Link>
      {NAV.map((n) => (
        <Link key={n.href} href={n.href} className={`nav-item ${path.startsWith(n.href) ? "active" : ""}`}>
          <span className="nav-icon">{n.icon}</span><span className="nav-label">{n.label}</span>
        </Link>
      ))}
    </nav>
  );
}

function useCountdown(seconds: number) {
  const [left, setLeft] = useState(seconds);
  useEffect(() => {
    setLeft(seconds);
    const t = setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [seconds]);
  return left;
}

function StreakPopover() {
  const { user } = useUser();
  if (!user) return null;
  return (
    <div className="popover">
      <h3>{user.streak} day streak</h3>
      <p className="muted" style={{ margin: "6px 0 12px" }}>
        {user.streak_active_today ? "You practised today. Come back tomorrow to keep it going!" : "Do a lesson today to keep your streak alive!"}
      </p>
      <div className="week-strip">
        {user.week.map((d) => (
          <div className="week-day" key={d.date}>
            <div className={`week-dot ${d.active ? "on" : ""}`}>{d.active ? "✓" : ""}</div>{d.label[0]}
          </div>
        ))}
      </div>
    </div>
  );
}

function HeartsPopover({ close }: { close: () => void }) {
  const { user, setUser } = useUser();
  const toast = useToast();
  const router = useRouter();
  const left = useCountdown(user?.next_heart_in_sec ?? 0);
  if (!user) return null;
  const full = user.hearts >= user.max_hearts;
  const refill = async () => {
    try { setUser(await api.refillHearts()); toast({ icon: "❤️", title: "Hearts refilled!" }); close(); }
    catch (e: any) { toast({ icon: "⚠️", title: e.message }); }
  };
  return (
    <div className="popover">
      <div style={{ fontSize: 44 }}>❤️</div>
      <h3>{full ? "Hearts are full" : `${user.hearts} of ${user.max_hearts} hearts`}</h3>
      <p className="muted" style={{ margin: "6px 0 14px" }}>
        {full ? "Make mistakes in lessons and you lose hearts. Keep learning!" : `Next heart in ${mmss(left)}`}
      </p>
      {!full && (
        <>
          <button className="btn btn-blue btn-block" onClick={refill} disabled={user.gems < user.refill_cost}>
            Refill for <Gem size={18} /> {user.refill_cost}
          </button>
          <button className="btn btn-secondary btn-block" style={{ marginTop: 10 }}
            onClick={() => { close(); router.push("/session/practice"); }}>Practice to earn +1</button>
        </>
      )}
    </div>
  );
}

export function StatsBar() {
  const { user } = useUser();
  const [open, setOpen] = useState<null | "streak" | "hearts">(null);
  if (!user) return <div className="stats-row" style={{ minHeight: 40 }} />;
  const toggle = (k: "streak" | "hearts") => setOpen(open === k ? null : k);
  return (
    <div className="stats-row" style={{ position: "relative" }}>
      <div className="course-chip" title={user.course ? `${user.course.title} for ${user.course.from_language} speakers` : ""}>
        <div className="flag">EN</div>
      </div>
      <button className="stat" onClick={() => toggle("streak")} style={{ color: "var(--orange)" }}>
        <Flame grey={!user.streak_active_today && user.streak === 0} /> {user.streak}
      </button>
      <span className="stat" style={{ color: "#e5a800", cursor: "default" }} title="Total XP"><Bolt /> {user.total_xp}</span>
      <span className="stat" style={{ color: "var(--blue)", cursor: "default" }} title="Gems"><Gem /> {user.gems}</span>
      <button className="stat" onClick={() => toggle("hearts")} style={{ color: "var(--red)" }}>
        <Heart grey={user.hearts === 0} /> {user.hearts}
      </button>
      {open === "streak" && <StreakPopover />}
      {open === "hearts" && <HeartsPopover close={() => setOpen(null)} />}
    </div>
  );
}

export function DailyGoalCard() {
  const { user } = useUser();
  if (!user) return null;
  const done = user.daily_xp >= user.daily_goal_xp;
  return (
    <div className="card goal-card">
      <h3>Daily Goal</h3>
      <div className="row" style={{ gap: 12 }}>
        <span style={{ fontSize: 30 }}>{done ? "🏆" : "🎯"}</span>
        <div style={{ flex: 1 }}>
          <b style={{ color: "var(--heading)" }}>{done ? "Goal reached!" : "Earn XP today"}</b>
          <div style={{ margin: "6px 0 4px" }}><ProgressBar value={user.daily_xp} max={user.daily_goal_xp} gold={done} /></div>
          <span className="muted" style={{ fontSize: 14 }}>{Math.min(user.daily_xp, user.daily_goal_xp)} / {user.daily_goal_xp} XP</span>
        </div>
      </div>
    </div>
  );
}

export function RightRail() {
  return (
    <aside className="shell-rail">
      <StatsBar />
      <DailyGoalCard />
      <Link href="/session/timed" className="card timed-card">
        <span style={{ fontSize: 34 }}>⏱️</span>
        <div><b style={{ color: "var(--heading)" }}>Timed practice</b><p className="muted" style={{ fontSize: 14 }}>Beat the clock — 2 minutes, as many as you can</p></div>
      </Link>
      <Link href="/leaderboard" className="card timed-card">
        <span style={{ fontSize: 34 }}>🏆</span>
        <div><b style={{ color: "var(--heading)" }}>Bronze League</b><p className="muted" style={{ fontSize: 14 }}>See where you rank this week</p></div>
      </Link>
    </aside>
  );
}
