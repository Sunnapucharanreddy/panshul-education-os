"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { useChat } from "@/components/ChatProvider";
import { AgentBadge, RichText } from "@/components/RichText";
import { VideoResults } from "@/components/VideoResults";
import { MENTORS } from "@/lib/mentors";

const STARTERS = [
  { id: "teacher", label: "Photosynthesis" },
  { id: "quiz", label: "Fractions" },
  { id: "career", label: "After class 12" },
] as const;

export function SideBot() {
  const pathname = usePathname();
  const hide = pathname === "/login" || pathname === "/tutor";
  const { session } = useAuth();
  const chat = useChat();
  const endRef = useRef<HTMLDivElement>(null);
  const [narrow, setNarrow] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(max-width: 1100px)");
    const apply = () => setNarrow(query.matches);
    apply();
    query.addEventListener("change", apply);
    return () => query.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [chat.messages, chat.pending]);

  useEffect(() => {
    if (!narrow || !chat.open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") chat.setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [narrow, chat]);

  useEffect(() => {
    document.body.classList.toggle("no-bot", hide);
    return () => document.body.classList.remove("no-bot");
  }, [hide]);

  const shown = !narrow || chat.open;
  if (hide) return null;

  return (
    <>
      {narrow && chat.open ? (
        <button type="button" className="backdrop" aria-label="Close mentor" onClick={() => chat.setOpen(false)} />
      ) : null}
      <aside className={`bot ${chat.open ? "is-open" : ""}`} aria-hidden={!shown} hidden={!shown && narrow}>
        <div className="bot-head">
          <p className="bot-title">Sathi</p>
          <div className="bot-tools">
            <button type="button" className="text-btn" onClick={chat.reset}>New</button>
            <button type="button" className="text-btn bot-close" onClick={() => chat.setOpen(false)}>Close</button>
          </div>
        </div>

        <div className="bot-messages" aria-live="polite">
          {chat.messages.length === 0 ? (
            <div className="empty-bot">
              <p>Start with a question.</p>
              <div className="starters">
                {STARTERS.map((starter) => {
                  const mentor = MENTORS.find((item) => item.id === starter.id);
                  if (!mentor) return null;
                  return (
                    <button key={starter.id} type="button" className="starter" onClick={() => chat.ask(mentor.prompt)}>
                      <span>{mentor.title}</span>
                      {starter.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            chat.messages.map((message) => (
              <article key={message.id} className={`bubble ${message.role === "user" ? "bubble-user" : "bubble-bot"}`}>
                {message.role === "assistant" ? <AgentBadge agent={message.agent} /> : null}
                <RichText text={message.content} />
                {message.role === "assistant" ? <VideoResults videos={message.videos} status={message.videoSearchStatus} /> : null}
              </article>
            ))
          )}
          {chat.pending ? <p className="pending">Thinking…</p> : null}
          {chat.recording ? <p className="pending">Listening. Tap the mic to send.</p> : null}
          <div ref={endRef} />
        </div>

        {chat.error ? <p className="error" role="alert">{chat.error}</p> : null}
        {!session ? (
          <p className="notice">
            <Link href="/login">Sign in</Link> to continue.
          </p>
        ) : null}

        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            void chat.send();
          }}
        >
          <div className="composer-box">
            <button
              type="button"
              className="mic-btn"
              aria-pressed={chat.recording}
              aria-label={chat.recording ? "Stop and send voice" : "Record a voice message"}
              disabled={chat.pending}
              onClick={() => void chat.toggleRecording()}
            >
              {chat.recording ? "Stop" : (
                <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
                  <path fill="currentColor" d="M8 1.2a2.3 2.3 0 0 0-2.3 2.3v4a2.3 2.3 0 1 0 4.6 0v-4A2.3 2.3 0 0 0 8 1.2Zm3.2 6.3a3.2 3.2 0 0 1-6.4 0H3.5a4.5 4.5 0 0 0 3.9 4.45V14H6.2v1.2h3.6V14H8.6v-2.05A4.5 4.5 0 0 0 12.5 7.5h-1.3Z" />
                </svg>
              )}
            </button>
            <label className="sr-only" htmlFor="sathi-draft">Message</label>
            <textarea
              id="sathi-draft"
              rows={1}
              maxLength={4000}
              placeholder="Message"
              value={chat.draft}
              onChange={(event) => chat.setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void chat.send();
                }
              }}
            />
            <button type="submit" className="send-btn" disabled={chat.pending || chat.recording}>
              Send
            </button>
          </div>
        </form>
      </aside>
      {narrow ? (
        <button type="button" className="launcher btn btn-primary" onClick={() => chat.setOpen(true)}>
          Ask Panshul
        </button>
      ) : null}
    </>
  );
}
