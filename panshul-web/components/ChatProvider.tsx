"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { startRecorder } from "@/lib/record";
import { useAuth } from "@/components/AuthProvider";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  videos?: VideoResult[];
  videoSearchStatus?: "success" | "no_results" | "unavailable" | "topic_required";
};

export type ChatAgent = "teacher" | "quiz" | "career" | "interview" | "startup";

export type VideoResult = {
  video_id: string;
  title: string;
  channel_title: string | null;
  thumbnail_url: string | null;
  url: string;
};

export type ChatResponse = {
  session_id: string;
  agent: string;
  response: string;
  videos?: VideoResult[];
  video_search_status?: ChatMessage["videoSearchStatus"];
  transcript?: string;
  audio_base64?: string;
};

type ChatValue = {
  messages: ChatMessage[];
  draft: string;
  setDraft: (value: string) => void;
  pending: boolean;
  recording: boolean;
  error: string | null;
  open: boolean;
  setOpen: (open: boolean) => void;
  send: (text?: string, agent?: ChatAgent) => Promise<void>;
  ask: (text: string) => void;
  toggleRecording: () => Promise<void>;
  reset: () => void;
  loadSession: (sessionId: string) => Promise<void>;
};

const ChatContext = createContext<ChatValue | null>(null);
const MESSAGES_KEY = "panshul.chatMessages";
const SESSION_KEY = "panshul.chatSession";
const OWNER_KEY = "panshul.chatOwner";

function uid() {
  return crypto.randomUUID();
}

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { ready: authReady, session } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [loadedOwner, setLoadedOwner] = useState<string | null>(null);
  const recorder = useRef<{ stop: () => Promise<Blob> } | null>(null);

  useEffect(() => {
    if (!authReady) return;
    setHydrated(false);
    setLoadedOwner(null);
    if (!session) {
      setMessages([]);
      setSessionId(null);
      sessionStorage.removeItem(MESSAGES_KEY);
      sessionStorage.removeItem(SESSION_KEY);
      sessionStorage.removeItem(OWNER_KEY);
      setHydrated(true);
      return;
    }
    try {
      if (sessionStorage.getItem(OWNER_KEY) === session.userId) {
        const stored = sessionStorage.getItem(MESSAGES_KEY);
        if (stored) setMessages(JSON.parse(stored) as ChatMessage[]);
        setSessionId(sessionStorage.getItem(SESSION_KEY));
      } else {
        setMessages([]);
        setSessionId(null);
        sessionStorage.removeItem(MESSAGES_KEY);
        sessionStorage.removeItem(SESSION_KEY);
      }
      sessionStorage.setItem(OWNER_KEY, session.userId);
    } catch {
      /* ignore a broken tab cache */
    }
    setLoadedOwner(session.userId);
    setHydrated(true);
  }, [authReady, session]);

  useEffect(() => {
    if (!hydrated || !session || loadedOwner !== session.userId) return;
    sessionStorage.setItem(MESSAGES_KEY, JSON.stringify(messages.slice(-40)));
    sessionStorage.setItem(OWNER_KEY, session.userId);
    if (sessionId) sessionStorage.setItem(SESSION_KEY, sessionId);
    else sessionStorage.removeItem(SESSION_KEY);
  }, [messages, sessionId, hydrated, loadedOwner, session]);

  const loadSession = useCallback(async (selectedSessionId: string) => {
    if (!session) return;
    setPending(true);
    setError(null);
    try {
      const data = await api<{
        session_id: string;
        messages: Array<{ id: string; role: "user" | "assistant"; content: string; agent?: string | null }>;
      }>(`/api/v1/chat/sessions/${encodeURIComponent(selectedSessionId)}`);
      setMessages(data.messages.map((message) => ({
        id: message.id,
        role: message.role,
        content: message.content,
        agent: message.agent ?? undefined,
      })));
      setSessionId(data.session_id);
      setOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load this conversation.");
    } finally {
      setPending(false);
    }
  }, [session]);

  const send = useCallback(async (text?: string, agent?: ChatAgent) => {
    const message = (text ?? draft).trim();
    if (!message || pending) return;
    setOpen(true);
    if (!session) {
      setDraft(message);
      setError("Sign in with your phone to talk to Panshul.");
      return;
    }
    if (message.length > 4000) {
      setError("Keep a message under 4,000 characters.");
      return;
    }
    setError(null);
    setDraft("");
    setMessages((current) => [...current, { id: uid(), role: "user", content: message }]);
    setPending(true);
    try {
      const data = await api<ChatResponse>("/api/v1/chat", {
        method: "POST",
        body: JSON.stringify({ message, session_id: sessionId, agent }),
      });
      setSessionId(data.session_id);
      setMessages((current) => [
        ...current,
        {
          id: uid(),
          role: "assistant",
          content: data.response,
          agent: data.agent,
          videos: data.videos,
          videoSearchStatus: data.video_search_status,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The mentor could not reply.");
    } finally {
      setPending(false);
    }
  }, [draft, pending, session, sessionId]);

  const ask = useCallback((text: string) => {
    void send(text);
  }, [send]);

  const playAudio = (base64?: string) => {
    if (!base64) return;
    const audio = new Audio(`data:audio/wav;base64,${base64}`);
    void audio.play().catch(() => undefined);
  };

  const toggleRecording = useCallback(async () => {
    if (!session) {
      setOpen(true);
      setError("Sign in with your phone to talk to Panshul.");
      return;
    }
    if (recorder.current) {
      const handle = recorder.current;
      recorder.current = null;
      setRecording(false);
      setPending(true);
      setError(null);
      try {
        const blob = await handle.stop();
        const body = new FormData();
        body.append("audio", blob, "speech.wav");
        if (sessionId) body.append("session_id", sessionId);
        const data = await api<ChatResponse>("/api/v1/voice/converse", { method: "POST", body });
        setSessionId(data.session_id);
        const heard = data.transcript?.trim() || "Voice message";
        setMessages((current) => [
          ...current,
          { id: uid(), role: "user", content: heard },
          { id: uid(), role: "assistant", content: data.response, agent: data.agent },
        ]);
        playAudio(data.audio_base64);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Voice could not be sent.");
      } finally {
        setPending(false);
      }
      return;
    }
    try {
      recorder.current = await startRecorder();
      setRecording(true);
      setError(null);
      setOpen(true);
    } catch {
      setError("Allow the microphone, then try the voice button again.");
    }
  }, [session, sessionId]);

  const reset = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    setDraft("");
  }, []);

  const value: ChatValue = {
    messages, draft, setDraft, pending, recording, error, open, setOpen, send, ask, toggleRecording, reset, loadSession,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const value = useContext(ChatContext);
  if (!value) throw new Error("useChat must be used inside ChatProvider");
  return value;
}
