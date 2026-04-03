import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Zap, Shield, TrendingUp } from 'lucide-react';
import api from '../services/api';
import Layout from '../components/Layout';

const BuyPolicy = () => {
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [quote, setQuote] = useState(null);

  useEffect(() => {
    const user = sessionStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        api.get(`/policy/quote?user_id=${userData.user_id}`)
          .then(res => setQuote(res.data))
          .catch(err => console.error("Quote API:", err));
      } catch (e) {
        console.log("No user session");
      }
    }
  }, []);

  // Weekly pricing plans
  const plans = {
    basic: {
      name: 'Basic Protection',
      price: 25,
      period: 'per week',
      icon: Shield,
      color: 'from-blue-500 to-blue-600',
      features: [
        'Extreme Heat Coverage (₹200)',
        'Heavy Rainfall Coverage (₹200)',
        'Email Support',
        '5-minute OTP verification'
      ]
    },
    standard: {
      name: 'Standard Coverage',
      price: 38,
      period: 'per week',
      icon: Zap,
      color: 'from-orange-500 to-red-600',
      features: [
        'All Basic features',
        'Platform Outage Coverage (₹150)',
        'Severe Smog Coverage (₹100)',
        'Priority Support',
        'Instant claim payouts',
        'Risk Assessment Dashboard'
      ],
      badge: 'Most Popular'
    },
    premium: {
      name: 'Premium Plus',
      price: 49,
      period: 'per week',
      icon: TrendingUp,
      color: 'from-yellow-500 to-orange-600',
      features: [
        'All Standard features',
        'Internet Blackout Coverage (₹120)',
        'Multi-delivery platform coverage',
        '24/7 Priority Support',
        'Monthly bonus credits',
        'Advanced fraud detection',
        'Family coverage available'
      ],
      badge: '🔥 Best Value'
    }
  };

  const handlePurchase = async () => {
    const user = sessionStorage.getItem('user');
    if (!user) {
      navigate('/login');
      return;
    }

    setLoading(true);
    try {
      const userData = JSON.parse(user);
      const plan = plans[selectedPlan];
      
      await api.post('/policy/purchase', {
        user_id: userData.user_id,
        premium_amount: plan.price,
        plan_type: selectedPlan
      });

      // Show success and navigate
      alert(`✅ ${plan.name} activated! Weekly premium: ₹${plan.price}`);
      navigate('/dashboard');
    } catch (err) {
      console.error('Purchase error:', err);
      alert('Purchase failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="fixed inset-0 bg-gradient-to-br from-white via-orange-50 to-white pt-20 pb-12 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-3">
              Weekly Protection Plans
            </h1>
            <p className="text-gray-600 text-lg">Safe delivery. Secured future.</p>
          </div>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {Object.entries(plans).map(([key, plan]) => {
              const IconComponent = plan.icon;
              const isSelected = selectedPlan === key;
              
              return (
                <div
                  key={key}
                  onClick={() => setSelectedPlan(key)}
                  className={`rounded-3xl p-8 cursor-pointer transition-all transform hover:-translate-y-2 border-2 ${
                    isSelected
                      ? `border-orange-500 bg-white shadow-2xl scale-105 ${
                          key === 'standard' ? 'shadow-orange-500/30' : ''
                        }`
                      : 'border-gray-200 bg-gray-50 hover:border-orange-300'
                  }`}
                >
                  {/* Badge */}
                  {plan.badge && (
                    <div className="mb-4">
                      <span className="inline-block bg-gradient-to-r from-orange-400 to-red-500 text-white px-4 py-1 rounded-full text-sm font-bold">
                        {plan.badge}
                      </span>
                    </div>
                  )}

                  {/* Icon and Title */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`bg-gradient-to-br ${plan.color} p-3 rounded-full`}>
                      <IconComponent className="text-white w-6 h-6" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                  </div>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-extrabold text-orange-600">₹{plan.price}</span>
                      <span className="text-gray-600 font-medium">/ {plan.period}</span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-3 mb-8">
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700 text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Select Button */}
                  <button
                    onClick={() => setSelectedPlan(key)}
                    className={`w-full py-3 rounded-2xl font-bold transition-all ${
                      isSelected
                        ? `bg-gradient-to-r ${plan.color} text-white shadow-lg`
                        : 'bg-white border-2 border-orange-300 text-orange-600 hover:bg-orange-50'
                    }`}
                  >
                    {isSelected ? '✓ Selected' : 'Select Plan'}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Purchase Section */}
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-3xl p-8 shadow-xl border-2 border-orange-100">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">
                📦 Order Summary
              </h2>

              <div className="space-y-4 mb-8 pb-6 border-b-2 border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-medium">Plan Selected:</span>
                  <span className="font-bold text-orange-600">{plans[selectedPlan].name}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-medium">Weekly Premium:</span>
                  <span className="text-2xl font-bold text-orange-600">₹{plans[selectedPlan].price}</span>
                </div>
                <div className="flex justify-between items-center text-sm text-gray-600">
                  <span>Auto-renew every 7 days</span>
                  <span>💳 Via your wallet balance</span>
                </div>
              </div>

              <button
                onClick={handlePurchase}
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-2xl font-bold text-lg shadow-xl transition-all active:scale-95"
              >
                {loading ? '⏳ Processing...' : `✓ Activate ${plans[selectedPlan].name}`}
              </button>

              <p className="text-center text-sm text-gray-600 mt-4">
                🔒 Secure payment • Auto-debit enabled • Cancel anytime
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BuyPolicy;
