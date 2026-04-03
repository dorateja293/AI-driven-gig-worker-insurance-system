import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, UserPlus, FileText, Settings, Rocket } from 'lucide-react';
import Register from './pages/Register';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import BuyPolicy from './pages/BuyPolicy';
import AdminPanel from './pages/AdminPanel';



function App() {
  return (
    <BrowserRouter>
      <div className="w-full h-full">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/buy-policy" element={<BuyPolicy />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
