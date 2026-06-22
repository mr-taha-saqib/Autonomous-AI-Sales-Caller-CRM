// Lightweight typed API client for the Algorixe backend.
const BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const API_BASE = BASE;

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("algorixe_token");
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem("algorixe_token", access);
  localStorage.setItem("algorixe_refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("algorixe_token");
  localStorage.removeItem("algorixe_refresh");
}

type Options = RequestInit & { auth?: boolean };

export async function api<T = any>(
  path: string,
  options: Options = {}
): Promise<T> {
  const { auth = true, headers, ...rest } = options;
  const h: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };
  if (auth) {
    const token = getToken();
    if (token) h["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...rest, headers: h });

  if (res.status === 401 && typeof window !== "undefined") {
    clearTokens();
    if (!window.location.pathname.startsWith("/login")) {
      window.location.href = "/login";
    }
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Invalid email or password");
  return res.json() as Promise<{ access_token: string; refresh_token: string }>;
}
