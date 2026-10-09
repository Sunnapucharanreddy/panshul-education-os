import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const HOP_BY_HOP = ["connection", "keep-alive", "transfer-encoding", "upgrade", "host"];

function backendBase() {
  return (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

function allowed(path: string[]) {
  if (path.some((part) => part === ".." || part.includes("\\"))) return false;
  const joined = path.join("/");
  return joined === "health" || joined.startsWith("api/v1/");
}

async function proxy(req: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  if (!allowed(path)) {
    return NextResponse.json({ message: "Not found" }, { status: 404 });
  }

  const incoming = new URL(req.url);
  const target = `${backendBase()}/${path.join("/")}${incoming.search}`;
  const headers = new Headers(req.headers);
  for (const name of HOP_BY_HOP) headers.delete(name);

  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  try {
    const upstream = await fetch(target, {
      method: req.method,
      headers,
      body: hasBody ? await req.arrayBuffer() : undefined,
      redirect: "manual",
      signal: AbortSignal.timeout(130_000),
    });
    const out = new Headers(upstream.headers);
    for (const name of ["content-encoding", "content-length", "transfer-encoding", "connection"]) {
      out.delete(name);
    }
    return new Response(upstream.body, { status: upstream.status, headers: out });
  } catch {
    return NextResponse.json(
      { error: "backend_unreachable", message: "Panshul API is not running." },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
