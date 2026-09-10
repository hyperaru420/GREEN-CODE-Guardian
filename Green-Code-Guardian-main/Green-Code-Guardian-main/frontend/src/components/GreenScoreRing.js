import React from 'react';

const getColor = (score) => {
  if (score >= 75) return { stroke: '#22c55e', text: '#22c55e', label: 'Excellent', bg: 'rgba(34,197,94,0.1)' };
  if (score >= 50) return { stroke: '#eab308', text: '#eab308', label: 'Moderate', bg: 'rgba(234,179,8,0.1)' };
  if (score >= 25) return { stroke: '#f97316', text: '#f97316', label: 'Poor', bg: 'rgba(249,115,22,0.1)' };
  return { stroke: '#ef4444', text: '#ef4444', label: 'Critical', bg: 'rgba(239,68,68,0.1)' };
};

const getGrade = (score) => {
  if (score >= 70) return 'B';
  if (score >= 60) return 'C';
  if (score >= 50) return 'D';
  return 'F';
};

export default function GreenScoreRing({ score = 0, size = 160, grade }) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const { stroke, text, label, bg } = getColor(score);
  const displayGrade = grade || getGrade(score);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background ring */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="rgba(34,197,94,0.1)" strokeWidth="10"
          />
          {/* Score ring */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={stroke} strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)', filter: `drop-shadow(0 0 8px ${stroke}66)` }}
          />
        </svg>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span style={{ color: text, textShadow: `0 0 20px ${text}66` }}
            className="text-4xl font-black font-mono leading-none">
            {Math.round(score)}
          </span>
          <span className="text-green-600 text-xs font-mono mt-0.5">/ 100</span>
          <span style={{ color: text, background: bg, border: `1px solid ${stroke}33` }}
            className="text-xs font-bold px-2 py-0.5 rounded-full mt-1.5">
            {displayGrade}
          </span>
        </div>
      </div>
      <div style={{ color: text }} className="text-sm font-semibold font-mono">{label}</div>
    </div>
  );
}
