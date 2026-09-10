import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
  Cpu, MemoryStick, Clock, HardDrive, Wifi, Leaf, RefreshCw,
  Download, Award, Zap, Play, ChevronDown
} from 'lucide-react';
import { metricsAPI, suggestionsAPI, certificateAPI, historyAPI } from '../services/api';
import GreenScoreRing from '../components/GreenScoreRing';
import MetricCard from '../components/MetricCard';
import SuggestionCard from '../components/SuggestionCard';
import EmissionChart from '../charts/EmissionChart';
import ResourceBarChart from '../charts/ResourceBarChart';

const REGIONS = [
  { id: 'us-east', name: 'US East' }, { id: 'us-west', name: 'US West' },
  { id: 'eu-west', name: 'EU West' }, { id: 'eu-north', name: 'EU North' },
  { id: 'ap-south', name: 'Asia South' }, { id: 'ap-east', name: 'Asia East' },
  { id: 'sa-east', name: 'South America' }, { id: 'global-average', name: 'Global Avg' },
];

function IssuesBreakdown({ issues }) {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [showAll, setShowAll] = useState(false);
  const visible = showAll ? issues : issues.slice(0, 4);

  return (
    <div className="card p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-green-300 font-semibold font-mono text-sm">Code Issues Breakdown</h3>
        <span className="text-xs text-red-400 font-mono">{issues.length} issues found</span>
      </div>
      <div className="space-y-2">
        {visible.map((issue, i) => {
          const [title, ...rest] = issue.split(':');
          const detail = rest.join(':').trim();
          const isOpen = expandedIndex === i;
          return (
            <div key={i} className="bg-dark-950 rounded-lg border border-red-900/20 overflow-hidden transition-all duration-200">
              <button
                onClick={() => setExpandedIndex(isOpen ? null : i)}
                className="w-full flex items-start justify-between gap-3 p-3 text-left hover:bg-red-950/10 transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0 mt-1" />
                  <span className="text-red-400 text-xs font-mono font-semibold">{title?.trim()}</span>
                </div>
                <ChevronDown size={14} className="text-red-700 flex-shrink-0 mt-0.5 transition-transform duration-200"
                  style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }} />
              </button>
              {isOpen && detail && (
                <div className="px-3 pb-3 pt-0">
                  <div className="border-t border-red-900/20 pt-2">
                    <p className="text-red-300 text-xs font-mono leading-relaxed whitespace-pre-wrap">{detail}</p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {issues.length > 4 && (
        <button onClick={() => setShowAll(!showAll)}
          className="mt-3 w-full text-xs font-mono text-red-600 hover:text-red-400 transition-colors py-1.5 border border-red-900/20 rounded-lg hover:border-red-900/40">
          {showAll ? 'Show less ↑' : `Show ${issues.length - 4} more issues ↓`}
        </button>
      )}
    </div>
  );
}

// Reusable dark card stat block
function CarbonStatCard({ label, value }) {
  return (
    <div className="bg-dark-950 rounded-lg p-3 border border-green-900/20">
      <div className="text-green-600 text-xs font-mono capitalize mb-1">{label}</div>
      <div className="text-green-300 font-bold font-mono">{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [projectName, setProjectName] = useState('my-application');
  const [region, setRegion] = useState('us-east');
  const [scanDirectory, setScanDirectory] = useState('C:/Users/ADMIN/OneDrive/Desktop/greencode-guardian');
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastScan, setLastScan] = useState(null);
  const [data, setData] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [trends, setTrends] = useState([]);
  const [certLoading, setCertLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [codeScanResult, setCodeScanResult] = useState(null);
  const [codeScanLoading, setCodeScanLoading] = useState(false);
  const [codeSuggestions, setCodeSuggestions] = useState([]);

  const fetchSummary = async () => {
    try { setSummary((await historyAPI.getSummary()).data); } catch {}
  };

  const fetchTrends = async (name) => {
    try { setTrends((await historyAPI.getTrends(name)).data.trends || []); } catch (err) {
      console.error('Failed to fetch trends:', err);
    }
  };

  const parseError = (err, fallback) => {
    const detail = err.response?.data?.detail;
    return typeof detail === 'string' ? detail
      : Array.isArray(detail) ? detail.map(d => d.msg).join(', ')
      : fallback;
  };

  const runScan = useCallback(async () => {
    if (!projectName.trim()) { toast.error('Enter a project name'); return; }
    setLoading(true);
    try {
      const { metrics, carbon, green_score } = (await metricsAPI.collect(projectName, region)).data;
      setData({ metrics, carbon, green_score });
      setLastScan(new Date().toLocaleTimeString());
      toast.success(`Scan complete — Score: ${green_score.score}`);

      const sugRes = await suggestionsAPI.generate({
        cpu_usage: metrics.cpu_usage, memory_usage: metrics.memory_usage,
        carbon_emissions: carbon.carbon_emissions_gco2, green_score: green_score.score,
        project_name: projectName, disk_usage: metrics.disk_usage, network_usage: metrics.network_usage,
      });
      setSuggestions(Array.isArray(sugRes.data.data?.suggestions) ? sugRes.data.data.suggestions : []);
      await fetchTrends(projectName);
      await fetchSummary();
    } catch (err) {
      toast.error(parseError(err, 'Scan failed — is backend running?'));
    } finally { setLoading(false); }
  }, [projectName, region]);

  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(runScan, 15000);
    return () => clearInterval(id);
  }, [autoRefresh, runScan]);

  useEffect(() => { fetchSummary(); }, []);

  const generateCert = async (setLoad = setCertLoading) => {
    if (!data) { toast.error('Run a scan first'); return; }
    setLoad(true);
    try {
      const cert = (await certificateAPI.generate(null, projectName)).data.certificate;
      toast.success(`Certificate ${cert.certificate_id} generated!`);
    } catch { toast.error('Certificate generation failed'); }
    finally { setLoad(false); }
  };

  const scanCode = async () => {
    if (!scanDirectory.trim()) { toast.error('Enter a directory path'); return; }
    setCodeScanLoading(true);
    try {
      const codeResult = (await suggestionsAPI.scan(scanDirectory)).data.data;
      setCodeScanResult(codeResult);
      const refactorRes = await suggestionsAPI.refactor({ path: scanDirectory, project_name: projectName, scan_type: 'code', max_files: 3 });
      const suggestions = Array.isArray(refactorRes.data.data?.refactor_suggestions) ? refactorRes.data.data.refactor_suggestions : [];
      setCodeSuggestions(suggestions);
      toast.success(`Code scan complete — Green Score: ${codeResult.green_score}. Found ${suggestions.length} AI suggestions.`);
    } catch (err) {
      toast.error(parseError(err, 'Code scan failed'));
    } finally { setCodeScanLoading(false); }
  };

  const metrics = data?.metrics;
  const carbon = data?.carbon;
  const score = data?.green_score;
  const cs = codeScanResult;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Leaf size={18} className="dark:text-green-400 text-green-700" />
            <h1 className="text-xl font-black dark:text-green-300 text-green-900 font-mono">Dashboard</h1>
            {lastScan && <span className="text-xs dark:text-green-700 text-green-600 font-mono ml-2">Last scan: {lastScan}</span>}
          </div>
          <p className="dark:text-green-700 text-green-600 text-sm font-mono">Real-time sustainability monitoring</p>
        </div>
        {summary && (
          <div className="flex items-center gap-4 text-xs font-mono">
            {[['Total Scans', summary.total_scans], ['Avg Score', summary.avg_green_score?.toFixed(0)], ['gCO2 Total', summary.total_carbon_gco2?.toFixed(2)]].map(([label, val]) => (
              <div key={label} className="text-center">
                <div className="dark:text-green-400 text-green-800 font-bold text-lg">{val}</div>
                <div className="dark:text-green-700 text-green-600">{label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Scan Controls */}
      <div className="card p-5">
        <div className="flex items-center gap-3 flex-wrap">
          {[['PROJECT NAME', projectName, setProjectName, 'my-application'], ['SCAN DIRECTORY', scanDirectory, setScanDirectory, 'C:/path/to/project']].map(([label, val, setter, placeholder]) => (
            <div key={label} className="flex-1 min-w-48">
              <label className="dark:text-green-600 text-green-500 text-xs font-mono mb-1 block">{label}</label>
              <input value={val} onChange={e => setter(e.target.value)} placeholder={placeholder}
                className="w-full dark:bg-dark-950 bg-white dark:border dark:border-green-900/40 border border-green-500/40 dark:text-green-200 text-gray-800 rounded-lg px-3 py-2 text-sm font-mono dark:placeholder-green-800 placeholder-gray-500 focus:outline-none dark:focus:border-green-500/60 focus:border-green-600/60 transition-all" />
            </div>
          ))}
          <div className="min-w-40">
            <label className="dark:text-green-600 text-green-500 text-xs font-mono mb-1 block">REGION</label>
            <div className="relative">
              <select value={region} onChange={e => setRegion(e.target.value)}
                className="w-full dark:bg-dark-950 bg-white dark:border dark:border-green-900/40 border border-green-500/40 dark:text-green-200 text-gray-800 rounded-lg px-3 py-2 text-sm font-mono appearance-none focus:outline-none dark:focus:border-green-500/60 focus:border-green-600/60 transition-all pr-8">
                {REGIONS.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 dark:text-green-600 text-green-500 pointer-events-none" />
            </div>
          </div>
          <div className="flex items-end gap-2 flex-wrap">
            <button onClick={runScan} disabled={loading} className="btn-primary px-5 py-2 rounded-lg text-sm font-mono flex items-center gap-2 disabled:opacity-50">
              {loading ? <div className="w-4 h-4 spinner" /> : <Play size={14} />}
              {loading ? 'Scanning...' : 'Run Scan'}
            </button>
            <button onClick={() => { setAutoRefresh(!autoRefresh); toast.success(autoRefresh ? 'Auto-refresh off' : 'Auto-refresh on (15s)'); }}
              className={`btn-outline px-4 py-2 rounded-lg text-sm font-mono flex items-center gap-2 ${autoRefresh ? 'dark:border-green-400 dark:text-green-400 border-green-600 text-green-600' : ''}`}>
              <RefreshCw size={14} className={autoRefresh ? 'animate-spin' : ''} />
              {autoRefresh ? 'Stop' : 'Auto'}
            </button>
            <button onClick={() => generateCert(setCertLoading)} disabled={certLoading} className="btn-outline px-4 py-2 rounded-lg text-sm font-mono flex items-center gap-2 disabled:opacity-50">
              {certLoading ? <div className="w-4 h-4 spinner" /> : <Award size={14} />}Certify
            </button>
            <button onClick={scanCode} disabled={codeScanLoading} className="btn-outline px-4 py-2 rounded-lg text-sm font-mono flex items-center gap-2 disabled:opacity-50">
              {codeScanLoading ? <div className="w-4 h-4 spinner" /> : <Download size={14} />}Scan Code
            </button>
          </div>
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        <div className="card p-6 flex flex-col items-center justify-center gap-2">
          <div className="dark:text-green-600 text-green-500 text-xs font-mono uppercase tracking-widest mb-2">Green Score</div>
          <GreenScoreRing score={score?.score || 0} grade={score?.grade || 'N/A'} size={160} />
          {score?.breakdown && (
            <div className="w-full mt-4 space-y-1.5">
              {Object.entries(score.breakdown).map(([key, val]) => (
                <div key={key} className="flex justify-between text-xs font-mono">
                  <span className="text-green-700 capitalize">{key.replace('_score', '')}</span>
                  <span className="text-green-400">{val?.toFixed(0)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="xl:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-4">
          <MetricCard icon={Cpu} label="CPU Usage" value={metrics?.cpu_usage || 0} unit="%" percentage={metrics?.cpu_usage} thresholds={[60, 80]} />
          <MetricCard icon={MemoryStick} label="Memory" value={metrics?.memory_usage || 0} unit="%" percentage={metrics?.memory_usage} thresholds={[70, 85]} />
          <MetricCard icon={Clock} label="Exec Time" value={metrics?.execution_time || 0} unit="s" color="#4ade80" />
          <MetricCard icon={HardDrive} label="Disk Usage" value={metrics?.disk_usage || 0} unit="%" percentage={metrics?.disk_usage} thresholds={[70, 90]} />
          <MetricCard icon={Wifi} label="Network" value={metrics?.network_usage || 0} unit="MB" color="#86efac" />
          <MetricCard icon={Leaf} label="Carbon" value={carbon?.carbon_emissions_gco2 || 0} unit="gCO2"
            color={carbon?.carbon_emissions_gco2 < 10 ? '#22c55e' : carbon?.carbon_emissions_gco2 < 50 ? '#eab308' : '#ef4444'}
            subtext={`${(carbon?.energy_consumed_kwh || 0).toFixed(6)} kWh`} />
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EmissionChart data={trends} title="Carbon & Score Trends" />
        <ResourceBarChart title="Resource Distribution"
          data={metrics
            ? [{ name: 'CPU', value: metrics.cpu_usage }, { name: 'Memory', value: metrics.memory_usage },
               { name: 'Disk', value: metrics.disk_usage }, { name: 'Network', value: Math.min(metrics.network_usage * 10, 100) }]
            : ['CPU', 'Memory', 'Disk', 'Network'].map(name => ({ name, value: 0 }))} />
      </div>

      {/* Carbon Breakdown */}
      {carbon && (
        <div className="card p-5">
          <h3 className="text-green-300 font-semibold font-mono text-sm mb-4">Carbon Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(carbon.power_breakdown_watts || {}).map(([key, val]) => (
              <CarbonStatCard key={key} label={key} value={`${val.toFixed(3)} W`} />
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-6 text-xs font-mono text-green-600">
            <span>Region: <span className="text-green-400">{carbon.region}</span></span>
            <span>Intensity: <span className="text-green-400">{carbon.carbon_intensity_gco2_kwh} gCO2/kWh</span></span>
            <span>Total Power: <span className="text-green-400">{carbon.total_power_watts?.toFixed(2)} W</span></span>
            <span>Energy: <span className="text-green-400">{carbon.energy_consumed_kwh?.toFixed(6)} kWh</span></span>
          </div>
        </div>
      )}

      {/* Certificate */}
      <div className="card p-6 text-center">
        <Award size={32} className="text-green-400 mx-auto mb-3" />
        <h3 className="text-green-300 font-semibold font-mono text-sm mb-2">GreenCode Certificate</h3>
        <p className="text-green-700 font-mono text-xs mb-4">Get a blockchain-verified certificate of your sustainability achievements</p>
        <button onClick={() => generateCert(setLoading)} disabled={loading} className="btn-primary">
          <Award size={16} className="mr-2" />Issue Certificate
        </button>
      </div>

      {/* AI Suggestions */}
      <SuggestionsSection title="AI Optimization Suggestions" suggestions={suggestions} emptyText='Run a scan to get AI-powered optimization suggestions' />

      {/* Code Scan Results */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Download size={16} className="text-green-400" />
          <h2 className="text-green-300 font-semibold font-mono text-sm">Code Scan Results</h2>
          {cs && <span className="ml-auto text-xs text-green-700 font-mono">Last scan: {new Date().toLocaleTimeString()}</span>}
        </div>

        <div className="flex justify-center mb-6">
          <GreenScoreRing score={cs?.green_score || 0} size={120} label="Code Green Score" />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <MetricCard icon={Cpu} label="Avg Complexity" value={cs?.avg_complexity?.toFixed(1) ?? '--'} unit="" color="text-blue-400" />
          <MetricCard icon={HardDrive} label="Avg Lines/File" value={cs?.avg_lines_per_file?.toFixed(0) ?? '--'} unit="" color="text-purple-400" />
          <MetricCard icon={MemoryStick} label="Total Files" value={cs?.total_files ?? '--'} unit="" color="text-green-400" />
          <MetricCard icon={Wifi} label="Issues Found" value={cs?.issues?.length ?? '--'} unit="" color="text-red-400" />
          <MetricCard icon={Zap} label="Est. Power" value={cs?.estimated_power_watts?.toFixed(2) ?? '--'} unit="W" color="text-yellow-400" />
          <MetricCard icon={Leaf} label="Est. Carbon" value={cs?.estimated_carbon_gco2?.toFixed(4) ?? '--'} unit="gCO2" color="text-green-400" />
        </div>

        <div className="card p-5 mb-6">
          <h3 className="text-green-300 font-semibold font-mono text-sm mb-4">Code Resource Analysis</h3>
          <ResourceBarChart title="Code Metrics" data={[
            { name: 'Complexity', value: cs ? Math.min(cs.avg_complexity || 0, 20) : 0 },
            { name: 'Lines/File', value: cs ? Math.min(cs.avg_lines_per_file || 0, 200) : 0 },
            { name: 'Issues', value: cs?.issues?.length || 0 },
            { name: 'Green Score', value: cs?.green_score || 0 },
          ]} />
        </div>

        <div className="card p-5 mb-6">
          <h3 className="text-green-300 font-semibold font-mono text-sm mb-4">Code Carbon & Score Trends</h3>
          <EmissionChart data={cs ? [{
            timestamp: 'Current Scan',
            carbon_emissions: cs.estimated_carbon_gco2 || 0,
            energy_consumption: cs.estimated_energy_kwh || 0,
            green_score: cs.green_score || 0,
          }] : []} title="Code Trends" />
        </div>

        <div className="card p-5 mb-6">
          <h3 className="text-green-300 font-semibold font-mono text-sm mb-4">Code Carbon Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[['Complexity Power', cs ? (cs.estimated_power_watts * 0.6).toFixed(2) : '--'],
              ['Memory Power',     cs ? (cs.estimated_power_watts * 0.3).toFixed(2) : '--'],
              ['Disk Power',       cs ? (cs.estimated_power_watts * 0.1).toFixed(2) : '--'],
              ['Total Power',      cs ? cs.estimated_power_watts?.toFixed(2)         : '--'],
            ].map(([label, val]) => <CarbonStatCard key={label} label={label} value={`${val} W`} />)}
          </div>
          <div className="mt-4 flex flex-wrap gap-6 text-xs font-mono text-green-600">
            <span>Region: <span className="text-green-400">{cs?.carbon_region ?? '--'}</span></span>
            <span>Intensity: <span className="text-green-400">{cs ? `${cs.carbon_intensity_gco2_kwh} gCO2/kWh` : '--'}</span></span>
            <span>Energy: <span className="text-green-400">{cs ? `${cs.estimated_energy_kwh?.toFixed(6)} kWh` : '--'}</span></span>
          </div>
        </div>

        {cs?.issues?.length > 0 && <IssuesBreakdown issues={cs.issues} />}

        <SuggestionsSection title="Code AI Optimization Suggestions" suggestions={codeSuggestions}
          emptyText={cs ? 'AI suggestions will appear after code scan' : 'Click "Scan Code" to get AI-powered optimization suggestions'} />
      </div>
    </div>
  );
}

function SuggestionsSection({ title, suggestions, emptyText }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Zap size={16} className="text-green-400" />
        <h2 className="text-green-300 font-semibold font-mono text-sm">{title}</h2>
        {suggestions.length > 0 && <span className="ml-auto text-xs text-green-700 font-mono">{suggestions.length} recommendations</span>}
      </div>
      {suggestions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestions.map((s, i) => <SuggestionCard key={i} suggestion={s} index={i} />)}
        </div>
      ) : (
        <div className="card p-8 text-center">
          <Zap size={32} className="text-green-800 mx-auto mb-3" />
          <p className="text-green-700 font-mono text-sm">{emptyText}</p>
        </div>
      )}
    </div>
  );
}