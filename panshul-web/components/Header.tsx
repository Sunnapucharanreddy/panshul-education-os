"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { maskPhone } from "@/lib/phone";

const LINKS = [
  ["/#about", "About"],
  ["/#mentors", "Features"],
  ["/#help", "Help"],
  ["/classroom", "Classroom"],
  ["/tutor", "AI Tutor"],
  ["/quiz", "Quiz"],
  ["/career", "Career"],
  ["/interview", "Interview"],
  ["/startup", "Startup"],
  ["/progress", "Progress"],
  ["/history", "Chat history"],
];

export function Header() {
  const pathname = usePathname();
  const { session, signOut } = useAuth();

  return (
    <header className="topbar">
      <Link href="/" className="brand" aria-label="Panshul home">
        <span className="brand-mark" aria-hidden="true">P</span>
        <span>
          <strong>PANSHUL</strong>
          <small>Sathi Seva</small>
        </span>
      </Link>
      <nav className="nav" aria-label="Primary">
        {LINKS.map(([href, label]) => (
          <Link key={href} href={href} className={pathname === href ? "is-active" : undefined} aria-current={pathname === href ? "page" : undefined}>
            {label}
          </Link>
        ))}
      </nav>
      <div className="top-actions">
        {session ? (
          <>
            <span className="who">{maskPhone(session.phone)}</span>
            <button type="button" className="btn btn-ghost btn-small" onClick={signOut}>Sign out</button>
          </>
        ) : (
          <Link href="/login" className="btn btn-primary btn-small">Sign in</Link>
        )}
      </div>
    </header>
  );
}
