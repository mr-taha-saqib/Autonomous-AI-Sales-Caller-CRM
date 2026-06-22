"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Pagination, Spinner, EmptyState } from "@/components/ui";
import { fmtDate, fmtDuration, statusColor } from "@/lib/format";

export default function CallsPage() {
  const [data, setData] = useState<any>(null);
  const [page, setPage] = useState(1);
  const [detail, setDetail] = useState<any>(null);

  useEffect(() => {
    api(`/api/v1/calls?page=${page}&page_size=15`).then(setData).catch(() => {});
  }, [page]);

  function open(id: number) {
    api(`/api/v1/calls/${id}`).then(setDetail).catch(() => {});
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Call History</h2>
      <div className="card overflow-x-auto">
        {!data ? (
          <Spinner />
        ) : data.items.length === 0 ? (
          <EmptyState message="No calls recorded yet." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-800">
                <th className="py-2">To</th>
                <th>Direction</th>
                <th>When</th>
                <th>Duration</th>
                <th>Outcome</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((c: any) => (
                <tr
                  key={c.id}
                  onClick={() => open(c.id)}
                  className="cursor-pointer border-b border-slate-100 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/40"
                >
                  <td className="py-2.5 font-medium">{c.to_number}</td>
                  <td className="text-slate-500">{c.direction}</td>
                  <td className="text-slate-500">{fmtDate(c.created_at)}</td>
                  <td className="text-slate-500">{fmtDuration(c.duration_seconds)}</td>
                  <td className="text-slate-500">{c.outcome || "—"}</td>
                  <td>
                    <Badge className={statusColor(c.status)}>{c.status}</Badge>
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

      {detail && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={() => setDetail(null)}
        >
          <div
            className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 dark:bg-slate-900"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-bold">Call to {detail.to_number}</h3>
              <button className="btn-ghost px-2 py-1" onClick={() => setDetail(null)}>
                Close
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Info label="Sentiment" value={detail.sentiment} />
              <Info label="Outcome" value={detail.outcome} />
              <Info label="Key intent" value={detail.key_intent} />
              <Info label="Duration" value={fmtDuration(detail.duration_seconds)} />
            </div>
            {detail.summary && (
              <div className="mt-4">
                <p className="text-xs font-semibold uppercase text-slate-500">Summary</p>
                <p className="mt-1 text-sm">{detail.summary}</p>
              </div>
            )}
            {detail.transcript?.turns?.length > 0 && (
              <div className="mt-4">
                <p className="mb-2 text-xs font-semibold uppercase text-slate-500">
                  Transcript
                </p>
                <div className="space-y-2">
                  {detail.transcript.turns.map((t: any, i: number) => (
                    <div
                      key={i}
                      className={`rounded-lg px-3 py-2 text-sm ${
                        t.role === "assistant"
                          ? "bg-brand-50 dark:bg-brand-900/30"
                          : "bg-slate-100 dark:bg-slate-800"
                      }`}
                    >
                      <span className="text-xs font-semibold text-slate-500">
                        {t.role === "assistant" ? "Agent" : "Customer"}:{" "}
                      </span>
                      {t.text}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Info({ label, value }: { label: string; value?: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-0.5">{value || "—"}</p>
    </div>
  );
}
