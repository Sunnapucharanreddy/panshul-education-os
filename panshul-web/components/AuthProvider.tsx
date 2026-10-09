"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { clearSession, loadSession, markReturning, saveSession, subscribe, type Session } from "@/lib/session";

type AuthValue = {
  ready: boolean;
  session: Session | null;
  signIn: (session: Session) => void;
  signOut: () => void;
  dismissWelcome: () => void;
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setSession(loadSession());
    setReady(true);
    return subscribe(() => setSession(loadSession()));
  }, []);

  const value: AuthValue = {
    ready,
    session,
    signIn: saveSession,
    signOut: clearSession,
    dismissWelcome: markReturning,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
