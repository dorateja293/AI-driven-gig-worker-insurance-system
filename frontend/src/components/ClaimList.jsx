import React from 'react';

const ClaimList = ({ claims }) => {
  const getStatusColor = (status) => {
    switch(status.toLowerCase()) {
      case 'paid': return 'bg-green-100 text-green-700 border-green-300';
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'flagged': return 'bg-red-100 text-red-700 border-red-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border-2 border-orange-100 p-6">
      <h3 className="text-gray-900 font-bold text-lg mb-4">Recent Claims</h3>
      
      {claims.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-6">No claims history.</p>
      ) : (
        <div className="space-y-3">
          {claims.map((claim, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-orange-50 hover:bg-orange-100 transition-colors rounded-xl border-2 border-orange-100 hover:border-orange-200">
              <div>
                <p className="font-semibold text-gray-900 text-sm mb-1">{claim.event_type || claim.type}</p>
                <p className="text-xs text-gray-500">{claim.timestamp || claim.date}</p>
              </div>
              <div className="flex flex-col items-end">
                <span className="font-bold text-gray-900 mb-1">₹{claim.payout_amount || claim.amount}</span>
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full tracking-wider border ${getStatusColor(claim.status)}`}>
                  {claim.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ClaimList;
