import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import PolicyCard from '../components/PolicyCard';
import ClaimList from '../components/ClaimList';
import WalletSummary from '../components/WalletSummary';
import Layout from '../components/Layout';

const Dashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState({ wallet: null, policy: null, claims: [] });
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Check if user is logged in (from registration)
        const userStr = sessionStorage.getItem('user');
        const token = sessionStorage.getItem('token');
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');
        
        console.log('🔍 Dashboard Check:', { userStr, token, isLoggedIn });
        
        if (!userStr || !token || !isLoggedIn) {
          console.log('❌ Not logged in, redirecting to register');
          return navigate('/register');
        }

        const user = JSON.parse(userStr);
        console.log('✅ User logged in:', user);
        setUserData(user);

        // Fetch dashboard data if user_id exists
        if (user.user_id) {
          const [walletRes, policyRes, claimsRes] = await Promise.all([
            api.get(`/wallet?user_id=${user.user_id}`).catch(e => ({ data: null })),
            api.get(`/policy/status?user_id=${user.user_id}`).catch(() => ({ data: null })),
            api.get(`/claims?user_id=${user.user_id}`).catch(e => ({ data: { claims: [] } }))
          ]);

          setData({
            wallet: walletRes?.data,
            policy: policyRes?.data,
            claims: claimsRes?.data?.claims || []
          });
        }
      } catch (err) {
        console.error("Dashboard Sync Error:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 3000); 
    return () => clearInterval(interval);
  }, [navigate]);

  if (loading) return (
    <Layout>
       <div className="flex justify-center items-center h-64 text-orange-600 font-bold animate-pulse">Syncing Secure Data...</div>
    </Layout>
  );

  return (
    <Layout>
      <div className="space-y-6">
        <header className="mb-8">
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent tracking-tight">Worker Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1 font-medium">Auto-synced via Parametric API</p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Top: Wallet */}
            <WalletSummary wallet={data.wallet} />
            
            {/* Bottom: Claims */}
            <div className="bg-white p-6 rounded-2xl shadow-lg border-2 border-orange-100 transition-all duration-200 hover:shadow-xl hover:border-orange-200">
               <h3 className="text-lg font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-4 border-b border-orange-50 pb-3">Recent Payouts</h3>
               <ClaimList claims={data.claims} />
            </div>
          </div>
          
          <div className="lg:col-span-1 h-full">
            {/* Middle: Policy Component */}
            <PolicyCard policy={data.policy} onBuyClick={() => navigate('/buy-policy')} />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
