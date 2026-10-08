"use client";
import { useRouter } from "next/navigation";
import type { SkillNodeData } from "@/lib/types";
import Mascot from "./Mascot";

const R = 50;                       // ring radius
const CIRC = 2 * Math.PI * R;

function darken(hex: string) {      // quick darker shade for the 3D button edge
  const n = parseInt(hex.slice(1), 16);
  const f = (v: number) => Math.max(0, Math.floor(v * 0.78));
  return `rgb(${f(n >> 16)}, ${f((n >> 8) & 255)}, ${f(n & 255)})`;
}

type Props = {
  skill: SkillNodeData; color: string; offset: number; open: boolean;
  onToggle: () => void; onClose: () => void;
};

export default function SkillNode({ skill, color, offset, open, onToggle, onClose }: Props) {
  const router = useRouter();
  const { state, lessons_completed: done, lessons_total: total } = skill;
  const completed = state === "completed";
  const fraction = completed ? 1 : done / total;

  const go = (url: string) => { onClose(); router.push(url); };

  return (
    <div className="node-wrap" style={{ transform: `translateX(${offset}px)`, ["--node" as any]: color, ["--node-d" as any]: darken(color) }}>
      {state !== "locked" && (
        <svg className="node-ring" viewBox="0 0 110 110" aria-hidden>
          <circle cx="55" cy="55" r={R} fill="none" stroke="var(--border)" strokeWidth="8" />
          <circle cx="55" cy="55" r={R} fill="none" strokeWidth="8" strokeLinecap="round"
            stroke={completed ? "var(--yellow)" : color}
            strokeDasharray={`${CIRC * fraction} ${CIRC}`} transform="rotate(-90 55 55)" />
        </svg>
      )}

      {skill.is_current && !open && <div className="start-bubble">{done > 0 ? "CONTINUE" : "START"}</div>}
      {skill.is_current && (
        <div className="path-mascot float" style={{ left: -96, top: 14 }}><Mascot size={78} mood="happy" /></div>
      )}

      <button className={`skill-btn ${state === "locked" ? "locked" : completed ? "done" : "available"}`}
        onClick={onToggle} aria-label={`${skill.title} (${state})`}>
        {state === "locked" ? "🔒" : completed ? "⭐" : skill.icon}
        {state !== "locked" && <span className="crown-badge">👑 {completed ? total : done}</span>}
      </button>

      {open && (
        <div className={`node-popover ${state === "locked" ? "locked" : ""}`}
          style={state === "locked" ? undefined : { background: completed ? "var(--yellow-d)" : color }}>
          <h3>{skill.title}</h3>
          {state === "locked" && <p>Finish the previous skill to unlock this one.</p>}
          {state === "available" && (
            <>
              <p>Lesson {done + 1} of {total}</p>
              <button className="btn" style={{ color }} onClick={() => go(`/lesson/${skill.next_lesson_id}`)}>
                Start +10 XP
              </button>
            </>
          )}
          {completed && (
            <>
              <p>Skill complete — all {total} lessons done!</p>
              <button className="btn" style={{ color: "var(--yellow-d)" }} onClick={() => go(`/session/practice?skill=${skill.id}`)}>
                Practice +5 XP
              </button>
              {skill.legendary
                ? <p style={{ margin: "10px 0 0", textAlign: "center" }}>👑 Legendary achieved</p>
                : <button className="btn" style={{ color: "var(--purple-d)" }} onClick={() => go(`/session/legendary?skill=${skill.id}`)}>
                    👑 Legendary
                  </button>}
            </>
          )}
        </div>
      )}
    </div>
  );
}
