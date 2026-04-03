import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Shield, Wallet, Zap, TrendingUp, Activity, AlertCircle, CheckCircle2, MapPin, Cloud, Droplets } from 'lucide-react';
import api from '../services/api';
import Layout from '../components/Layout';

const Dashboard = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    wallet: null,
    policy: null,
    claims: [],
    autoClaimStatus: false
  });
  const [weather, setWeather] = useState({
    city: 'Loading...',
    temperature: 0,
    condition: 'Unknown',
    wind: 0,
    risk_level: 'low',
    lat: null,
    lon: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const userStr = sessionStorage.getItem('user');
        const token = sessionStorage.getItem('token');
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');
        
        if (!userStr || !token || !isLoggedIn) {
          return navigate('/login');
        }

        const user = JSON.parse(userStr);
        setUserData(user);

        if (user.user_id) {
          const [walletRes, policyRes, claimsRes] = await Promise.all([
            api.get(`/wallet?user_id=${user.user_id}`).catch(() => ({ data: null })),
            api.get(`/policy/status?user_id=${user.user_id}`).catch(() => ({ data: null })),
            api.get(`/claims?user_id=${user.user_id}`).catch(() => ({ data: { claims: [] } }))
          ]);

          setDashboardData({
            wallet: walletRes?.data,
            policy: policyRes?.data,
            claims: claimsRes?.data?.claims || [],
            autoClaimStatus: true
          });
        }

        // Get user location and fetch weather
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            async (position) => {
              const { latitude, longitude } = position.coords;
              console.log(`📍 Location detected: ${latitude}, ${longitude}`);
              
              try {
                const weatherRes = await api.post('/api/auth/weather', {
                  lat: latitude,
                  lon: longitude
                });
                
                setWeather(weatherRes.data);
                console.log('✅ Weather fetched:', weatherRes.data);
              } catch (err) {
                console.error('Weather API error:', err);
                setWeather(prev => ({
                  ...prev,
                  city: 'Location found',
                  lat: latitude,
                  lon: longitude
                }));
              }
            },
            (error) => {
              console.warn('Geolocation error:', error.message);
              setWeather(prev => ({
                ...prev,
                city: 'Location unavailable'
              }));
            }
          );
        }
      } catch (err) {
        console.error("Dashboard Error:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
    // Auto-refresh weather every 3 minutes (180000ms)
    const interval = setInterval(fetchDashboardData, 180000);
    return () => clearInterval(interval);
  }, [navigate]);

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64 text-gray-600">Loading...</div>
      </Layout>
    );
  }

  const isVerified = userData?.email && userData?.phone;
  const policyActive = dashboardData.policy?.status === 'active';
  const balance = dashboardData.wallet?.balance || 0;
  const claimCount = dashboardData.claims?.length || 0;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
        
        {/* MAIN GRID: 2 Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          
          {/* LEFT SIDE (70% - col-span-2) */}
          <div className="lg:col-span-2 space-y-6">

            {/* 1. PROFILE CARD */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {userData?.name?.[0] || 'W'}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{userData?.name || 'Worker'}</h2>
                    <p className="text-sm text-gray-600 mt-1">📧 {userData?.email || 'email@example.com'}</p>
                    <p className="text-sm text-gray-600">🆔 {userData?.worker_id || 'Worker-ID'}</p>
                    <div className="flex gap-4 mt-2 text-sm text-gray-600">
                      <span>📍 {userData?.city || 'City'}</span>
                      <span>🚚 {userData?.platform || 'Platform'}</span>
                    </div>
                  </div>
                </div>
                
                {isVerified ? (
                  <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full flex items-center gap-2 font-bold text-sm">
                    <CheckCircle2 className="w-5 h-5" />
                    ✅ Verified
                  </div>
                ) : (
                  <div className="bg-yellow-100 text-yellow-700 px-4 py-2 rounded-full flex items-center gap-2 font-bold text-sm">
                    <AlertCircle className="w-5 h-5" />
                    ⚠️ Pending
                  </div>
                )}
              </div>
            </div>

            {/* 2. WALLET CARD */}
            <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-7 border border-orange-200 shadow-md hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Wallet className="w-6 h-6 text-orange-600" />
                  <h3 className="text-xl font-bold text-gray-900">InsureX Wallet</h3>
                </div>
                <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                  Auto-Claim Enabled
                </span>
              </div>
              <div className="text-5xl font-bold text-orange-600">₹{balance}</div>
              <p className="text-sm text-gray-600 mt-2">Available balance • Active account</p>
            </div>

            {/* 3. INSURANCE PLAN CARD */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-3 mb-5">
                <Shield className="w-6 h-6 text-blue-600" />
                <h3 className="text-xl font-bold text-gray-900">Your Insurance Plan</h3>
              </div>
              
              {policyActive ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-xl p-5 border border-blue-200">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 font-medium">Weekly Premium</p>
                        <p className="text-2xl font-bold text-blue-600 mt-1">₹{dashboardData.policy?.premium || 38}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 font-medium">Coverage Hours</p>
                        <p className="text-lg font-bold text-gray-900 mt-1">8 AM – 8 PM</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 font-medium">Risk Zone</p>
                        <p className="text-lg font-bold text-gray-900 mt-1">{dashboardData.policy?.zone || 'Zone-A'}</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
                    <p className="text-green-800 font-medium">✅ Active until {new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}</p>
                  </div>
                  <button onClick={() => navigate('/buy-policy')} className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition-colors">
                    Renew Coverage
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-red-50 rounded-xl p-5 border border-red-200">
                    <p className="text-red-800 font-bold">⚠️ No Active Coverage</p>
                    <p className="text-red-700 text-sm mt-1">Activate a plan to receive automatic claim payouts.</p>
                  </div>
                  <button 
                    onClick={() => navigate('/buy-policy')} 
                    disabled={!isVerified}
                    className={`w-full py-3 rounded-lg font-bold transition-colors ${
                      isVerified 
                        ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white' 
                        : 'bg-gray-300 text-gray-600 cursor-not-allowed'
                    }`}
                  >
                    Buy Coverage Now
                  </button>
                  {!isVerified && <p className="text-xs text-red-600 text-center font-medium">Only verified workers can purchase coverage</p>}
                </div>
              )}
            </div>

            {/* 4. AUTO CLAIM SYSTEM CARD (MAIN FEATURE) */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-7 border border-purple-200 shadow-md hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-600 p-2 rounded-full">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">Auto Claim System</h3>
                </div>
                <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                  Live Monitoring
                </span>
              </div>

              <div className="bg-white rounded-xl p-5 mb-4 border border-purple-100">
                <p className="text-sm text-gray-600 font-medium mb-2">System Status</p>
                <p className="text-lg font-bold text-purple-600">🟢 Real-time Monitoring Active</p>
                <p className="text-xs text-gray-600 mt-2">Claims triggered automatically during weather disruptions</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-lg p-4 border border-purple-100 flex items-start gap-3">
                  <Cloud className="w-5 h-5 text-blue-500 flex-shrink-0 mt-1" />
                  <div>
                    <p className="text-sm font-bold text-gray-900">Weather API</p>
                    <p className="text-xs text-gray-600">Temperature, Wind, Rain</p>
                  </div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-purple-100 flex items-start gap-3">
                  <Droplets className="w-5 h-5 text-amber-500 flex-shrink-0 mt-1" />
                  <div>
                    <p className="text-sm font-bold text-gray-900">Flood Alerts</p>
                    <p className="text-xs text-gray-600">Real-time notifications</p>
                  </div>
                </div>
              </div>

              <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
                <p className="text-blue-800 text-sm font-medium">💡 How it works: When disruptions are detected, claims are automatically processed. No paperwork needed!</p>
              </div>
            </div>

            {/* 4B. LIVE LOCATION & WEATHER CARD (NEW) */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-7 border-2 border-cyan-200 shadow-md hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <Cloud className="w-6 h-6 text-blue-600" />
                  <h3 className="text-xl font-bold text-gray-900">Live Location & Weather</h3>
                </div>
                <span className="text-xl">📍</span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-5">
                <div className="bg-white rounded-lg p-4 border border-cyan-200">
                  <p className="text-sm text-gray-600 font-medium mb-1">📍 Location</p>
                  <p className="text-lg font-bold text-gray-900">{weather.city}</p>
                  {weather.lat && <p className="text-xs text-gray-500 mt-1">{weather.lat.toFixed(2)}, {weather.lon.toFixed(2)}</p>}
                </div>

                <div className="bg-white rounded-lg p-4 border border-cyan-200">
                  <p className="text-sm text-gray-600 font-medium mb-1">🌡 Temperature</p>
                  <p className="text-lg font-bold text-red-600">{weather.temperature}°C</p>
                </div>

                <div className="bg-white rounded-lg p-4 border border-cyan-200">
                  <p className="text-sm text-gray-600 font-medium mb-1">🌧 Condition</p>
                  <p className="text-lg font-bold text-gray-900">{weather.condition}</p>
                </div>

                <div className="bg-white rounded-lg p-4 border border-cyan-200">
                  <p className="text-sm text-gray-600 font-medium mb-1">🌬 Wind Speed</p>
                  <p className="text-lg font-bold text-blue-600">{weather.wind} m/s</p>
                </div>
              </div>

              {/* Risk Level Indicator */}
              <div className={`rounded-lg p-4 border-2 text-center ${
                weather.risk_level === 'high' ? 'bg-red-100 border-red-400' :
                weather.risk_level === 'medium' ? 'bg-yellow-100 border-yellow-400' :
                'bg-green-100 border-green-400'
              }`}>
                <p className="text-xs text-gray-600 font-medium mb-1">⚠️ RISK LEVEL</p>
                <p className={`text-xl font-bold uppercase ${
                  weather.risk_level === 'high' ? 'text-red-700' :
                  weather.risk_level === 'medium' ? 'text-yellow-700' :
                  'text-green-700'
                }`}>
                  {weather.risk_level === 'high' ? '🔴 HIGH' :
                   weather.risk_level === 'medium' ? '🟡 MEDIUM' :
                   '🟢 LOW'}
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  {weather.risk_level === 'high' ? 'High disruption risk - Claims may be triggered' :
                   weather.risk_level === 'medium' ? 'Moderate risk - Stay alert' :
                   'Safe conditions - Regular work'}
                </p>
              </div>
            </div>

            {/* 5. CLAIMS HISTORY */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-3 mb-5">
                <TrendingUp className="w-6 h-6 text-green-600" />
                <h3 className="text-xl font-bold text-gray-900">Recent Payouts</h3>
              </div>
              
              {claimCount > 0 ? (
                <div className="space-y-3">
                  {dashboardData.claims.slice(0, 5).map((claim, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors">
                      <div className="flex items-center gap-4">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <div>
                          <p className="font-bold text-gray-900">Weather Disruption Claim</p>
                          <p className="text-sm text-gray-600">{new Date().toLocaleDateString()}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">+₹500</p>
                        <p className="text-xs text-green-700 font-medium">Processed</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-600 font-medium">No claims yet</p>
                  <p className="text-sm text-gray-500">Claims will appear when disruptions are detected</p>
                </div>
              )}
            </div>

            {/* 6. ACTIVITY TIMELINE */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100 hover:shadow-lg transition-shadow">
              <h3 className="text-xl font-bold text-gray-900 mb-5">Activity Timeline</h3>
              
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="w-3 h-3 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div className="pb-4 border-b border-slate-200 last:border-0 flex-grow">
                    <p className="font-bold text-gray-900">✅ Email Verified</p>
                    <p className="text-sm text-gray-600">{new Date().toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-3 h-3 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div className="pb-4 border-b border-slate-200 last:border-0 flex-grow">
                    <p className="font-bold text-gray-900">✅ Worker ID Verified</p>
                    <p className="text-sm text-gray-600">{userData?.platform} • {userData?.city}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div className="flex-grow">
                    <p className="font-bold text-gray-900">📋 Account Registered</p>
                    <p className="text-sm text-gray-600">Welcome to InsureX!</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT SIDE (30% - col-span-1) */}
          <div className="lg:col-span-1 space-y-6">

            {/* 7. COVERAGE STATUS */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Coverage Status</h3>
              
              {policyActive ? (
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-300 text-center">
                  <div className="text-4xl mb-3">🛡️</div>
                  <p className="font-bold text-lg text-green-700">Coverage Active</p>
                  <p className="text-sm text-green-600 mt-2">Protected until</p>
                  <p className="font-bold text-gray-900 mt-1">{new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}</p>
                </div>
              ) : (
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 border-2 border-amber-300 text-center">
                  <div className="text-4xl mb-3">⚠️</div>
                  <p className="font-bold text-lg text-amber-700">No Coverage</p>
                  <p className="text-sm text-amber-600 mt-2">Activate a plan now</p>
                </div>
              )}
            </div>

            {/* 8. QUICK ACTIONS */}
            <div className="bg-white rounded-2xl p-7 shadow-md border border-slate-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
              
              <div className="space-y-3">
                <button 
                  onClick={() => navigate('/buy-policy')}
                  className="w-full flex items-center justify-between bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-5 py-3 rounded-xl font-bold transition-all transform hover:-translate-y-0.5"
                >
                  <span>💳 Buy Policy</span>
                  <ChevronRight className="w-5 h-5" />
                </button>

                <button 
                  onClick={() => navigate('/history')}
                  className="w-full flex items-center justify-between bg-slate-100 hover:bg-slate-200 text-gray-900 px-5 py-3 rounded-xl font-bold transition-all"
                >
                  <span>📊 View Claims</span>
                  <ChevronRight className="w-5 h-5" />
                </button>

                <button 
                  className="w-full flex items-center justify-between bg-slate-100 hover:bg-slate-200 text-gray-900 px-5 py-3 rounded-xl font-bold transition-all"
                >
                  <span>📞 Support</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* 9. RISK INSIGHTS */}
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-7 shadow-md border border-indigo-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Risk Insights</h3>
              
              <div className="space-y-4">
                <div className="bg-white rounded-lg p-4 border border-indigo-200">
                  <p className="text-sm text-gray-600 font-medium">Risk Zone</p>
                  <p className="text-2xl font-bold text-indigo-600 mt-1">{dashboardData.policy?.zone || 'Zone-A'}</p>
                </div>

                <div className="bg-white rounded-lg p-4 border border-indigo-200">
                  <p className="text-sm text-gray-600 font-medium">Weather Risk</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="h-2 flex-grow bg-green-400 rounded-full"></div>
                    <p className="text-sm font-bold text-green-600">Low</p>
                  </div>
                </div>

                <div className="bg-indigo-100 rounded-lg p-4 border border-indigo-300">
                  <p className="text-indigo-800 text-sm font-medium">
                    💡 <strong>Smart Tip:</strong> Your area has low weather risk, keeping your premium affordable.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;

