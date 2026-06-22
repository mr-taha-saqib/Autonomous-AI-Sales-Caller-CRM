"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatCard, Spinner } from "@/components/ui";
import { FunnelChart, TimeseriesChart, TemperaturePie } from "@/components/Charts";

export default function AnalyticsPage() {
  const [report, setReport] = useState<any>(null);
  const [period, setPeriod] = useState("weekly");

  useEffect(() => {
    api(`/api/v1/analytics/reports/${period}`).then(setReport).catch(() => {});
  }, [period]);

  if (!report) return <Spinner />;
  const s = report.summary;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Analytics</h2>
        <select
          className="input max-w-[160px]"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Avg Call Duration" value={`${s.avg_call_duration_seconds}s`} />
        <StatCard label="Completed Calls" value={s.completed_calls} />
        <StatCard
          label="Appt Conversion"
          value={`${s.appointment_conversion_rate}%`}
        />
        <StatCard label="Lead Conversion" value={`${s.lead_conversion_rate}%`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Calls per Day</h3>
          <TimeseriesChart data={report.calls_by_day} label="Calls" />
        </div>
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">New Leads per Day</h3>
          <TimeseriesChart data={report.leads_by_day} label="Leads" />
        </div>
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Sales Funnel</h3>
          <FunnelChart data={report.funnel} />
        </div>
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold">Lead Temperature</h3>
          <TemperaturePie hot={s.hot_leads} warm={s.warm_leads} cold={s.cold_leads} />
        </div>
      </div>
    </div>
  );
}
