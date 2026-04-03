import React from 'react';
import { IndianRupee } from 'lucide-react';

const WalletSummary = ({ balance }) => {
  return (
    <div className="bg-gradient-to-br from-orange-50 via-white to-red-50 rounded-3xl shadow-xl p-8 flex items-center justify-between relative overflow-hidden group border-2 border-orange-200">
      <div className="absolute top-0 right-0 w-full h-full bg-grid-orange/[0.02] bg-[length:32px_32px]"></div>
      <div className="absolute top-0 right-0 w-64 h-64 bg-orange-200/20 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-orange-200/30 transition-all duration-700"></div>
      
      <div className="relative z-10">
        <p className="text-sm text-orange-600 font-medium mb-2 uppercase tracking-widest">InsureX Protected Wallet</p>
        <div className="flex items-baseline text-orange-600">
          <span className="text-5xl font-semibold opacity-90 mr-1">₹</span>
          <span className="text-7xl font-extrabold tracking-tighter text-gray-900">{balance}</span>
        </div>
      </div>
      
      <div className="relative z-10 bg-green-100/80 backdrop-blur-md border-2 border-green-300 px-6 py-4 rounded-2xl hidden sm:block">
         <div className="flex items-center space-x-2">
           <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse"></div>
           <p className="text-sm text-green-700 font-bold uppercase tracking-widest">Live Auto-Claim Sync</p>
         </div>
      </div>
    </div>
  );
};

export default WalletSummary;
