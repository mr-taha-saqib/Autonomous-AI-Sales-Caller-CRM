"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatCard, Spinner, Badge } from "@/components/ui";
import { FunnelChart, TemperaturePie } from "@/components/Charts";
import { fmtDate, statusColor, tempColor } from "@/lib/format";

export default function DashboardHome() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api("/api/v1/dashboard/home").then(setData).catch(() => {});
  }, []);

  if (!data) return <Spinner />;
  const s = data.summary;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Dashboard</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Leads" value={s.total_leads} hint={`${s.hot_leads} hot`} />
        <StatCard label="Calls Made" value={s.total_calls} hint={`${s.completed_calls} completed`} />
        <StatCard label="Appointments" value={s.appointments_scheduled} hint={`${s.appointments_completed} completed`} />
        <StatCard label="Lead Conversion" value={`${s.lead_conversion_rate}%`} hint="lead → customer" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Sales Funnel</h3>
          <FunnelChart data={data.funnel} />
        </div>
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Lead Temperature</h3>
          <TemperaturePie hot={s.hot_leads} warm={s.warm_leads} cold={s.cold_leads} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Hottest Leads</h3>
          <table className="w-full text-sm">
            <tbody>
              {data.hot_leads.map((l: any) => (
                <tr key={l.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2 font-medium">{l.full_name || l.phone}</td>
                  <td className="py-2 text-slate-500">{l.vehicle_interest || "—"}</td>
                  <td className="py-2 text-right">
                    <Badge className={tempColor(l.temperature)}>
                      {l.temperature} · {l.score}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Recent Calls</h3>
          <table className="w-full text-sm">
            <tbody>
              {data.recent_calls.map((c: any) => (
                <tr key={c.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2 font-medium">{c.to_number}</td>
                  <td className="py-2 text-slate-500">{fmtDate(c.created_at)}</td>
                  <td className="py-2 text-right">
                    <Badge className={statusColor(c.status)}>{c.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
