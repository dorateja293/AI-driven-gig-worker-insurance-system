import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { policyAPI, walletAPI } from '../api/api';
import Layout from '../components/Layout';

const PolicyPage = () => {
  const { user } = useAuth();
  const [quote, setQuote] = useState(null);
  const [policyStatus, setPolicyStatus] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load wallet
      const walletRes = await walletAPI.getWallet(user.user_id);
      setWallet(walletRes.data);

      // Load policy status
      try {
        const policyRes = await policyAPI.getPolicyStatus(user.user_id);
        setPolicyStatus(policyRes.data);
      } catch (err) {
        setPolicyStatus(null);

        // If no policy, get quote
        const quoteRes = await policyAPI.getQuote(user.user_id);
        setQuote(quoteRes.data);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const handlePurchasePolicy = async () => {
    if (!quote) return;

    if (wallet.balance < quote.weekly_premium) {
      setMessage({
        type: 'error',
        text: 'Insufficient wallet balance. Please top up your wallet first.',
      });
      return;
    }

    try {
      setPurchasing(true);
      setMessage({ type: '', text: '' });

      await policyAPI.purchasePolicy({
        user_id: user.user_id,
        premium_amount: quote.weekly_premium,
      });

      setMessage({
        type: 'success',
        text: 'Policy purchased successfully! You are now covered for 7 days.',
      });

      // Reload data
      setTimeout(() => {
        loadData();
      }, 1500);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to purchase policy',
      });
    } finally {
      setPurchasing(false);
    }
  };

  const handleTopUp = async () => {
    try {
      const amount = prompt('Enter amount to top up (₹):');
      if (!amount || isNaN(amount) || amount <= 0) {
        return;
      }

      await walletAPI.topUp({
        user_id: user.user_id,
        amount: parseFloat(amount),
      });

      setMessage({
        type: 'success',
        text: `Successfully added ₹${amount} to your wallet!`,
      });

      loadData();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to top up wallet',
      });
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-xl text-gray-600">Loading policy information...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Policy Management 📋
          </h2>
          <p className="text-gray-600">
            Purchase and manage your insurance policy
          </p>
        </div>

        {/* Message */}
        {message.text && (
          <div
            className={`rounded-lg p-4 ${
              message.type === 'success'
                ? 'bg-green-100 text-green-800 border border-green-200'
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Wallet Balance */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-bold mb-1">Wallet Balance</h3>
              <div className="text-3xl font-bold">
                ₹{wallet?.balance?.toFixed(2) || '0.00'}
              </div>
            </div>
            <button
              onClick={handleTopUp}
              className="bg-white text-green-600 px-6 py-2 rounded-lg hover:bg-green-50 transition font-semibold"
            >
              Top Up
            </button>
          </div>
        </div>

        {policyStatus ? (
          /* Active Policy */
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  Active Policy ✓
                </h3>
                <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  {policyStatus.status.toUpperCase()}
                </span>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Policy ID</div>
                <div className="font-mono text-xs text-gray-800">
                  {policyStatus.policy_id}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Days Remaining</div>
                <div className="text-3xl font-bold text-blue-600">
                  {policyStatus.days_remaining}
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Claims This Week</div>
                <div className="text-3xl font-bold text-purple-600">
                  {policyStatus.claims_this_week}
                </div>
              </div>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-800 mb-2">Coverage Details</h4>
              <p className="text-gray-600 text-sm mb-2">
                Your policy covers the following events:
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-700">
                  <span className="mr-2">🔥</span>
                  Extreme Heat (&gt;43°C for 2+ hours) - ₹200 payout
                </li>
                <li className="flex items-center text-sm text-gray-700">
                  <span className="mr-2">🌧️</span>
                  Heavy Rain (&gt;50mm in 3 hours) - ₹200 payout
                </li>
                <li className="flex items-center text-sm text-gray-700">
                  <span className="mr-2">⚠️</span>
                  Platform Outage (30+ min downtime) - ₹150 payout
                </li>
              </ul>
            </div>
          </div>
        ) : quote ? (
          /* Policy Quote */
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 text-white">
              <h3 className="text-2xl font-bold mb-2">Get Protected Today!</h3>
              <p className="opacity-90">
                Smart AI-powered insurance tailored to your zone's risk profile
              </p>
            </div>

            <div className="p-6">
              {/* Risk Score */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700 font-semibold">Risk Score</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {(quote.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-green-500 to-yellow-500 h-3 rounded-full transition-all"
                    style={{ width: `${quote.risk_score * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Based on weather patterns and zone risk for {quote.zone}
                </p>
              </div>

              {/* Premium Price */}
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg p-6 mb-6 border border-yellow-200">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-1">
                    Weekly Premium
                  </div>
                  <div className="text-5xl font-bold text-orange-600 mb-2">
                    ₹{quote.weekly_premium}
                  </div>
                  <div className="text-sm text-gray-600">
                    Valid for 7 days of coverage
                  </div>
                </div>
              </div>

              {/* Coverage Details */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">
                  What's Covered
                </h4>
                <div className="space-y-3">
                  {quote.coverage_triggers.map((trigger) => (
                    <div
                      key={trigger}
                      className="flex items-center p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="text-2xl mr-3">
                        {trigger === 'extreme_heat'
                          ? '🔥'
                          : trigger === 'heavy_rain'
                          ? '🌧️'
                          : '⚠️'}
                      </span>
                      <div>
                        <div className="font-semibold text-gray-800">
                          {trigger.replace(/_/g, ' ').toUpperCase()}
                        </div>
                        <div className="text-sm text-gray-600">
                          Payout: ₹{quote.max_payout_per_event}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Purchase Button */}
              <button
                onClick={handlePurchasePolicy}
                disabled={purchasing || wallet.balance < quote.weekly_premium}
                className={`w-full py-4 rounded-lg font-bold text-lg transition ${
                  purchasing || wallet.balance < quote.weekly_premium
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-lg'
                }`}
              >
                {purchasing
                  ? 'Processing...'
                  : wallet.balance < quote.weekly_premium
                  ? 'Insufficient Balance - Top Up First'
                  : `Purchase Policy for ₹${quote.weekly_premium}`}
              </button>

              {wallet.balance < quote.weekly_premium && (
                <p className="text-center text-sm text-red-600 mt-2">
                  You need ₹{(quote.weekly_premium - wallet.balance).toFixed(2)}{' '}
                  more to purchase this policy.
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">😕</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Unable to Load Quote
            </h3>
            <p className="text-gray-500">
              Please try again or contact support.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default PolicyPage;
