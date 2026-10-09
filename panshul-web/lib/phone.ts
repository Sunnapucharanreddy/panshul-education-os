/** Turn a typed phone number into E.164, defaulting bare 10-digit numbers to India. */
export function toE164(input: string): string | null {
  const compact = input.trim().replace(/[\s()-]/g, "");
  if (/^\+\d{9,15}$/.test(compact)) return compact;
  const digits = compact.replace(/\D/g, "");
  if (digits.length === 10) return `+91${digits}`;
  if (digits.length === 12 && digits.startsWith("91")) return `+${digits}`;
  return null;
}

export function maskPhone(phone: string) {
  const last = phone.replace(/\D/g, "").slice(-4);
  return last ? `···· ${last}` : "Signed in";
}

export function safeNext(value: string | null) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/classroom";
  return value;
}
