"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui";

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null);
  const [period, setPeriod] = useState("monthly");

  useEffect(() => {
    api(`/api/v1/analytics/reports/${period}`).then(setReport).catch(() => {});
  }, [period]);

  function download() {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `algorixe-report-${period}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!report) return <Spinner />;
  const s = report.summary;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Reports</h2>
        <div className="flex gap-2">
          <select
            className="input max-w-[150px]"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <button className="btn-primary" onClick={download}>
            Export JSON
          </button>
        </div>
      </div>

      <div className="card">
        <p className="text-sm text-slate-500">
          {report.period} report · {report.start_date} → {report.end_date}
        </p>
        <table className="mt-4 w-full text-sm">
          <tbody>
            {Object.entries(s).map(([k, v]) => (
              <tr key={k} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 capitalize text-slate-500">
                  {k.replace(/_/g, " ")}
                </td>
                <td className="py-2 text-right font-medium">{String(v)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
