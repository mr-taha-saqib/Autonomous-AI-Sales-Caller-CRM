"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function NewAppointmentPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    lead_id: "",
    appointment_type: "showroom_visit",
    scheduled_for: "",
    location: "",
    meeting_link: "",
    notes: "",
  });
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/api/v1/appointments", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          lead_id: form.lead_id ? Number(form.lead_id) : null,
          scheduled_for: new Date(form.scheduled_for).toISOString(),
        }),
      });
      router.push("/appointments");
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-4">
      <h2 className="text-xl font-bold">New Appointment</h2>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <form onSubmit={submit} className="card space-y-3">
        <label className="block text-sm">
          Lead ID (optional)
          <input
            className="input mt-1"
            value={form.lead_id}
            onChange={(e) => setForm({ ...form, lead_id: e.target.value })}
          />
        </label>
        <label className="block text-sm">
          Type
          <select
            className="input mt-1"
            value={form.appointment_type}
            onChange={(e) =>
              setForm({ ...form, appointment_type: e.target.value })
            }
          >
            <option value="showroom_visit">Showroom Visit</option>
            <option value="virtual_consultation">Virtual Consultation</option>
          </select>
        </label>
        <label className="block text-sm">
          Date &amp; time
          <input
            type="datetime-local"
            className="input mt-1"
            value={form.scheduled_for}
            onChange={(e) => setForm({ ...form, scheduled_for: e.target.value })}
            required
          />
        </label>
        <label className="block text-sm">
          Location
          <input
            className="input mt-1"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
          />
        </label>
        <label className="block text-sm">
          Meeting link (virtual)
          <input
            className="input mt-1"
            value={form.meeting_link}
            onChange={(e) => setForm({ ...form, meeting_link: e.target.value })}
          />
        </label>
        <label className="block text-sm">
          Notes
          <textarea
            className="input mt-1"
            rows={3}
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </label>
        <button className="btn-primary w-full">Create appointment</button>
      </form>
    </div>
  );
}
