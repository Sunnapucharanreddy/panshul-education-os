"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import type { ChatAgent, ChatMessage, ChatResponse } from "@/components/ChatProvider";
import { AgentBadge, RichText } from "@/components/RichText";
import { VideoResults } from "@/components/VideoResults";

export type WorkspaceConfig = {
  agent: "career" | "interview" | "startup";
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  prompts: string[];
  guideTitle: string;
  guideItems: string[];
};

export function AgentWorkspace({ config }: { config: WorkspaceConfig }) {
  const { session } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hydratedKey, setHydratedKey] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [role, setRole] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const storageKey = session ? `panshul.workspace.${config.agent}.${session.userId}` : null;
  const interviewStarted = config.agent === "interview" && messages.some((message) => message.agent === "interview");

  useEffect(() => {
    if (!storageKey) return;
    const selectedSessionId = new URLSearchParams(window.location.search).get("sessionId");
    if (selectedSessionId) {
      setHydratedKey(null);
      setPending(true);
      setError(null);
      api<{
        session_id: string;
        messages: Array<{ id: string; role: "user" | "assistant"; content: string; agent?: string | null }>;
      }>(`/api/v1/chat/sessions/${encodeURIComponent(selectedSessionId)}`)
        .then((data) => {
          setMessages(data.messages.map((message) => ({
            id: message.id,
            role: message.role,
            content: message.content,
            agent: message.agent ?? undefined,
          })));
          setSessionId(data.session_id);
          setHydratedKey(storageKey);
        })
        .catch((err: unknown) => {
          setMessages([]);
          setSessionId(null);
          setError(err instanceof Error ? err.message : "Could not load this conversation.");
          setHydratedKey(storageKey);
        })
        .finally(() => setPending(false));
      return;
    }
    try {
      const saved = JSON.parse(sessionStorage.getItem(storageKey) ?? "{}") as {
        messages?: ChatMessage[];
        sessionId?: string | null;
      };
      setMessages(Array.isArray(saved.messages) ? saved.messages : []);
      setSessionId(typeof saved.sessionId === "string" ? saved.sessionId : null);
    } catch {
      setMessages([]);
      setSessionId(null);
    }
    setHydratedKey(storageKey);
  }, [storageKey]);

  useEffect(() => {
    if (!storageKey || hydratedKey !== storageKey) return;
    try {
      sessionStorage.setItem(storageKey, JSON.stringify({ messages: messages.slice(-40), sessionId }));
    } catch {
      /* The server conversation remains saved if this tab cache is unavailable. */
    }
  }, [hydratedKey, messages, sessionId, storageKey]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  async function send(text: string, agent: ChatAgent = config.agent) {
    const clean = text.trim();
    if (!clean || pending) return;
    setError(null);
    setDraft("");
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: "user", content: clean, agent }]);
    setPending(true);
    try {
      const data = await api<ChatResponse>("/api/v1/chat", {
        method: "POST",
        body: JSON.stringify({ message: clean, session_id: sessionId, agent }),
      });
      setSessionId(data.session_id);
      setMessages((current) => [...current, {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        agent: data.agent,
        videos: data.videos,
        videoSearchStatus: data.video_search_status,
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Panshul could not reply. Please try again.");
    } finally {
      setPending(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (config.agent === "interview" && !interviewStarted) {
      void send(`Start a mock interview for the role of ${role.trim() || "a role I am preparing for"}. Ask one realistic question and wait for my answer. After each answer, give brief feedback on content, structure, and communication, then ask exactly one next question.`);
      return;
    }
    const text = draft.trim();
    if (config.agent === "interview") {
      void send(`My answer to the latest interview question: ${text}. Give brief feedback on content, structure, and communication, then ask exactly one next question.`);
    } else {
      void send(text);
    }
  }

  function reset() {
    setMessages([]);
    setSessionId(null);
    setError(null);
    setDraft("");
  }

  return (
    <section className="page agent-experience">
      <div className="agent-experience-heading">
        <div>
          <p className="kicker">{config.agent} workspace</p>
          <h1>{config.title}</h1>
          <p className="lede">{config.description}</p>
        </div>
        <Link className="btn btn-ghost btn-small" href="/classroom">Dashboard</Link>
      </div>

      <div className="agent-experience-grid">
        <section className="card agent-workspace-card" aria-label={`${config.agent} conversation`}>
          <div className="agent-workspace-topline">
            <div><span className={`agent-pill agent-${config.agent}`}>{config.agent} advisor</span></div>
            <button className="text-btn" type="button" onClick={reset} disabled={pending || messages.length === 0}>New conversation</button>
          </div>

          <div className="agent-thread" aria-live="polite" aria-label="Conversation messages">
            {pending && messages.length === 0 ? <p className="muted" role="status">Loading conversation…</p> : null}
            {messages.length === 0 && !pending ? (
              <div className="agent-empty">
                <span className="tutor-mark" aria-hidden="true">P</span>
                <h2>{config.emptyTitle}</h2>
                <p>{config.emptyDescription}</p>
                {config.agent !== "interview" ? (
                  <div className="tutor-prompts">
                    {config.prompts.map((prompt) => (
                      <button className="chip" key={prompt} type="button" disabled={pending} onClick={() => void send(prompt)}>{prompt}</button>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : messages.map((message) => (
              <article key={message.id} className={`tutor-message ${message.role === "user" ? "tutor-user" : "tutor-assistant"}`}>
                <div className="tutor-message-label">{message.role === "user" ? "You" : <><span className="mini-mark">P</span> Panshul</>}</div>
                {message.role === "assistant" ? <AgentBadge agent={message.agent} /> : null}
                <div className="tutor-message-body"><RichText text={message.content} /></div>
                {message.role === "assistant" ? <VideoResults videos={message.videos} status={message.videoSearchStatus} /> : null}
              </article>
            ))}
            {pending ? <div className="tutor-thinking" role="status"><span className="thinking-dots" /> Panshul is thinking…</div> : null}
            <div ref={endRef} />
          </div>

          {error ? <p className="error agent-workspace-error" role="alert">{error}</p> : null}
          <form className="agent-workspace-composer" onSubmit={submit}>
            {config.agent === "interview" && !interviewStarted ? (
              <label className="field agent-role-field"><span>Interview role</span><input value={role} onChange={(event) => setRole(event.target.value)} maxLength={120} placeholder="e.g. Junior software developer" /></label>
            ) : null}
            <label className="sr-only" htmlFor={`${config.agent}-message`}>
              {config.agent === "interview" && !interviewStarted ? "Start mock interview" : "Your message"}
            </label>
            {!(config.agent === "interview" && !interviewStarted) ? (
              <textarea id={`${config.agent}-message`} rows={3} maxLength={4000} value={draft} onChange={(event) => setDraft(event.target.value)} disabled={pending} placeholder={config.agent === "interview" ? "Answer the latest interview question…" : `Message your ${config.agent} advisor…`} />
            ) : null}
            <div className="agent-composer-footer">
              <span className="muted">Your conversation is saved to your Panshul session.</span>
              <button className="btn btn-primary btn-small" type="submit" disabled={pending || (config.agent === "interview" ? !interviewStarted && !role.trim() : !draft.trim())}>
                {pending ? "Sending…" : config.agent === "interview" && !interviewStarted ? "Start interview" : "Send"}
              </button>
            </div>
          </form>
        </section>

        <aside className="card agent-guide-card">
          <p className="kicker">Your session</p>
          <h2>{config.guideTitle}</h2>
          <ul className="agent-guide-list">{config.guideItems.map((item) => <li key={item}>{item}</li>)}</ul>
          <p className="help">Panshul responds using its existing {config.agent} agent. You can ask follow-up questions at any time.</p>
        </aside>
      </div>
    </section>
  );
}
