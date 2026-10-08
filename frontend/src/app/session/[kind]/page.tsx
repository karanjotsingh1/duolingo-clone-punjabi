"use client";
// /session/practice | /session/timed | /session/legendary?skill=ID
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import LessonPlayer from "@/components/LessonPlayer";

function Inner({ kind }: { kind: string }) {
  const skill = useSearchParams().get("skill");
  const k = (["practice", "timed", "legendary"].includes(kind) ? kind : "practice") as "practice" | "timed" | "legendary";
  return <LessonPlayer source={{ kind: k, skillId: skill ? Number(skill) : undefined }} />;
}

export default function SessionPage({ params }: { params: { kind: string } }) {
  return <Suspense fallback={null}><Inner kind={params.kind} /></Suspense>;
}
