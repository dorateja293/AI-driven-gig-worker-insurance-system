import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Mail, AlertCircle, CheckCircle, ArrowRight, BadgeCheck, Lock } from 'lucide-react';
import api from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  
  // Form State
  const [workerID, setWorkerID] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Validation Functions
  const validateEmail = (emailValue) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(emailValue);
  };

  // Handle Login Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!workerID.trim()) {
      setError('Worker ID is required');
      return;
    }

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email');
      return;
    }

    if (!password.trim()) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const loginPayload = { 
        worker_id: workerID.trim().toUpperCase(), 
        email: email.trim().toLowerCase(),
        password: password.trim()
      };
      
      const res = await api.post('/auth/login', loginPayload);
      
      if (res.status === 200 && res.data?.user_id) {
        sessionStorage.setItem('user', JSON.stringify({
          user_id: res.data.user_id,
          name: res.data.name,
          email: email,
          worker_id: workerID,
          platform: res.data.platform,
          city: res.data.city,
          wallet_balance: res.data.wallet_balance || 0
        }));
        
        if (res.data?.token) {
          sessionStorage.setItem('token', res.data.token);
        }
        
        sessionStorage.setItem('isLoggedIn', 'true');
        
        setLoading(false);
        navigate('/dashboard');
      } else {
        setError('User not found. Please register first.');
        setLoading(false);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('User not found. Please register first.');
      } 
      else if (err.response?.status === 401) {
        setError('Invalid password');
      }
      else if (err.response?.status === 400) {
        setError(err.response?.data?.error || 'Invalid credentials');
      }
      else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message) {
        setError('Login failed. Please check your connection and try again.');
      } else {
        setError('An unexpected error occurred during login.');
      }
      
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-white via-orange-50 to-white flex items-center justify-center px-4 py-12 overflow-auto">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl border border-orange-100 p-8">
          
          {/* Header */}
          <div className="text-center mb-10">
            <div className="bg-gradient-to-br from-orange-400 to-red-500 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <ShieldCheck className="text-white w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">InsureX</h1>
            <p className="text-gray-600 mt-2 font-medium text-sm">
              Safe delivery. Secured future.
            </p>
          </div>

          {error && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-2xl">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700 font-medium">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Worker ID */}
            <div className="space-y-3">
              <label htmlFor="workerID" className="block text-sm font-semibold text-gray-800">
                💼 Worker ID
              </label>
              <div className="relative group">
                <BadgeCheck className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                <input
                  id="workerID"
                  type="text"
                  value={workerID}
                  onChange={(e) => setWorkerID(e.target.value)}
                  placeholder="Your worker ID"
                  autoComplete="off"
                  className="w-full pl-12 pr-4 py-3 bg-white border-2 border-gray-200 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent hover:border-orange-300"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-3">
              <label htmlFor="email" className="block text-sm font-semibold text-gray-800">
                ✉️ Email
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  autoComplete="off"
                  className="w-full pl-12 pr-4 py-3 bg-white border-2 border-gray-200 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent hover:border-orange-300"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-3">
              <label htmlFor="password" className="block text-sm font-semibold text-gray-800">
                🔐 Password
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  autoComplete="off"
                  className="w-full pl-12 pr-12 py-3 bg-white border-2 border-gray-200 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent hover:border-orange-300"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-orange-500 transition-colors"
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
          
            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full mt-8 py-4 px-4 rounded-2xl font-bold text-white tracking-wide transition-all duration-300 flex items-center justify-center gap-3 border-2 ${
                !loading
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 active:scale-95 shadow-lg border-transparent'
                  : 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
              }`}
            >
              {loading ? (
                <>
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Logging in...</span>
                </>
              ) : (
                <>
                  <span>Login Securely</span>
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="text-center text-sm text-gray-600 mt-8">
            Don't have an account?{' '}
            <Link to="/register" className="text-orange-600 font-bold hover:text-orange-700 transition-colors">
              Register here
            </Link>
          </p>
        </div>

        {/* Trust Badge */}
        <div className="text-center mt-8">
          <p className="text-xs text-gray-600 flex items-center justify-center gap-2">
            <span>🔒 256-bit SSL Encrypted</span>
            <span>•</span>
            <span>✅ NISM Registered</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
