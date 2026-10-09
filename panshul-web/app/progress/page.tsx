"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ProgressList, type TopicProgress } from "@/components/ProgressList";
import { RequireAuth } from "@/components/RequireAuth";

export default function ProgressPage() {
  return (
    <div className="page">
      <p className="kicker">Progress</p>
      <h1>What you have practiced.</h1>
      <p className="lede">Average score for each topic, from quizzes you submitted.</p>
      <div className="section">
        <RequireAuth>
          <ProgressReport />
        </RequireAuth>
      </div>
    </div>
  );
}

function ProgressReport() {
  const [topics, setTopics] = useState<TopicProgress[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api<{ topics: TopicProgress[] }>("/api/v1/quiz/progress")
      .then((data) => { if (!cancelled) setTopics(data.topics ?? []); })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not load progress.");
      });
    return () => { cancelled = true; };
  }, []);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!topics) return <p className="muted">Loading scores…</p>;

  return (
    <div className="card">
      <ProgressList topics={topics} />
      <div className="row">
        <Link href="/quiz" className="btn btn-primary">Practice another topic</Link>
      </div>
    </div>
  );
}
