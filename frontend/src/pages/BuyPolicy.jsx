import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/Layout';

const BuyPolicy = () => {
  const navigate = useNavigate();
  const [quote, setQuote] = useState({ risk_score: 0.72, premium: 38, zone: "Zone-A" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const user_id = localStorage.getItem('user_id');
    if (!user_id) return navigate('/register');
    
    api.get(`/policy/quote?user_id=${user_id}`)
      .then(res => setQuote(res.data))
      .catch(err => console.error("Waiting for backend...", err));
  }, []);

  const handlePurchase = async () => {
    setLoading(true);
    try {
      const user_id = localStorage.getItem('user_id');
      await api.post('/policy/purchase', { user_id, premium_amount: quote.weekly_premium || quote.premium });
    } catch (err) {
      console.error(err);
    }
    navigate('/dashboard');
  };

  return (
    <Layout>
      <div className="flex justify-center items-center py-12 flex-col">
        <div className="bg-white p-12 rounded-3xl shadow-2xl border-2 border-orange-100 w-full max-w-2xl transform transition-all">
          <h2 className="text-4xl font-extrabold text-center mb-10 bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent tracking-tight">AI Risk Profiler</h2>
          
          <div className="bg-gradient-to-br from-orange-50 to-white rounded-3xl p-8 mb-10 border-2 border-orange-100 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-orange-200 rounded-full blur-[80px] opacity-20 -mr-20 -mt-20"></div>
            
            <div className="relative z-10 flex justify-between items-center pb-8 border-b border-orange-200 mb-8">
              <div>
                 <p className="text-orange-600 font-medium tracking-wide mb-2 uppercase text-xs">Dynamic Quote ({quote.zone})</p>
                 <div className="flex items-baseline space-x-1">
                   <span className="text-4xl text-orange-600 font-bold">₹</span>
                   <span className="text-7xl font-extrabold text-gray-900 tracking-tighter">{quote.weekly_premium || quote.premium}</span>
                 </div>
              </div>
              <div className="text-right">
                 <p className="text-orange-600 font-medium tracking-wide mb-2 uppercase text-xs">Risk Index</p>
                 <div className="bg-orange-100 text-orange-700 border-2 border-orange-300 px-4 py-2 rounded-full inline-block">
                   <span className="text-2xl font-bold">{quote.risk_score}</span>
                 </div>
              </div>
            </div>
            
            <div className="relative z-10 space-y-4">
               <div className="flex items-center justify-between text-sm font-medium">
                 <span className="flex items-center text-gray-700"><span className="w-2 h-2 rounded-full bg-orange-500 mr-3"></span> Extreme Heat Coverage</span>
                 <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-bold border border-green-300">Included</span>
               </div>
               <div className="flex items-center justify-between text-sm font-medium">
                 <span className="flex items-center text-gray-700"><span className="w-2 h-2 rounded-full bg-orange-500 mr-3"></span> Heavy Rainfall</span>
                 <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-bold border border-green-300">Included</span>
               </div>
               <div className="flex items-center justify-between text-sm font-medium">
                 <span className="flex items-center text-gray-700"><span className="w-2 h-2 rounded-full bg-orange-500 mr-3"></span> Platform Outages</span>
                 <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-bold border border-green-300">Included</span>
               </div>
            </div>
          </div>

          <button onClick={handlePurchase} disabled={loading} className="w-full py-5 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-2xl font-bold text-xl shadow-xl shadow-orange-600/30 hover:shadow-orange-600/50 hover:-translate-y-1 active:scale-[0.98] transition-all">
            {loading ? 'Authorizing Auto-Debit...' : 'Activate Weekly Protection'}
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default BuyPolicy;
