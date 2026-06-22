"use client";

import { useEffect, useState } from "react";
import { Moon, Sun, Bell } from "lucide-react";
import { api } from "@/lib/api";

export default function Topbar() {
  const [dark, setDark] = useState(false);
  const [email, setEmail] = useState<string>("");

  useEffect(() => {
    const saved = localStorage.getItem("algorixe_theme") === "dark";
    setDark(saved);
    document.documentElement.classList.toggle("dark", saved);
    api("/api/v1/auth/me")
      .then((u) => setEmail(u.email))
      .catch(() => {});
  }, []);

  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("algorixe_theme", next ? "dark" : "light");
  }

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3 dark:border-slate-800 dark:bg-slate-900">
      <h1 className="text-sm font-semibold text-slate-500">
        Algorixe Car Care — AI Sales Console
      </h1>
      <div className="flex items-center gap-3">
        <button className="btn-ghost p-2" title="Notifications">
          <Bell size={18} />
        </button>
        <button onClick={toggle} className="btn-ghost p-2" title="Toggle theme">
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div className="grid h-8 w-8 place-items-center rounded-full bg-brand-700 text-xs font-bold text-white">
          {email ? email[0].toUpperCase() : "A"}
        </div>
      </div>
    </header>
  );
}
