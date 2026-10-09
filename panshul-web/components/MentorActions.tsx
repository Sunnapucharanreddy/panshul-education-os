"use client";

import { MENTORS } from "@/lib/mentors";
import Link from "next/link";

const ROUTES: Record<(typeof MENTORS)[number]["id"], string> = {
  teacher: "/tutor",
  quiz: "/quiz",
  career: "/career",
  interview: "/interview",
  startup: "/startup",
};

export function MentorActions() {
  return (
    <div className="mentor-grid">
      {MENTORS.map((mentor) => (
        <Link key={mentor.id} href={ROUTES[mentor.id]} className="mentor-card">
          <span className={`agent-pill agent-${mentor.id}`}>{mentor.title}</span>
          <strong>{mentor.headline}</strong>
          <p>{mentor.line}</p>
          <span className="mentor-go">Open {mentor.title}</span>
        </Link>
      ))}
    </div>
  );
}
