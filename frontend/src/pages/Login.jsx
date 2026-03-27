import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Phone } from 'lucide-react';
import api from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/login', { phone });
      if (res.data?.user_id) localStorage.setItem('user_id', res.data.user_id);
      if (res.data?.token) localStorage.setItem('token', res.data.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to login');
    }
    setLoading(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="bg-white p-8 sm:p-10 rounded-2xl shadow-lg border border-gray-100 max-w-md w-full transition-all duration-200 hover:shadow-xl">
        
        <div className="text-center mb-8">
          <div className="bg-indigo-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-transform hover:scale-105">
            <ShieldCheck className="text-indigo-600 w-8 h-8" />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">InsureX Login</h2>
          <p className="text-sm text-gray-500 font-medium mt-2">Welcome back. Secure your gig income.</p>
        </div>
        
        {error && <div className="mb-4 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="text-sm font-semibold text-gray-700">Phone Number</label>
            <div className="relative">
              <Phone className="absolute inset-y-0 left-3 my-auto h-5 w-5 text-gray-400" />
              <input type="tel" required placeholder="+91 98765 43210" value={phone} className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900" onChange={e => setPhone(e.target.value)} />
            </div>
          </div>
          
          <button type="submit" disabled={loading} className="w-full mt-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-md active:scale-95 transition-all duration-200 flex justify-center items-center">
            {loading ? 'Logging in...' : 'Login Securely'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Don't have an account? <Link to="/register" className="text-indigo-600 font-semibold hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
