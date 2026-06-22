export function tempColor(t: string): string {
  return (
    {
      hot: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
      warm: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
      cold: "bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300",
    }[t] || "bg-slate-100 text-slate-700"
  );
}

export function statusColor(s: string): string {
  if (["completed", "converted", "confirmed", "qualified"].includes(s))
    return "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300";
  if (["failed", "lost", "no_answer", "canceled", "do_not_call"].includes(s))
    return "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300";
  return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300";
}

export function fmtDate(iso?: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function fmtDuration(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
}
