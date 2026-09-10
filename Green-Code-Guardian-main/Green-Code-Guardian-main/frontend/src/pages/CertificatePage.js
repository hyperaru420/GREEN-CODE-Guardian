import React, { useState, useEffect } from 'react';
import { certificateAPI } from '../services/api';
import { Award, ExternalLink, Shield, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

const CertCard = ({ cert }) => {
  const score = cert.green_score || 0;
  const color = score >= 75 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444';

  const viewHtml = async () => {
    try {
      const response = await certificateAPI.getHtml(cert.certificate_id);
      const html = response.data;
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => URL.revokeObjectURL(url), 10000);
    } catch (error) {
      toast.error('Failed to open certificate.');
    }
  };

  return (
    <div className="card p-5 flex flex-col gap-3 hover:border-green-500/40 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: `${color}12`, border: `1px solid ${color}30` }}>
            <Award size={16} style={{ color }} />
          </div>
          <div>
            <div className="text-green-200 font-semibold text-sm">{cert.project_name}</div>
            <div className="text-green-700 text-xs font-mono">{cert.certificate_id}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="font-black font-mono text-2xl" style={{ color }}>{score}</div>
          <div className="text-green-700 text-xs">/ 100</div>
        </div>
      </div>

      <div className="space-y-1.5 text-xs font-mono">
        <div className="flex justify-between">
          <span className="text-green-700">Carbon</span>
          <span className="text-green-400">{(cert.carbon_value || 0).toFixed(6)} gCO2</span>
        </div>
        <div className="flex justify-between">
          <span className="text-green-700">Network</span>
          <span className={cert.network === 'mock' ? 'text-yellow-500' : 'text-green-400'}>
            {cert.network?.toUpperCase() || 'MOCK'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-green-700">Verified</span>
          {cert.verified
            ? <CheckCircle size={12} className="text-green-400" />
            : <XCircle size={12} className="text-yellow-500" />}
        </div>
        <div className="flex justify-between">
          <span className="text-green-700">Date</span>
          <span className="text-green-600">{cert.timestamp ? new Date(cert.timestamp).toLocaleDateString() : 'N/A'}</span>
        </div>
      </div>

      <div className="pt-2 border-t border-green-900/20">
        <div className="text-green-800 text-xs font-mono truncate mb-2">{cert.blockchain_hash?.slice(0, 32)}...</div>
        <div className="flex gap-2">
          <button onClick={viewHtml}
            className="btn-outline flex-1 py-1.5 rounded-lg text-xs font-mono flex items-center justify-center gap-1.5">
            <ExternalLink size={11} /> View Certificate
          </button>
          {cert.explorer_url && (
            <a href={cert.explorer_url} target="_blank" rel="noreferrer"
              className="btn-outline px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1.5">
              <Shield size={11} /> Explorer
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default function CertificatePage() {
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await certificateAPI.list();
      setCerts(res.data.certificates || []);
    } catch { toast.error('Failed to load certificates'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Award size={18} className="text-green-400" />
          <h1 className="text-xl font-black text-green-300 font-mono">Certificates</h1>
        </div>
        <button onClick={load} className="btn-outline px-4 py-2 rounded-lg text-sm font-mono flex items-center gap-2">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {/* Info banner */}
      <div className="card p-4 flex items-start gap-3 border-green-500/20">
        <Shield size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
        <div className="text-xs font-mono text-green-600">
          Certificates are generated from scan results and stored on blockchain. 
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48"><div className="w-8 h-8 spinner" /></div>
      ) : certs.length === 0 ? (
        <div className="card p-12 text-center">
          <Award size={40} className="text-green-900 mx-auto mb-3" />
          <p className="text-green-700 font-mono text-sm">No certificates yet</p>
          <p className="text-green-800 text-xs font-mono mt-1">Run a scan and click "Certify" from the Dashboard</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {certs.map((c, i) => <CertCard key={c._id || i} cert={c} />)}
        </div>
      )}
    </div>
  );
}
