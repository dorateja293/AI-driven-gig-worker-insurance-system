import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Mail, AlertCircle, CheckCircle, Send, ArrowRight, BadgeCheck } from 'lucide-react';
import api from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  
  // Form State
  const [workerID, setWorkerID] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // OTP State
  const [isOtpSent, setIsOtpSent] = useState(false);
  const [isOtpVerified, setIsOtpVerified] = useState(false);
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const [otpError, setOtpError] = useState('');
  const [otpMessage, setOtpMessage] = useState('');
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const otpRefs = useRef([]);

  // Auto-focus first OTP input when OTP section appears
  useEffect(() => {
    if (isOtpSent && !isOtpVerified && otpRefs.current[0]) {
      otpRefs.current[0].focus();
    }
  }, [isOtpSent, isOtpVerified]);

  // Validation Functions
  const validateEmail = (emailValue) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(emailValue);
  };

  // Handle Send OTP
  const handleSendOtp = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email');
      return;
    }

    setSendingOtp(true);
    setError('');
    setOtpError('');
    setOtpMessage('');

    try {
      const response = await fetch('http://localhost:5000/api/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase()
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsOtpSent(true);
        setOtpMessage('✓ OTP sent to your email! Check your inbox.');
        if (otpRefs.current[0]) {
          otpRefs.current[0].focus();
        }
      } else {
        setError(data.message || 'Failed to send OTP');
      }
    } catch (error) {
      console.error('Error sending OTP:', error);
      setError('Connection error. Please check backend is running.');
    } finally {
      setSendingOtp(false);
    }
  };

  // Handle Verify OTP
  const handleVerifyOtp = async (e) => {
    e.preventDefault();

    const fullOtp = otpDigits.join('');

    if (!fullOtp) {
      setOtpError('OTP is required');
      return;
    }

    if (fullOtp.length !== 6) {
      setOtpError('Please enter all 6 digits');
      return;
    }

    setVerifyingOtp(true);
    setOtpError('');

    try {
      const response = await fetch('http://localhost:5000/api/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          otp: fullOtp
        })
      });

      const data = await response.json();

      if (response.ok && data.verified) {
        setIsOtpVerified(true);
        setOtpMessage('✓ Email verified successfully');
        setOtpDigits(['', '', '', '', '', '']);
      } else {
        setOtpError(data.message || 'Invalid OTP');
      }
    } catch (error) {
      console.error('Error verifying OTP:', error);
      setOtpError('Connection error. Please try again.');
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Handle OTP Digit Input
  const handleOtpDigitChange = (index, value) => {
    if (value && !/^\d$/.test(value)) {
      return;
    }

    const newOtpDigits = [...otpDigits];
    newOtpDigits[index] = value;
    setOtpDigits(newOtpDigits);
    setOtpError('');

    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  // Handle OTP Digit Backspace
  const handleOtpDigitKeyDown = (index, e) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      
      const newOtpDigits = [...otpDigits];
      if (otpDigits[index]) {
        newOtpDigits[index] = '';
        setOtpDigits(newOtpDigits);
      } else if (index > 0) {
        newOtpDigits[index - 1] = '';
        setOtpDigits(newOtpDigits);
        otpRefs.current[index - 1]?.focus();
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      otpRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  // Handle OTP Digit Paste
  const handleOtpPaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    const digits = pastedData.replace(/\D/g, '').split('').slice(0, 6);
    
    const newOtpDigits = [...otpDigits];
    digits.forEach((digit, index) => {
      newOtpDigits[index] = digit;
    });
    setOtpDigits(newOtpDigits);

    const nextIndex = Math.min(digits.length, 5);
    otpRefs.current[nextIndex]?.focus();
  };

  // Handle Login Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log('📋 Login Button Clicked');
    console.log('Form State:', { isOtpVerified, workerID, email });
    
    if (!isOtpVerified) {
      console.error('❌ Email not verified');
      setError('Please verify your email with OTP first');
      return;
    }

    if (!workerID.trim()) {
      console.error('❌ Worker ID is empty');
      setError('Worker ID is required');
      return;
    }

    console.log('✅ All validations passed, starting login...');
    setLoading(true);
    setError('');
    
    try {
      const loginPayload = { worker_id: workerID, email };
      console.log('📤 Sending login request:', loginPayload);
      
      const res = await api.post('/auth/login', loginPayload);
      
      console.log('📥 Login response status:', res.status);
      console.log('📥 Login response data:', res.data);
      
      if (res.status === 200 && res.data?.user_id) {
        console.log('✅ User found! user_id:', res.data.user_id);
        
        sessionStorage.setItem('user', JSON.stringify({
          user_id: res.data.user_id,
          name: res.data.name,
          email: email,
          worker_id: workerID,
          platform: res.data.platform,
          city: res.data.city,
          wallet_balance: res.data.wallet_balance || 0
        }));
        console.log('✅ Stored user data in sessionStorage');
        
        if (res.data?.token) {
          sessionStorage.setItem('token', res.data.token);
          console.log('✅ Stored token in sessionStorage');
        }
        
        sessionStorage.setItem('isLoggedIn', 'true');
        console.log('✅ Set isLoggedIn flag');
        
        console.log('✅ Login successful! All data stored in sessionStorage.');
        console.log('🚀 Navigating to dashboard...');
        
        setLoading(false);
        navigate('/dashboard');
      } else {
        console.error('❌ User not found in response');
        setError('User not found. Please register first.');
        setLoading(false);
      }
    } catch (err) {
      console.error('❌ Login error caught in catch block:', err);
      console.error('Error response status:', err.response?.status);
      console.error('Error response data:', err.response?.data);
      
      if (err.response?.status === 404) {
        console.error('❌ 404 Error - User not found');
        setError('User not found. Please register first.');
      } 
      else if (err.response?.status === 400) {
        console.error('❌ 400 Error - Bad request');
        setError(err.response?.data?.error || 'Invalid credentials');
      }
      else if (err.response?.data?.error) {
        console.error('❌ Error from backend:', err.response.data.error);
        setError(err.response.data.error);
      } else if (err.message) {
        console.error('❌ Error message:', err.message);
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

            {/* Email with OTP */}
            <div className="space-y-3">
              <label htmlFor="email" className="block text-sm font-semibold text-gray-800">
                ✉️ Email
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative group">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    readOnly={isOtpSent}
                    placeholder="your@email.com"
                    autoComplete="off"
                    className={`w-full pl-12 pr-4 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none focus:ring-2 focus:border-transparent hover:border-orange-300 ${
                      isOtpSent ? 'cursor-not-allowed opacity-60 border-gray-200' : 'border-gray-200'
                    } ${
                      isOtpVerified
                        ? 'border-green-300 focus:ring-green-400'
                        : 'focus:ring-orange-400'
                    }`}
                  />
                  {isOtpVerified && (
                    <CheckCircle className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                </div>
                {!isOtpVerified && !isOtpSent && (
                  <button
                    type="button"
                    onClick={handleSendOtp}
                    disabled={sendingOtp}
                    className={`px-5 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 transition-all duration-300 border-2 whitespace-nowrap ${
                      sendingOtp
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
                        : 'bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600 active:scale-95 border-transparent shadow-lg'
                    }`}
                  >
                    {sendingOtp ? (
                      <>
                        <div className="h-3 w-3 border-2 border-gray-500 border-t-transparent rounded-full animate-spin" />
                        <span>Sending</span>
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        <span>Send OTP</span>
                      </>
                    )}
                  </button>
                )}
                {isOtpSent && !isOtpVerified && (
                  <button
                    type="button"
                    onClick={() => {
                      setIsOtpSent(false);
                      setOtpDigits(['', '', '', '', '', '']);
                      setOtpError('');
                      setOtpMessage('');
                      setEmail('');
                    }}
                    className="px-4 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 transition-all duration-300 border-2 whitespace-nowrap bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 active:scale-95"
                  >
                    ← Change Email
                  </button>
                )}
              </div>
              {otpMessage && isOtpSent && !isOtpVerified && (
                <div className="flex items-center gap-2 text-sm text-blue-700 bg-blue-50 p-2 rounded-lg border border-blue-200">
                  <CheckCircle className="h-4 w-4" />
                  <span>{otpMessage}</span>
                </div>
              )}
              {otpMessage && isOtpVerified && (
                <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 p-2 rounded-lg border border-green-200">
                  <CheckCircle className="h-4 w-4" />
                  <span>{otpMessage}</span>
                </div>
              )}
            </div>

            {/* OTP Input Section */}
            {isOtpSent && !isOtpVerified && (
              <div className="space-y-4 p-5 bg-orange-50 rounded-2xl border-2 border-orange-200">
                <label className="block text-sm font-bold text-gray-800">
                  🔐 Enter 6-Digit OTP
                </label>
                
                {/* 6 OTP Input Boxes */}
                <div className="flex gap-2 justify-center py-2">
                  {otpDigits.map((digit, index) => (
                    <input
                      key={index}
                      ref={(el) => (otpRefs.current[index] = el)}
                      type="text"
                      inputMode="numeric"
                      maxLength="1"
                      value={digit}
                      onChange={(e) => handleOtpDigitChange(index, e.target.value)}
                      onKeyDown={(e) => handleOtpDigitKeyDown(index, e)}
                      onPaste={handleOtpPaste}
                      placeholder="•"
                      className={`w-12 h-12 text-center text-xl font-bold rounded-xl border-2 transition-all duration-200 focus:outline-none font-mono ${
                        otpError
                          ? 'border-red-400 bg-red-50 text-red-700 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                          : digit
                          ? 'border-orange-500 bg-orange-100 text-orange-800 focus:border-orange-600'
                          : 'border-orange-300 bg-white text-gray-900 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 hover:border-orange-400'
                      }`}
                    />
                  ))}
                </div>

                {otpError && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{otpError}</span>
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleVerifyOtp}
                  disabled={verifyingOtp || otpDigits.join('').length !== 6}
                  className={`w-full py-3 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 border-2 ${
                    verifyingOtp || otpDigits.join('').length !== 6
                      ? 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
                      : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 active:scale-95 border-transparent shadow-lg'
                  }`}
                >
                  {verifyingOtp ? (
                    <>
                      <div className="h-3 w-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Verifying...</span>
                    </>
                  ) : (
                    '✓ Verify OTP'
                  )}
                </button>
              </div>
            )}
          
            {/* Login Button */}
            <button
              type="submit"
              disabled={loading || !isOtpVerified || !workerID.trim()}
              className={`w-full mt-8 py-4 px-4 rounded-2xl font-bold text-white tracking-wide transition-all duration-300 flex items-center justify-center gap-3 border-2 ${
                isOtpVerified && workerID.trim()
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 active:scale-95 shadow-lg border-transparent'
                  : 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
              }`}
              title={!isOtpVerified ? 'Please verify email with OTP first' : !workerID.trim() ? 'Please enter worker ID' : 'Click to login'}
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
