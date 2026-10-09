"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { ready, session } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  useEffect(() => {
    if (ready && !session) router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [ready, session, pathname, router]);
  if (!ready) return <p className="muted">Loading your session…</p>;
  if (!session) {
    return (
      <p className="muted" role="status">Taking you to sign in… <Link href={`/login?next=${encodeURIComponent(pathname)}`}>Continue</Link></p>
    );
  }
  return children;
}
