import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import api from '../services/api';
import AdminTriggerPanel from '../components/AdminTriggerPanel';
import Layout from '../components/Layout';

const AdminPanel = () => {
  const [logs, setLogs] = useState([]);
  const [flaggedClaims, setFlaggedClaims] = useState([]);

  useEffect(() => {
    const fetchFlagged = async () => {
      try {
        const res = await api.get('/fraud/flagged');
        setFlaggedClaims(res.data.flagged_claims || res.data || []);
      } catch(err) {
        console.error("Waiting for backend...", err);
      }
    };
    fetchFlagged();
    const interval = setInterval(fetchFlagged, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleSimulateLog = (message) => {
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prev]);
  };

  return (
    <Layout>
      <div className="pb-12">
        <div className="mb-10 text-center">
           <h1 className="text-4xl font-extrabold text-gray-900 flex items-center justify-center tracking-tight mb-2">
             <Activity className="w-10 h-10 mr-4 text-red-500" /> Admin Command Center
           </h1>
           <p className="text-gray-500 font-medium text-lg">Simulate market crashes and monitor the adversarial defense matrix.</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="col-span-1 border border-red-100 bg-white/50 backdrop-blur-md rounded-[2rem] p-8 shadow-xl">
            <AdminTriggerPanel onTrigger={handleSimulateLog} />
            
            <div className="mt-8 bg-gray-950 p-6 rounded-3xl h-64 overflow-y-auto font-mono text-xs text-emerald-400 shadow-inner border border-gray-800">
              <div className="text-gray-500 mb-4 uppercase tracking-widest font-bold">// Live System Logs //</div>
              {logs.map((log, i) => <div key={i} className="mb-2 leading-relaxed opacity-90">{log}</div>)}
              {logs.length === 0 && <span className="opacity-50">Awaiting events...</span>}
            </div>
          </div>

          <div className="col-span-2 glass p-10 rounded-[2rem]">
            <div className="flex justify-between items-center mb-10 pb-6 border-b border-gray-100">
              <h3 className="text-2xl font-extrabold text-gray-900 tracking-tight">Adversarial Defense Monitor</h3>
              <span className="bg-red-50 border border-red-200 text-red-600 text-xs font-extrabold px-4 py-2 rounded-full uppercase tracking-widest pulse-glow">
                Active Monitoring
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-gray-400 font-bold text-xs uppercase tracking-widest">
                    <th className="pb-4 pl-4">Claim ID</th>
                    <th className="pb-4">Machine Learning Flag Reason</th>
                    <th className="pb-4 text-center">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {flaggedClaims.map(fc => (
                    <tr key={fc.claim_id || fc.id} className="hover:bg-gray-50 transition-colors group">
                      <td className="py-5 pl-4 font-bold text-gray-900">{fc.claim_id || fc.id}</td>
                      <td className="py-5 text-sm text-gray-600 font-medium">
                        <span className="block text-gray-900 group-hover:text-indigo-600 transition-colors">{fc.reason}</span>
                        <span className="text-xs text-gray-400 mt-1 block uppercase tracking-wider">Entity: {fc.user_id}</span>
                      </td>
                      <td className="py-5 text-center">
                        <span className="bg-red-500/10 text-red-600 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider border border-red-500/20">
                          {fc.risk_level || 'CRITICAL'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {flaggedClaims.length === 0 && (
                    <tr>
                      <td colSpan="3" className="text-center py-10 text-gray-400 font-medium">No adversarial rings detected. System normal.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminPanel;
