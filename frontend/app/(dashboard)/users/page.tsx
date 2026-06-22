"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Spinner, EmptyState } from "@/components/ui";

const EMPTY = { full_name: "", email: "", password: "", role: "agent" };

export default function UsersPage() {
  const [users, setUsers] = useState<any[] | null>(null);
  const [form, setForm] = useState({ ...EMPTY });
  const [error, setError] = useState("");

  function load() {
    api("/api/v1/users")
      .then(setUsers)
      .catch((e) => {
        setUsers([]);
        setError(e.message);
      });
  }
  useEffect(load, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/api/v1/users", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm({ ...EMPTY });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function deactivate(id: number) {
    if (!confirm("Deactivate this user?")) return;
    await api(`/api/v1/users/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">User Management</h2>
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="card">
        <h3 className="mb-3 text-sm font-semibold">Add User</h3>
        <form onSubmit={create} className="grid grid-cols-1 gap-3 sm:grid-cols-4">
          <input
            className="input"
            placeholder="Full name"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            required
          />
          <input
            className="input"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <input
            className="input"
            type="password"
            placeholder="Password (8+)"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <select
            className="input"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="agent">Agent</option>
            <option value="viewer">Viewer</option>
          </select>
          <button className="btn-primary sm:col-span-4">Create user</button>
        </form>
      </div>

      <div className="card overflow-x-auto">
        {!users ? (
          <Spinner />
        ) : users.length === 0 ? (
          <EmptyState message="No users." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-800">
                <th className="py-2">Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Active</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2.5 font-medium">{u.full_name}</td>
                  <td className="text-slate-500">{u.email}</td>
                  <td>
                    <Badge className="bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-200">
                      {u.role}
                    </Badge>
                  </td>
                  <td>{u.is_active ? "Yes" : "No"}</td>
                  <td className="text-right">
                    {u.is_active && (
                      <button
                        className="btn-ghost px-2 py-1 text-xs text-red-600"
                        onClick={() => deactivate(u.id)}
                      >
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
