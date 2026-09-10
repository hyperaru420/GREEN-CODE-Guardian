import React, { useState, useEffect } from 'react';
import { historyAPI } from '../services/api';
import { History, Search, TrendingUp, TrendingDown, Minus, Filter } from 'lucide-react';
import EmissionChart from '../charts/EmissionChart';
import toast from 'react-hot-toast';

const ScoreBadge = ({ score }) => {
  const color = score >= 75 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444';
  return (
    <span className="font-bold font-mono text-sm px-2.5 py-0.5 rounded-full"
      style={{ color, background: `${color}15`, border: `1px solid ${color}30` }}>
      {score?.toFixed(0)}
    </span>
  );
};

export default function HistoryPage() {
  const [projects, setProjects] = useState([]);
  const [names, setNames] = useState([]);
  const [selected, setSelected] = useState('');
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [pRes, nRes] = await Promise.all([
          historyAPI.getProjects({ limit: 50 }),
          historyAPI.getProjectNames(),
        ]);
        setProjects(pRes.data.projects || []);
        setNames(nRes.data.projects || []);
      } catch { toast.error('Failed to load history'); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  useEffect(() => {
    if (!selected) return;
    historyAPI.getTrends(selected).then(r => setTrends(r.data.trends || [])).catch(() => {});
  }, [selected]);

  const filtered = projects.filter(p =>
    (!search || p.project_name?.toLowerCase().includes(search.toLowerCase())) &&
    (!selected || p.project_name === selected)
  );

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 spinner" />
    </div>
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 mb-1">
        <History size={18} className="text-green-400" />
        <h1 className="text-xl font-black text-green-300 font-mono">Project History</h1>
      </div>

      {/* Filters */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-green-700" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search projects..."
            className="w-full bg-dark-950 border border-green-900/40 text-green-200 rounded-lg pl-9 pr-3 py-2 text-sm font-mono
              placeholder-green-800 focus:outline-none focus:border-green-500/60 transition-all" />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-green-600" />
          <select value={selected} onChange={e => setSelected(e.target.value)}
            className="bg-dark-950 border border-green-900/40 text-green-200 rounded-lg px-3 py-2 text-sm font-mono
              focus:outline-none focus:border-green-500/60 transition-all">
            <option value="">All Projects</option>
            {names.map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <span className="text-green-700 text-xs font-mono">{filtered.length} records</span>
      </div>

      {/* Trend chart (when project selected) */}
      {selected && trends.length > 0 && (
        <EmissionChart data={trends} title={`Trends — ${selected}`} />
      )}

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="border-b border-green-900/30">
                {['Project', 'CPU %', 'Memory %', 'Carbon gCO2', 'Score', 'Region', 'Timestamp'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-green-600 text-xs uppercase tracking-wider font-semibold">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-green-800">No records found</td></tr>
              ) : filtered.map((p, i) => (
                <tr key={p._id || i}
                  className="border-b border-green-900/10 hover:bg-green-500/5 transition-colors cursor-pointer"
                  onClick={() => setSelected(p.project_name)}>
                  <td className="px-4 py-3 text-green-200 font-semibold">{p.project_name}</td>
                  <td className="px-4 py-3">
                    <span className={p.cpu_usage > 80 ? 'text-red-400' : p.cpu_usage > 60 ? 'text-yellow-400' : 'text-green-400'}>
                      {p.cpu_usage?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={p.memory_usage > 85 ? 'text-red-400' : p.memory_usage > 70 ? 'text-yellow-400' : 'text-green-400'}>
                      {p.memory_usage?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-green-400">{p.carbon_emissions?.toFixed(6)}</td>
                  <td className="px-4 py-3"><ScoreBadge score={p.green_score} /></td>
                  <td className="px-4 py-3 text-green-700">{p.region || 'N/A'}</td>
                  <td className="px-4 py-3 text-green-700 text-xs">
                    {p.timestamp ? new Date(p.timestamp).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
