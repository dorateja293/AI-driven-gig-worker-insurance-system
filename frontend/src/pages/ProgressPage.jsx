import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { walletAPI } from '../api/api';
import Layout from '../components/Layout';

const ProgressPage = () => {
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, credit, debit

  useEffect(() => {
    if (user) {
      loadWalletData();
    }
  }, [user]);

  const loadWalletData = async () => {
    try {
      setLoading(true);
      const response = await walletAPI.getWallet(user.user_id);
      setWallet(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading wallet data:', error);
      setLoading(false);
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

      alert(`Successfully added ₹${amount} to your wallet!`);
      loadWalletData();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to top up wallet');
    }
  };

  const filteredTransactions = wallet?.transactions?.filter((txn) => {
    if (filter === 'all') return true;
    if (filter === 'credit') return txn.amount > 0;
    if (filter === 'debit') return txn.amount < 0;
    return true;
  });

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'claim_payout':
        return '💰';
      case 'premium_paid':
        return '📄';
      case 'top_up':
        return '➕';
      default:
        return '📊';
    }
  };

  const getTransactionColor = (amount) => {
    return amount > 0 ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-xl text-gray-600">Loading wallet data...</div>
        </div>
      </Layout>
    );
  }

  const totalCredit = wallet?.transactions
    ?.filter((t) => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0);

  const totalDebit = wallet?.transactions
    ?.filter((t) => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Financial Progress 💰
          </h2>
          <p className="text-gray-600">
            Track your wallet balance and transaction history
          </p>
        </div>

        {/* Wallet Balance Card */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-xl p-8 text-white">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg opacity-90 mb-2">Current Balance</h3>
              <div className="text-5xl font-bold">
                ₹{wallet?.balance?.toFixed(2) || '0.00'}
              </div>
            </div>
            <button
              onClick={handleTopUp}
              className="bg-white text-green-600 px-6 py-3 rounded-lg hover:bg-green-50 transition font-semibold shadow-md"
            >
              Top Up Wallet
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-8 pt-6 border-t border-green-400">
            <div>
              <div className="text-sm opacity-90 mb-1">Total Received</div>
              <div className="text-2xl font-bold">₹{totalCredit?.toFixed(2) || '0.00'}</div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Total Spent</div>
              <div className="text-2xl font-bold">₹{totalDebit?.toFixed(2) || '0.00'}</div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600">Total Transactions</span>
              <span className="text-2xl">📊</span>
            </div>
            <div className="text-3xl font-bold text-gray-800">
              {wallet?.transactions?.length || 0}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600">Payouts Received</span>
              <span className="text-2xl">💵</span>
            </div>
            <div className="text-3xl font-bold text-green-600">
              {wallet?.transactions?.filter((t) => t.type === 'claim_payout')
                .length || 0}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600">Premiums Paid</span>
              <span className="text-2xl">📄</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {wallet?.transactions?.filter((t) => t.type === 'premium_paid')
                .length || 0}
            </div>
          </div>
        </div>

        {/* Transaction Filter */}
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
              All Transactions ({wallet?.transactions?.length || 0})
            </button>
            <button
              onClick={() => setFilter('credit')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'credit'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Credits ({wallet?.transactions?.filter((t) => t.amount > 0).length || 0})
            </button>
            <button
              onClick={() => setFilter('debit')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'debit'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Debits ({wallet?.transactions?.filter((t) => t.amount < 0).length || 0})
            </button>
          </div>
        </div>

        {/* Transactions List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="bg-gray-50 px-6 py-3 border-b">
            <h3 className="font-semibold text-gray-800">Transaction History</h3>
          </div>

          {filteredTransactions?.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                No Transactions
              </h3>
              <p className="text-gray-500">
                Your transaction history will appear here.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredTransactions.map((txn) => (
                <div
                  key={txn.transaction_id}
                  className="p-6 hover:bg-gray-50 transition flex justify-between items-center"
                >
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">
                      {getTransactionIcon(txn.type)}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">
                        {txn.type
                          .split('_')
                          .map(
                            (word) =>
                              word.charAt(0).toUpperCase() + word.slice(1)
                          )
                          .join(' ')}
                      </div>
                      <div className="text-sm text-gray-600">
                        {txn.description}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(txn.date).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div
                      className={`text-2xl font-bold ${getTransactionColor(
                        txn.amount
                      )}`}
                    >
                      {txn.amount > 0 ? '+' : ''}₹{Math.abs(txn.amount).toFixed(2)}
                    </div>
                    <div className="text-xs font-mono text-gray-500 mt-1">
                      {txn.transaction_id}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ProgressPage;
