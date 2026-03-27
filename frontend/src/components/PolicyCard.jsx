import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';

const PolicyCard = ({ policy, onBuyClick }) => {
  // Inactive State
  if (!policy || policy.status !== 'active') {
    return (
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-red-100 flex flex-col justify-center h-full transition-all duration-200 hover:shadow-md group">
        <div className="mb-5 inline-flex p-3 bg-red-50 text-red-500 rounded-xl group-hover:scale-105 transition-transform duration-200">
           <ShieldAlert className="w-8 h-8" />
        </div>
        <h3 className="text-gray-900 font-extrabold text-2xl mb-2 tracking-tight">Coverage Inactive</h3>
        <p className="text-gray-500 mb-8 text-sm leading-relaxed">Your income is critically exposed to weather disruptions. Protect your gig today.</p>
        <button onClick={onBuyClick} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 active:scale-95 shadow-sm">
          Get Covered Instantly
        </button>
      </div>
    );
  }

  // Active State
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 h-full flex flex-col justify-between transition-all duration-200 hover:shadow-md relative overflow-hidden">
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-emerald-50 rounded-full blur-2xl z-0"></div>
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-5">
          <div className="inline-flex p-2.5 bg-emerald-50 text-emerald-600 rounded-xl">
             <ShieldCheck className="w-6 h-6" />
          </div>
          <span className="bg-emerald-100 border border-emerald-200 text-emerald-700 text-[11px] font-extrabold px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm">
            Active
          </span>
        </div>
        
        <h3 className="text-gray-900 font-extrabold text-2xl mb-1 tracking-tight">Protected</h3>
        <p className="text-gray-500 text-sm font-medium mb-8">Pays out dynamically via AI.</p>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 transition-colors hover:bg-white">
             <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1.5">Days Left</p>
             <p className="font-extrabold text-gray-900 text-2xl">{policy.days_remaining}</p>
          </div>
          <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100 flex flex-col justify-center items-center text-center transition-colors hover:bg-white">
             <Cpu className="w-4 h-4 text-indigo-500 mb-1" />
             <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider">AI Risk Map</p>
             <p className="font-extrabold text-indigo-700 text-xl leading-none mt-1.5">{policy.riskScore || 0.72}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PolicyCard;
