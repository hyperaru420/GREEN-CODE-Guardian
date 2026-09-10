import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Zap, AlertTriangle, Info } from 'lucide-react';

const severityConfig = {
  high: { icon: AlertTriangle, color: '#ef4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)', label: 'High Impact' },
  medium: { icon: Zap, color: '#eab308', bg: 'rgba(234,179,8,0.08)', border: 'rgba(234,179,8,0.2)', label: 'Medium' },
  low: { icon: Info, color: '#22c55e', bg: 'rgba(34,197,94,0.08)', border: 'rgba(34,197,94,0.2)', label: 'Low' },
};

export default function SuggestionCard({ suggestion, index }) {
  const [expanded, setExpanded] = useState(false);
  const config = severityConfig[suggestion.severity] || severityConfig.low;
  const SevIcon = config.icon;

  return (
    // ✅ Removed `overflow-hidden` — it was clipping the expanded panel
    <div className="card transition-all duration-200"
      style={{ animationDelay: `${index * 80}ms` }}>
      <div
        className="p-4 cursor-pointer flex items-start gap-3"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ background: config.bg, border: `1px solid ${config.border}` }}>
          <SevIcon size={14} style={{ color: config.color }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full mr-2"
                style={{ color: config.color, background: config.bg, border: `1px solid ${config.border}` }}>
                {suggestion.category}
              </span>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="dark:text-green-400 text-green-800 font-mono text-sm font-bold">
                -{suggestion.estimated_savings?.toFixed(0)}%
              </span>
              {expanded
                ? <ChevronUp size={14} className="dark:text-green-600 text-green-500" />
                : <ChevronDown size={14} className="dark:text-green-600 text-green-500" />}
            </div>
          </div>
          <h4 className="dark:text-green-200 text-gray-800 text-sm font-semibold mt-1.5">{suggestion.title}</h4>
          <p className="dark:text-green-600 text-green-500 text-xs mt-1 leading-relaxed line-clamp-2">{suggestion.description}</p>
        </div>
      </div>

      {/* ✅ Animated expand/collapse using max-height transition */}
      <div
        style={{
          maxHeight: expanded ? '600px' : '0px',
          overflow: 'hidden',
          transition: 'max-height 0.3s ease',
        }}
      >
        <div className="px-4 pb-4 dark:border-t dark:border-green-900/30 border-t border-green-500/30 pt-3">
          <p className="dark:text-green-500 text-green-600 text-xs leading-relaxed mb-3">{suggestion.description}</p>
          {(suggestion.refactored_snippet || suggestion.code_example) && (
            <div className="bg-dark-950 rounded-lg p-3 border border-green-900/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-green-700 text-xs font-mono ml-2">refactor.py</span>
              </div>
              {suggestion.original_snippet && (
                <div className="mb-3">
                  <div className="text-red-400 text-xs font-mono mb-1">Before:</div>
                  <pre className="text-red-300 text-xs font-mono whitespace-pre-wrap overflow-x-auto leading-relaxed bg-red-950/20 p-2 rounded">
                    {suggestion.original_snippet}
                  </pre>
                </div>
              )}
              <div className="text-green-400 text-xs font-mono mb-1">After:</div>
              <pre className="text-green-300 text-xs font-mono whitespace-pre-wrap overflow-x-auto leading-relaxed">
                {suggestion.refactored_snippet || suggestion.code_example}
              </pre>
            </div>
          )}
          <div className="mt-3 flex items-center gap-2 text-xs text-green-600 font-mono">
            <span>Estimated savings:</span>
            <span className="text-green-400 font-bold">{suggestion.estimated_savings?.toFixed(0)}% energy reduction</span>
          </div>
        </div>
      </div>
    </div>
  );
}