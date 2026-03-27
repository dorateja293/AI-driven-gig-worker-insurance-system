import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { claimsAPI } from '../api/api';
import Layout from '../components/Layout';

const HistoryPage = () => {
  const { user } = useAuth();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, paid, pending, flagged

  useEffect(() => {
    if (user) {
      loadClaims();
    }
  }, [user]);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const response = await claimsAPI.getUserClaims(user.user_id);
      setClaims(response.data.claims);
      setLoading(false);
    } catch (error) {
      console.error('Error loading claims:', error);
      setLoading(false);
    }
  };

  const filteredClaims = claims.filter((claim) => {
    if (filter === 'all') return true;
    return claim.status === filter;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'approved':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'flagged':
        return 'bg-red-100 text-red-800';
      case 'rejected':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-xl text-gray-600">Loading claims history...</div>
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
            Claims History 📜
          </h2>
          <p className="text-gray-600">
            View all your insurance claims and their statuses
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'all'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Claims ({claims.length})
            </button>
            <button
              onClick={() => setFilter('paid')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'paid'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Paid ({claims.filter((c) => c.status === 'paid').length})
            </button>
            <button
              onClick={() => setFilter('pending')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'pending'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Pending ({claims.filter((c) => c.status === 'pending').length})
            </button>
            <button
              onClick={() => setFilter('approved')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'approved'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Approved ({claims.filter((c) => c.status === 'approved').length})
            </button>
            <button
              onClick={() => setFilter('flagged')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'flagged'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Flagged ({claims.filter((c) => c.status === 'flagged').length})
            </button>
          </div>
        </div>

        {/* Claims List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {filteredClaims.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                No Claims Found
              </h3>
              <p className="text-gray-500">
                {filter === 'all'
                  ? 'You have no claims yet. Claims will appear here when events are triggered.'
                  : `No ${filter} claims found.`}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredClaims.map((claim) => (
                <div
                  key={claim.claim_id}
                  className="p-6 hover:bg-gray-50 transition"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        {claim.event_type.replace(/_/g, ' ').toUpperCase()}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {claim.trigger_value}
                      </p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                claim.status
                      )}`}
                    >
                      {claim.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Payout Amount:</span>
                      <span className="ml-2 font-semibold text-green-600">
                        ₹{claim.payout_amount}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Claim ID:</span>
                      <span className="ml-2 font-mono text-xs text-gray-700">
                        {claim.claim_id}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Date:</span>
                      <span className="ml-2 text-gray-700">
                        {new Date(claim.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Time:</span>
                      <span className="ml-2 text-gray-700">
                        {new Date(claim.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {claims.length > 0 && (
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow p-6 text-white">
            <h3 className="text-xl font-bold mb-4">Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-2xl font-bold">
                  {claims.filter((c) => c.status === 'paid').length}
                </div>
                <div className="text-sm opacity-90">Paid Claims</div>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  ₹
                  {claims
                    .filter((c) => c.status === 'paid')
                    .reduce((sum, c) => sum + c.payout_amount, 0)
                    .toFixed(2)}
                </div>
                <div className="text-sm opacity-90">Total Received</div>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {claims.filter((c) => c.status === 'pending').length}
                </div>
                <div className="text-sm opacity-90">Pending Claims</div>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {claims.filter((c) => c.status === 'flagged').length}
                </div>
                <div className="text-sm opacity-90">Flagged Claims</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default HistoryPage;
