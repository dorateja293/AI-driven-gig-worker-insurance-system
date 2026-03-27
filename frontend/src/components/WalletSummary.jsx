import React from 'react';
import { IndianRupee } from 'lucide-react';

const WalletSummary = ({ balance }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-900 via-[#101935] to-indigo-950 rounded-[2rem] shadow-2xl p-8 flex items-center justify-between relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-full h-full bg-grid-white/[0.02] bg-[length:32px_32px]"></div>
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-indigo-500/30 transition-all duration-700"></div>
      
      <div className="relative z-10">
        <p className="text-sm text-indigo-200/80 font-medium mb-2 uppercase tracking-widest">InsureX Protected Wallet</p>
        <div className="flex items-baseline text-emerald-400">
          <span className="text-5xl font-semibold opacity-90 mr-1">₹</span>
          <span className="text-7xl font-extrabold tracking-tighter">{balance}</span>
        </div>
      </div>
      
      <div className="relative z-10 bg-emerald-500/10 backdrop-blur-md border border-emerald-500/20 px-6 py-4 rounded-2xl hidden sm:block">
         <div className="flex items-center space-x-2">
           <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
           <p className="text-sm text-emerald-300 font-bold uppercase tracking-widest">Live Auto-Claim Sync</p>
         </div>
      </div>
    </div>
  );
};

export default WalletSummary;
