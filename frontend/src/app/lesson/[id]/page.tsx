"use client";
import LessonPlayer from "@/components/LessonPlayer";

export default function LessonPage({ params }: { params: { id: string } }) {
  return <LessonPlayer source={{ kind: "lesson", id: Number(params.id) }} />;
}
