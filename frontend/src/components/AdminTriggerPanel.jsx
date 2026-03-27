import React, { useState } from 'react';
import { Flame, CloudRain, ServerCrash, Wind, WifiOff } from 'lucide-react';
import api from '../services/api';

const AdminTriggerPanel = ({ onTrigger }) => {
  const [loading, setLoading] = useState(false);

  const simulateMapping = {
    'Heatwave': { type: 'extreme_heat', value: 46 },
    'Rainfall': { type: 'heavy_rain', value: 65 },
    'App Outage': { type: 'platform_outage', value: 45 },
    'Severe Smog': { type: 'severe_smog', value: 480 },
    'Blackout': { type: 'internet_blackout', value: 120 }
  };

  const handleSimulate = async (label) => {
    setLoading(true);
    const { type, value } = simulateMapping[label];
    try {
      await api.post('/events/simulate', {
        zone: "Zone-A",
        type,
        value,
        duration_hours: 3
      });
      onTrigger(`Successfully triggered ${label} in Zone A. Check Worker Dashboard.`);
    } catch (error) {
       onTrigger(`[Mock] System: Triggered ${label} in Zone-A -> Worker claims processing...`);
    }
    setLoading(false);
  };

  return (
    <div className="bg-red-50 p-6 rounded-2xl border border-red-200 shadow-sm h-full">
      <h3 className="text-red-800 font-bold text-lg mb-4">Simulate The 5 Demo Triggers</h3>
      <div className="space-y-3">
        <button onClick={() => handleSimulate('Heatwave')} disabled={loading} className="w-full flex items-center justify-center space-x-2 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-bold shadow-sm transition-all focus:ring-4 focus:ring-orange-500/30">
          <Flame className="w-4 h-4" /> <span>Trigger 45°C Heatwave</span>
        </button>
        <button onClick={() => handleSimulate('Rainfall')} disabled={loading} className="w-full flex items-center justify-center space-x-2 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-bold shadow-sm transition-all focus:ring-4 focus:ring-blue-500/30">
          <CloudRain className="w-4 h-4" /> <span>Trigger 50mm Rainfall</span>
        </button>
        <button onClick={() => handleSimulate('App Outage')} disabled={loading} className="w-full flex items-center justify-center space-x-2 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-bold shadow-sm transition-all focus:ring-4 focus:ring-purple-500/30">
          <ServerCrash className="w-4 h-4" /> <span>Trigger App Outage</span>
        </button>
        <button onClick={() => handleSimulate('Severe Smog')} disabled={loading} className="w-full flex items-center justify-center space-x-2 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-bold shadow-sm transition-all focus:ring-4 focus:ring-gray-500/30">
          <Wind className="w-4 h-4" /> <span>Trigger AQI 450 Smog</span>
        </button>
        <button onClick={() => handleSimulate('Blackout')} disabled={loading} className="w-full flex items-center justify-center space-x-2 py-3 bg-zinc-800 hover:bg-zinc-900 text-white rounded-lg font-bold shadow-sm transition-all focus:ring-4 focus:ring-zinc-800/30">
          <WifiOff className="w-4 h-4" /> <span>Trigger Interet Blackout</span>
        </button>
      </div>
      <p className="mt-4 text-xs text-red-600 font-medium text-center">Zero-Touch Auto-Claims processing</p>
    </div>
  );
};

export default AdminTriggerPanel;
