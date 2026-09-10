import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { format, parseISO, addHours, addMinutes } from 'date-fns';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card px-4 py-3 text-xs font-mono" style={{ minWidth: 180 }}>
      <p className="dark:text-green-500 text-green-600 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex justify-between gap-4 dark:text-green-300 text-green-800">
          <span style={{ color: entry.color }}>{entry.name}</span>
          <span>{typeof entry.value === 'number' ? entry.value.toFixed(4) : entry.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function EmissionChart({ data = [], title = "Emission Trends" }) {
  const formatted = data.map(d => ({
    ...d,
    time: (() => {
      try {
        const utcTime = parseISO(d.timestamp);
        const istTime = addMinutes(addHours(utcTime, 5), 30);
        return format(istTime, 'HH:mm');
      } catch {
        return d.timestamp?.slice(11, 16) || '';
      }
    })(),
  }));

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <h3 className="dark:text-green-300 text-green-900 font-semibold font-mono text-sm">{title}</h3>
        <span className="dark:text-green-700 text-green-600 text-xs font-mono">{data.length} readings</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={formatted} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="carbonGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="energyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4ade80" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#86efac" stopOpacity={0.12} />
              <stop offset="95%" stopColor="#86efac" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.06)" />
          <XAxis dataKey="time" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
          <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} width={50} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: '11px', color: 'var(--text-secondary)' }} />
          <Area type="monotone" dataKey="carbon_emissions" name="Carbon (gCO2)" stroke="#22c55e"
            strokeWidth={2} fill="url(#carbonGrad)" dot={false} activeDot={{ r: 4, fill: '#22c55e' }} />
          <Area type="monotone" dataKey="green_score" name="Green Score" stroke="#86efac"
            strokeWidth={1.5} fill="url(#scoreGrad)" dot={false} activeDot={{ r: 3, fill: '#86efac' }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
