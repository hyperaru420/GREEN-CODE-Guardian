import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card px-3 py-2 text-xs font-mono">
      <p style={{ color: payload[0]?.fill }}>{payload[0]?.name}: {payload[0]?.value?.toFixed(1)}%</p>
    </div>
  );
};

const getBarFill = (value) => {
  if (value < 60) return '#22c55e';
  if (value < 80) return '#eab308';
  return '#ef4444';
};

export default function ResourceBarChart({ data = [], title = "Resource Usage" }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <h3 className="dark:text-green-300 text-green-900 font-semibold font-mono text-sm">{title}</h3>
        <span className="dark:text-green-700 text-green-600 text-xs font-mono">Live</span>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }} barSize={32}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(34,197,94,0.06)" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false}
            tickFormatter={(v) => `${v}%`} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34,197,94,0.04)' }} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Usage">
            {data.map((entry, index) => (
              <Cell key={index} fill={getBarFill(entry.value)}
                style={{ filter: `drop-shadow(0 0 4px ${getBarFill(entry.value)}44)` }} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
