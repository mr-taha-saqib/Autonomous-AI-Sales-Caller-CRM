"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users2,
  PhoneCall,
  CalendarDays,
  Contact,
  BarChart3,
  FileText,
  UserCog,
  Settings,
  LogOut,
} from "lucide-react";
import { clearTokens } from "@/lib/api";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/leads", label: "Lead Management", icon: Users2 },
  { href: "/calls", label: "Call History", icon: PhoneCall },
  { href: "/appointments", label: "Appointments", icon: CalendarDays },
  { href: "/crm", label: "CRM", icon: Contact },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/users", label: "User Management", icon: UserCog },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearTokens();
    router.push("/login");
  }

  return (
    <aside className="flex w-64 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center gap-2 px-6 py-5">
        <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-700 font-bold text-white">
          A
        </div>
        <div>
          <p className="text-sm font-bold leading-tight">Algorixe</p>
          <p className="text-xs text-slate-500">Sales Assistant</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                active
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-100"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
      <button
        onClick={logout}
        className="m-3 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        <LogOut size={18} /> Sign out
      </button>
    </aside>
  );
}
