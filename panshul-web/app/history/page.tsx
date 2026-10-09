"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { RequireAuth } from "@/components/RequireAuth";

type Conversation = {
  session_id: string;
  created_at: string;
  updated_at: string;
  agent: string;
  title: string;
  preview: string;
  message_count: number;
};
type SessionList = { items: Conversation[]; limit: number; offset: number; has_more: boolean };

const WORKSPACE: Record<string, string> = {
  career: "/career",
  interview: "/interview",
  startup: "/startup",
  teacher: "/tutor",
  quiz: "/tutor",
  youtube: "/tutor",
};

function dayLabel(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Earlier";
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "long" }).format(date);
}

function HistoryContent() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load(start: number, append: boolean) {
    append ? setLoadingMore(true) : setLoading(true);
    setError(null);
    try {
      const data = await api<SessionList>(`/api/v1/chat/sessions?limit=30&offset=${start}`);
      setItems((current) => append ? [...current, ...data.items] : data.items);
      setOffset(start + data.items.length);
      setHasMore(data.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load chat history.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }

  useEffect(() => { void load(0, false); }, []);

  const groups = useMemo(() => {
    const grouped = new Map<string, Conversation[]>();
    for (const item of items) {
      const key = dayLabel(item.updated_at || item.created_at);
      grouped.set(key, [...(grouped.get(key) ?? []), item]);
    }
    return [...grouped.entries()];
  }, [items]);

  return (
    <div className="page">
      <p className="kicker">Your learning record</p>
      <h1>Chat history</h1>
      <p className="lede">Return to a previous tutoring, career, interview, or startup conversation.</p>
      {error ? <div className="error" role="alert">{error}<button className="text-btn" type="button" onClick={() => void load(0, false)}>Try again</button></div> : null}
      {loading ? <p className="muted" role="status">Loading your conversations…</p> : null}
      {!loading && !error && items.length === 0 ? (
        <div className="card history-empty"><h2>No conversations yet</h2><p>Your saved AI conversations will appear here after the first successful reply.</p><Link className="btn btn-primary" href="/tutor">Ask the tutor</Link></div>
      ) : null}
      {!loading && groups.map(([day, conversations]) => (
        <section className="section history-group" key={day}>
          <h2>{day}</h2>
          <div className="history-list">
            {conversations.map((conversation) => {
              const href = WORKSPACE[conversation.agent] ?? "/tutor";
              return (
                <Link className="card history-item" key={conversation.session_id} href={`${href}?sessionId=${encodeURIComponent(conversation.session_id)}`}>
                  <div className="history-item-heading"><span className={`agent-pill agent-${conversation.agent}`}>{conversation.agent || "teacher"}</span><time dateTime={conversation.updated_at}>{new Date(conversation.updated_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</time></div>
                  <h3>{conversation.title}</h3>
                  <p>{conversation.preview || "No message preview available."}</p>
                  <small>{conversation.message_count} messages · Continue conversation →</small>
                </Link>
              );
            })}
          </div>
        </section>
      ))}
      {hasMore ? <button type="button" className="btn" disabled={loadingMore} onClick={() => void load(offset, true)}>{loadingMore ? "Loading…" : "Load older conversations"}</button> : null}
    </div>
  );
}

export default function HistoryPage() {
  return <RequireAuth><HistoryContent /></RequireAuth>;
}
