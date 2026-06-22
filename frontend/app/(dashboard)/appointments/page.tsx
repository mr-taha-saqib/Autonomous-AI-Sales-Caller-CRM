"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Spinner, EmptyState } from "@/components/ui";
import { fmtDate, statusColor } from "@/lib/format";

export default function AppointmentsPage() {
  const [items, setItems] = useState<any[] | null>(null);

  function load() {
    api("/api/v1/appointments").then(setItems).catch(() => setItems([]));
  }
  useEffect(load, []);

  async function setStatus(id: number, status: string) {
    await api(`/api/v1/appointments/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    load();
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Appointments</h2>
      <div className="card overflow-x-auto">
        {!items ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="No appointments scheduled." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-800">
                <th className="py-2">When</th>
                <th>Type</th>
                <th>Location</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2.5 font-medium">{fmtDate(a.scheduled_for)}</td>
                  <td className="text-slate-500">
                    {a.appointment_type.replace("_", " ")}
                  </td>
                  <td className="text-slate-500">
                    {a.location || a.meeting_link || "—"}
                  </td>
                  <td>
                    <Badge className={statusColor(a.status)}>{a.status}</Badge>
                  </td>
                  <td className="text-right">
                    <select
                      className="input max-w-[150px] py-1 text-xs"
                      value={a.status}
                      onChange={(e) => setStatus(a.id, e.target.value)}
                    >
                      {["scheduled", "confirmed", "completed", "canceled", "no_show"].map(
                        (s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        )
                      )}
                    </select>
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
