"use client";
import { useEffect, useState } from "react";
import SkillNode from "@/components/SkillNode";
import { useToast } from "@/components/ui";
import { api } from "@/lib/api";
import type { UnitData } from "@/lib/types";
import { useUser } from "@/lib/user-context";

// Horizontal wiggle (px) that gives the path its winding look.
const OFFSETS = [0, -42, -66, -42, 0, 42, 66, 42];

export default function LearnPage() {
  const [units, setUnits] = useState<UnitData[] | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const { refresh } = useUser();
  const toast = useToast();

  useEffect(() => {
    api.path().then((p) => setUnits(p.units)).catch(() => setUnits([]));
    refresh();   // pick up streak/hearts changed elsewhere
  }, [refresh]);

  if (!units) return <div className="loading">Loading your path…</div>;

  return (
    <div className="page" onClick={() => setOpenId(null)}>
      {units.map((unit) => (
        <section key={unit.id}>
          <div className="unit-banner" style={{ background: unit.color }}>
            <div>
              <div className="kicker">Section 1, Unit {unit.position}</div>
              <h2>{unit.title}</h2>
              <p className="native">{unit.description}</p>
            </div>
            <button className="banner-btn" onClick={(e) => { e.stopPropagation(); toast({ icon: "📖", title: "Guidebook", text: "Coming soon!" }); }}>
              📖 Guide
            </button>
          </div>
          <div className="path">
            {unit.skills.map((skill, i) => (
              // stop propagation so clicking a node doesn't immediately close its own popover
              <div key={skill.id} onClick={(e) => e.stopPropagation()} style={{ position: "relative", zIndex: openId === skill.id ? 20 : 1 }}>
                <SkillNode skill={skill} color={unit.color} offset={OFFSETS[i % OFFSETS.length]}
                  open={openId === skill.id}
                  onToggle={() => setOpenId(openId === skill.id ? null : skill.id)}
                  onClose={() => setOpenId(null)} />
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
