import { Suspense } from "react";
import { LoginForm } from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="login-wrap"><p className="muted">Loading sign-in…</p></div>}>
      <LoginForm />
    </Suspense>
  );
}
