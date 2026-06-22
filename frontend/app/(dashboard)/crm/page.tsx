"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Spinner, EmptyState } from "@/components/ui";
import { tempColor, statusColor, fmtDate } from "@/lib/format";

export default function CrmPage() {
  const [leads, setLeads] = useState<any[] | null>(null);
  const [selected, setSelected] = useState<any>(null);
  const [notes, setNotes] = useState<any[]>([]);
  const [noteBody, setNoteBody] = useState("");

  useEffect(() => {
    api("/api/v1/leads?page_size=50")
      .then((d) => setLeads(d.items))
      .catch(() => setLeads([]));
  }, []);

  function select(lead: any) {
    setSelected(lead);
    api(`/api/v1/leads/${lead.id}/notes`).then(setNotes).catch(() => setNotes([]));
  }

  async function addNote() {
    if (!noteBody.trim() || !selected) return;
    await api(`/api/v1/leads/${selected.id}/notes`, {
      method: "POST",
      body: JSON.stringify({ lead_id: selected.id, body: noteBody }),
    });
    setNoteBody("");
    api(`/api/v1/leads/${selected.id}/notes`).then(setNotes);
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">CRM</h2>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <h3 className="mb-3 text-sm font-semibold">Contacts</h3>
          {!leads ? (
            <Spinner />
          ) : leads.length === 0 ? (
            <EmptyState message="No contacts." />
          ) : (
            <ul className="space-y-1">
              {leads.map((l) => (
                <li key={l.id}>
                  <button
                    onClick={() => select(l)}
                    className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm ${
                      selected?.id === l.id
                        ? "bg-brand-50 dark:bg-brand-900/30"
                        : "hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    <span className="font-medium">{l.full_name || l.phone}</span>
                    <Badge className={tempColor(l.temperature)}>{l.temperature}</Badge>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card lg:col-span-2">
          {!selected ? (
            <EmptyState message="Select a contact to view their CRM record." />
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold">
                  {selected.full_name || "Unknown"}
                </h3>
                <Badge className={statusColor(selected.status)}>
                  {selected.status}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <Field label="Phone" value={selected.phone} />
                <Field label="Email" value={selected.email} />
                <Field label="Location" value={selected.location} />
                <Field label="Budget" value={selected.budget} />
                <Field label="Vehicle" value={selected.vehicle_interest} />
                <Field label="Timeline" value={selected.purchase_timeline} />
                <Field
                  label="Financing"
                  value={selected.financing_need ? "Yes" : "No"}
                />
                <Field
                  label="Trade-in"
                  value={selected.trade_in_interest ? "Yes" : "No"}
                />
              </div>
              {selected.intent_summary && (
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">
                    AI Intent Summary
                  </p>
                  <p className="mt-1 text-sm">{selected.intent_summary}</p>
                </div>
              )}

              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-slate-500">
                  Sales Notes
                </p>
                <div className="space-y-2">
                  {notes.map((n) => (
                    <div
                      key={n.id}
                      className="rounded-lg bg-slate-100 px-3 py-2 text-sm dark:bg-slate-800"
                    >
                      {n.body}
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex gap-2">
                  <input
                    className="input"
                    placeholder="Add a note…"
                    value={noteBody}
                    onChange={(e) => setNoteBody(e.target.value)}
                  />
                  <button className="btn-primary" onClick={addNote}>
                    Add
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value?: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-0.5">{value || "—"}</p>
    </div>
  );
}
