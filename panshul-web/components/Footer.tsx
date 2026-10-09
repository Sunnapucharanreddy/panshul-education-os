"use client";

import { useEffect, useState } from "react";

export function Footer() {
  const [state, setState] = useState<"checking" | "ok" | "down">("checking");

  useEffect(() => {
    let cancelled = false;
    fetch("/backend/health")
      .then((res) => (res.ok ? setState("ok") : setState("down")))
      .catch(() => { if (!cancelled) setState("down"); });
    return () => { cancelled = true; };
  }, []);

  const label = state === "ok" ? "API connected" : state === "down" ? "API offline" : "Checking API";

  return (
    <footer className="footer">
      <span>Panshul Education OS</span>
      <span className="status">
        <span className={`status-dot ${state === "ok" ? "is-ok" : state === "down" ? "is-down" : ""}`} />
        {label}
      </span>
    </footer>
  );
}
