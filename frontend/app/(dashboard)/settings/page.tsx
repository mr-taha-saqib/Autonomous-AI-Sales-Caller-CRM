"use client";

import { useEffect, useState } from "react";
import { api, API_BASE } from "@/lib/api";

export default function SettingsPage() {
  const [me, setMe] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    api("/api/v1/auth/me").then(setMe).catch(() => {});
    fetch(`${API_BASE}/health`).then((r) => r.json()).then(setHealth).catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Settings</h2>

      <div className="card">
        <h3 className="mb-3 text-sm font-semibold">Account</h3>
        {me ? (
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-xs uppercase text-slate-500">Name</dt>
              <dd>{me.full_name}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-500">Email</dt>
              <dd>{me.email}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-500">Role</dt>
              <dd className="capitalize">{me.role}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-slate-500">Loading…</p>
        )}
      </div>

      <div className="card">
        <h3 className="mb-3 text-sm font-semibold">System Health</h3>
        {health ? (
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-xs uppercase text-slate-500">Status</dt>
              <dd
                className={
                  health.status === "ok" ? "text-green-600" : "text-amber-600"
                }
              >
                {health.status}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-500">Version</dt>
              <dd>{health.version}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-500">Database</dt>
              <dd>{health.database}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-slate-500">Environment</dt>
              <dd>{health.environment}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-slate-500">Checking…</p>
        )}
      </div>

      <div className="card">
        <h3 className="mb-3 text-sm font-semibold">Voice & AI</h3>
        <p className="text-sm text-slate-500">
          Twilio caller ID, voice, and Claude model are configured via backend
          environment variables (<code>.env</code>). See the Admin Guide for the
          full list. The Algorixe Sales Assistant persona is defined in{" "}
          <code>backend/app/services/prompts.py</code>.
        </p>
      </div>
    </div>
  );
}
