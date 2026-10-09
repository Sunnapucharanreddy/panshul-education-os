"use client";

import { FormEvent, useEffect, useRef } from "react";
import Link from "next/link";
import { RequireAuth } from "@/components/RequireAuth";
import { useChat } from "@/components/ChatProvider";
import { AgentBadge, RichText } from "@/components/RichText";
import { VideoResults } from "@/components/VideoResults";

const PROMPTS = [
  "Explain photosynthesis in simple terms.",
  "Help me understand how fractions work.",
  "Why do objects fall at the same rate in a vacuum?",
];

export default function TutorPage() {
  return <RequireAuth><TutorExperience /></RequireAuth>;
}

function TutorExperience() {
  const chat = useChat();
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sessionId = new URLSearchParams(window.location.search).get("sessionId");
    if (sessionId) void chat.loadSession(sessionId);
  }, [chat.loadSession]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chat.messages, chat.pending]);

  function submit(event: FormEvent) {
    event.preventDefault();
    void chat.send(undefined, "teacher");
  }

  return (
    <section className="page tutor-page">
      <div className="tutor-heading">
        <div>
          <p className="kicker">AI tutor</p>
          <h1>Your study partner, ready when you are.</h1>
          <p className="lede">Ask a question in your own words. Panshul will route it to the right learning mentor.</p>
        </div>
        <div className="tutor-actions">
          <button className="btn btn-ghost" type="button" onClick={chat.reset} disabled={chat.pending}>New chat</button>
          <Link className="btn btn-small" href="/classroom">Dashboard</Link>
        </div>
      </div>

      <div className="tutor-shell card">
        <div className="tutor-transcript" aria-live="polite" aria-label="Conversation">
          {chat.messages.length === 0 ? (
            <div className="tutor-empty">
              <span className="tutor-mark" aria-hidden="true">P</span>
              <h2>What would you like to learn?</h2>
              <p>Try a question below, or write your own in the message box.</p>
              <div className="tutor-prompts">
                {PROMPTS.map((prompt) => <button key={prompt} className="chip" type="button" onClick={() => void chat.send(prompt, "teacher")}>{prompt}</button>)}
              </div>
            </div>
          ) : chat.messages.map((message) => (
            <article key={message.id} className={`tutor-message ${message.role === "user" ? "tutor-user" : "tutor-assistant"}`}>
              <div className="tutor-message-label">{message.role === "user" ? "You" : <><span className="mini-mark">P</span> Panshul</>}</div>
              {message.role === "assistant" ? <AgentBadge agent={message.agent} /> : null}
              <div className="tutor-message-body"><RichText text={message.content} /></div>
              {message.role === "assistant" ? <VideoResults videos={message.videos} status={message.videoSearchStatus} /> : null}
            </article>
          ))}
          {chat.pending ? <div className="tutor-thinking" role="status"><span className="thinking-dots" /> Panshul is thinking…</div> : null}
          <div ref={bottom} />
        </div>

        {chat.error ? <p className="error tutor-error" role="alert">{chat.error}</p> : null}

        <form className="tutor-composer" onSubmit={submit}>
          <label className="sr-only" htmlFor="tutor-message">Your question</label>
          <textarea id="tutor-message" value={chat.draft} rows={2} maxLength={4000} placeholder="Ask anything you are learning…" disabled={chat.pending || chat.recording} onChange={(event) => chat.setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void chat.send(undefined, "teacher"); } }} />
          <div className="tutor-composer-footer">
            <span className="muted">AI can make mistakes. Check important work.</span>
            <div className="tutor-compose-actions">
              <button type="button" className={`btn btn-small ${chat.recording ? "btn-recording" : "btn-ghost"}`} onClick={() => void chat.toggleRecording()} disabled={chat.pending} aria-pressed={chat.recording} aria-label={chat.recording ? "Stop recording and send" : "Record a voice question"}>
                {chat.recording ? "Stop recording" : "Voice"}
              </button>
              <button type="submit" className="btn btn-primary btn-small" disabled={chat.pending || chat.recording || !chat.draft.trim()}>{chat.pending ? "Thinking…" : "Send question"}</button>
            </div>
          </div>
        </form>
      </div>
    </section>
  );
}
