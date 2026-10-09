import { clearSession, readAccess, readRefresh, writeAccess } from "@/lib/session";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.message === "string") return data.message;
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail) && typeof data.detail[0]?.msg === "string") {
      return data.detail[0].msg;
    }
  } catch {
    /* response was not JSON */
  }
  return `Request failed (${res.status})`;
}

async function refreshAccess(): Promise<boolean> {
  const refresh = readRefresh();
  if (!refresh) return false;
  let res: Response;
  try {
    res = await fetch("/backend/api/v1/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
  } catch {
    return false;
  }
  if (!res.ok) {
    clearSession();
    return false;
  }
  const data = (await res.json()) as { access_token?: string };
  if (!data.access_token) {
    clearSession();
    return false;
  }
  writeAccess(data.access_token);
  return true;
}

export async function api<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  const token = readAccess();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (typeof init.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(`/backend${path}`, { ...init, headers });
  } catch {
    throw new ApiError("Cannot reach Panshul. Start the API, then try again.", 0);
  }

  if (res.status === 401 && retry && readRefresh()) {
    const ok = await refreshAccess();
    if (ok) return api<T>(path, init, false);
    throw new ApiError("Your session expired. Sign in again.", 401);
  }

  if (!res.ok) throw new ApiError(await readError(res), res.status);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
