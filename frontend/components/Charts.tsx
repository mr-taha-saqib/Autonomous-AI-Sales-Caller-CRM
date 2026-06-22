"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#0e7490", "#06b6d4", "#f59e0b", "#ef4444", "#22c55e"];

export function TimeseriesChart({
  data,
  label,
}: {
  data: { date: string; value: number }[];
  label: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0e7490" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#0e7490" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="date" fontSize={11} stroke="#94a3b8" />
        <YAxis fontSize={11} stroke="#94a3b8" allowDecimals={false} />
        <Tooltip />
        <Area
          type="monotone"
          dataKey="value"
          name={label}
          stroke="#0e7490"
          fill="url(#g)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function FunnelChart({
  data,
}: {
  data: { stage: string; count: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} layout="vertical" margin={{ left: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" fontSize={11} stroke="#94a3b8" allowDecimals={false} />
        <YAxis
          dataKey="stage"
          type="category"
          fontSize={11}
          stroke="#94a3b8"
          width={110}
        />
        <Tooltip />
        <Bar dataKey="count" fill="#0e7490" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TemperaturePie({
  hot,
  warm,
  cold,
}: {
  hot: number;
  warm: number;
  cold: number;
}) {
  const data = [
    { name: "Hot", value: hot },
    { name: "Warm", value: warm },
    { name: "Cold", value: cold },
  ];
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={55}
          outerRadius={90}
          paddingAngle={3}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={[COLORS[3], COLORS[2], COLORS[1]][i]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
