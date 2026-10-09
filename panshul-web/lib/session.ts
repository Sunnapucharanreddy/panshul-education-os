export type Session = {
  accessToken: string;
  refreshToken: string;
  userId: string;
  phone: string;
  isNewUser: boolean;
};

const KEY = "panshul.session";

const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((listener) => listener());
}

export function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function loadSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  try {
    const data = JSON.parse(raw) as Session;
    if (!data.accessToken || !data.refreshToken || !data.userId) return null;
    return data;
  } catch {
    return null;
  }
}

export function saveSession(session: Session) {
  localStorage.setItem(KEY, JSON.stringify(session));
  emit();
}

export function clearSession() {
  localStorage.removeItem(KEY);
  emit();
}

export function writeAccess(token: string) {
  const current = loadSession();
  if (!current) return;
  current.accessToken = token;
  localStorage.setItem(KEY, JSON.stringify(current));
}

export function markReturning() {
  const current = loadSession();
  if (!current || !current.isNewUser) return;
  current.isNewUser = false;
  localStorage.setItem(KEY, JSON.stringify(current));
  emit();
}

export function readAccess() {
  return loadSession()?.accessToken ?? null;
}

export function readRefresh() {
  return loadSession()?.refreshToken ?? null;
}
