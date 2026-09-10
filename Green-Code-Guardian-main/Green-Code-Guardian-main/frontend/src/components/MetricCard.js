import React from 'react';

const getBarColor = (value, thresholds = [60, 80]) => {
  if (value < thresholds[0]) return '#22c55e';
  if (value < thresholds[1]) return '#eab308';
  return '#ef4444';
};

export default function MetricCard({ icon: Icon, label, value, unit, subtext, percentage, thresholds, color }) {
  const barColor = color || (percentage !== undefined ? getBarColor(percentage, thresholds) : '#22c55e');

  return (
    <div className="card p-5 fade-in-up">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: `${barColor}15`, border: `1px solid ${barColor}30` }}>
            <Icon size={16} style={{ color: barColor }} />
          </div>
          <span className="dark:text-green-500 text-green-600 text-xs font-mono uppercase tracking-widest">{label}</span>
        </div>
        {percentage !== undefined && (
          <span className="text-xs font-mono px-2 py-0.5 rounded-full"
            style={{ color: barColor, background: `${barColor}15`, border: `1px solid ${barColor}25` }}>
            {percentage.toFixed(1)}%
          </span>
        )}
      </div>

      <div className="mt-1">
        <span className="text-2xl font-black font-mono" style={{ color: barColor }}>
          {typeof value === 'number' ? value.toFixed(value < 10 ? 4 : 1) : value}
        </span>
        {unit && <span className="dark:text-green-600 text-green-500 text-sm ml-1.5 font-mono">{unit}</span>}
      </div>

      {subtext && <p className="dark:text-green-700 text-green-600 text-xs mt-1.5 font-mono">{subtext}</p>}

      {percentage !== undefined && (
        <div className="mt-3 h-1 rounded-full dark:bg-green-950 bg-gray-200 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{
              width: `${Math.min(percentage, 100)}%`,
              background: barColor,
              boxShadow: `0 0 8px ${barColor}66`,
            }}
          />
        </div>
      )}
    </div>
  );
}
