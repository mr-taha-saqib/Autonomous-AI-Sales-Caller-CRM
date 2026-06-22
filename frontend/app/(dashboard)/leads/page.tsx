"use client";

import { useCallback, useEffect, useState } from "react";
import { Search, PhoneOutgoing } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Pagination, Spinner, EmptyState } from "@/components/ui";
import { tempColor, statusColor } from "@/lib/format";

export default function LeadsPage() {
  const [data, setData] = useState<any>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [temp, setTemp] = useState("");
  const [calling, setCalling] = useState<number | null>(null);

  const load = useCallback(() => {
    const params = new URLSearchParams({ page: String(page), page_size: "15" });
    if (search) params.set("search", search);
    if (temp) params.set("temperature", temp);
    api(`/api/v1/leads?${params}`).then(setData).catch(() => {});
  }, [page, search, temp]);

  useEffect(() => {
    load();
  }, [load]);

  async function call(lead: any) {
    setCalling(lead.id);
    try {
      await api("/api/v1/calls/outbound", {
        method: "POST",
        body: JSON.stringify({ to_number: lead.phone, lead_id: lead.id }),
      });
      alert(`Calling ${lead.full_name || lead.phone}…`);
      load();
    } catch (e: any) {
      alert(`Call failed: ${e.message}`);
    } finally {
      setCalling(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Lead Management</h2>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
          <input
            className="input pl-9"
            placeholder="Search name, phone, vehicle…"
            value={search}
            onChange={(e) => {
              setPage(1);
              setSearch(e.target.value);
            }}
          />
        </div>
        <select
          className="input max-w-[160px]"
          value={temp}
          onChange={(e) => {
            setPage(1);
            setTemp(e.target.value);
          }}
        >
          <option value="">All temperatures</option>
          <option value="hot">Hot</option>
          <option value="warm">Warm</option>
          <option value="cold">Cold</option>
        </select>
      </div>

      <div className="card overflow-x-auto">
        {!data ? (
          <Spinner />
        ) : data.items.length === 0 ? (
          <EmptyState message="No leads match your filters." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-800">
                <th className="py-2">Name</th>
                <th>Phone</th>
                <th>Vehicle</th>
                <th>Timeline</th>
                <th>Score</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((l: any) => (
                <tr
                  key={l.id}
                  className="border-b border-slate-100 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/40"
                >
                  <td className="py-2.5 font-medium">{l.full_name || "Unknown"}</td>
                  <td className="text-slate-500">{l.phone}</td>
                  <td className="text-slate-500">{l.vehicle_interest || "—"}</td>
                  <td className="text-slate-500">{l.purchase_timeline || "—"}</td>
                  <td>
                    <Badge className={tempColor(l.temperature)}>
                      {l.temperature} · {l.score}
                    </Badge>
                  </td>
                  <td>
                    <Badge className={statusColor(l.status)}>{l.status}</Badge>
                  </td>
                  <td className="text-right">
                    <button
                      className="btn-primary px-2.5 py-1 text-xs"
                      disabled={calling === l.id}
                      onClick={() => call(l)}
                    >
                      <PhoneOutgoing size={14} />
                      {calling === l.id ? "Dialing…" : "Call"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {data && (
          <Pagination
            page={data.page}
            pageSize={data.page_size}
            total={data.total}
            onPage={setPage}
          />
        )}
      </div>
    </div>
  );
}
