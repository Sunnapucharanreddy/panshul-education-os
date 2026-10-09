"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import { MentorActions } from "@/components/MentorActions";
import { ProgressList, type TopicProgress } from "@/components/ProgressList";
import { RequireAuth } from "@/components/RequireAuth";

export default function ClassroomPage() {
  return <RequireAuth><ClassroomDashboard /></RequireAuth>;
}

function ClassroomDashboard() {
  const { session, dismissWelcome } = useAuth();
  const [topics, setTopics] = useState<TopicProgress[] | null>(null);

  useEffect(() => {
    if (!session) {
      setTopics(null);
      return;
    }
    let cancelled = false;
    api<{ topics: TopicProgress[] }>("/api/v1/quiz/progress")
      .then((data) => { if (!cancelled) setTopics(data.topics ?? []); })
      .catch(() => { if (!cancelled) setTopics([]); });
    return () => { cancelled = true; };
  }, [session]);

  return (
    <div className="page">
      <p className="kicker">Classroom</p>
      <h1>Pick a starting point, or type your own.</h1>
      <p className="lede">
        Choose a focused workspace for tutoring, scored quiz practice, career planning,
        interview preparation, or startup guidance.
      </p>

      {session?.isNewUser ? (
        <div className="card" style={{ marginTop: 22 }}>
          <strong>Welcome. Tell Sathi your class and what you want to learn.</strong>
          <p className="help">That first message gives the teacher something to adapt to.</p>
          <button type="button" className="btn btn-small" style={{ marginTop: 12 }} onClick={dismissWelcome}>
            Got it
          </button>
        </div>
      ) : null}

      <div className="section">
        <MentorActions />
      </div>

      <section className="section split">
        <div className="card">
          <p className="kicker">Scores</p>
          <h2>Progress by topic</h2>
          {session ? (
            topics ? <ProgressList topics={topics} /> : <p className="muted">Loading scores…</p>
          ) : (
            <p className="muted">Sign in to see quiz scores saved on your account.</p>
          )}
          <div className="row">
            <Link href="/quiz" className="btn btn-leaf">New quiz</Link>
            <Link href="/progress" className="btn">Full progress</Link>
          </div>
        </div>
        <div className="card">
          <p className="kicker">Voice</p>
          <h2>Speak the question.</h2>
          <p className="lede">
            The mic in Sathi records a short clip, sends it to the voice API, and plays the spoken answer back.
          </p>
        </div>
      </section>
    </div>
  );
}
