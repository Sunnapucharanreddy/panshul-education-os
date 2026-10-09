"use client";

import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { safeNext, toE164 } from "@/lib/phone";
import { useAuth } from "@/components/AuthProvider";

type TokenPair = {
  access_token: string;
  refresh_token: string;
  user_id: string;
  is_new_user: boolean;
};

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { session, signIn } = useAuth();
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const next = safeNext(params.get("next"));
  const showDevHint = process.env.NEXT_PUBLIC_DEV_OTP_HINT === "1";

  async function requestCode(event?: FormEvent) {
    event?.preventDefault();
    const e164 = toE164(phone);
    if (!e164) {
      setError("Use a mobile number, for example 9876543210 or +919876543210.");
      return;
    }
    setPhone(e164);
    setPending(true);
    setError(null);
    try {
      await api("/api/v1/auth/otp/request", {
        method: "POST",
        body: JSON.stringify({ phone: e164 }),
      });
      setStep("otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send the code.");
    } finally {
      setPending(false);
    }
  }

  async function verify(event: FormEvent) {
    event.preventDefault();
    if (!/^\d{6}$/.test(otp)) {
      setError("Enter the 6-digit code.");
      return;
    }
    setPending(true);
    setError(null);
    try {
      const tokens = await api<TokenPair>("/api/v1/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ phone, otp }),
      });
      signIn({
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        userId: tokens.user_id,
        phone,
        isNewUser: tokens.is_new_user,
      });
      router.push(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "That code was not accepted.");
    } finally {
      setPending(false);
    }
  }

  if (session) {
    return (
      <div className="login-wrap">
        <div className="login-card">
          <p className="kicker">Signed in</p>
          <h1>You are already in.</h1>
          <div className="row">
            <a className="btn btn-primary" href="/classroom">Go to the classroom</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <p className="kicker">Phone sign-in</p>
        <h1>{step === "phone" ? "Get a code." : "Enter the code."}</h1>
        <p className="lede">
          {step === "phone"
            ? "Panshul creates your account the first time the code checks out."
            : `Sent to ${phone}. It expires in 5 minutes.`}
        </p>

        {step === "phone" ? (
          <form onSubmit={requestCode}>
            <label className="field">
              <span>Mobile number</span>
              <input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                inputMode="tel"
                autoComplete="tel"
                placeholder="98765 43210"
                required
              />
            </label>
            <div className="stack">
              <button type="submit" className="btn btn-primary" disabled={pending}>
                {pending ? "Sending…" : "Send code"}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={verify}>
            <label className="field">
              <span>6-digit code</span>
              <input
                value={otp}
                onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))}
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="000000"
                required
              />
            </label>
            {showDevHint ? (
              <p className="help">Local API logs the code when SMS is set to console. Check the backend terminal.</p>
            ) : null}
            <div className="stack">
              <button type="submit" className="btn btn-primary" disabled={pending}>
                {pending ? "Checking…" : "Verify and continue"}
              </button>
              <button type="button" className="btn btn-ghost" disabled={pending} onClick={() => void requestCode()}>
                Send a new code
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => { setStep("phone"); setOtp(""); setError(null); }}>
                Use a different number
              </button>
            </div>
          </form>
        )}
        {error ? <p className="error" role="alert">{error}</p> : null}
      </div>
    </div>
  );
}
