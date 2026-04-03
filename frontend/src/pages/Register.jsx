import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, User, Mail, Phone, MapPin, Briefcase, AlertCircle, CheckCircle, Send, BadgeCheck, ArrowRight } from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();
  
  // Form State
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    city: '',
    zone: '',
    platform: 'Swiggy',
    workerID: ''
  });

  // Validation State
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  // OTP State
  const [isOtpSent, setIsOtpSent] = useState(false);
  const [isOtpVerified, setIsOtpVerified] = useState(false);
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const [otpError, setOtpError] = useState('');
  const [otpMessage, setOtpMessage] = useState('');
  const otpRefs = useRef([]);
  
  // Loading State
  const [loading, setLoading] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);

  // Worker Verification State
  const [workerIDValidation, setWorkerIDValidation] = useState('');
  const [isWorkerVerified, setIsWorkerVerified] = useState(false);
  const [verifyingWorker, setVerifyingWorker] = useState(false);

  // Auto-focus first OTP input when OTP section appears
  useEffect(() => {
    if (isOtpSent && !isOtpVerified && otpRefs.current[0]) {
      otpRefs.current[0].focus();
    }
  }, [isOtpSent, isOtpVerified]);

  // Validation Functions
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone) => {
    const phoneRegex = /^\d{10}$/;
    const cleanPhone = phone.replace(/\D/g, '');
    return cleanPhone.length === 10;
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    } else if (formData.fullName.trim().length < 3) {
      newErrors.fullName = 'Name must be at least 3 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!validatePhone(formData.phone)) {
      newErrors.phone = 'Phone number must be 10 digits';
    }

    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    } else if (formData.city.trim().length < 2) {
      newErrors.city = 'City name must be at least 2 characters';
    }

    if (!formData.zone.trim()) {
      newErrors.zone = 'Zone is required';
    } else if (formData.zone.trim().length < 2) {
      newErrors.zone = 'Zone name must be at least 2 characters';
    }

    if (!formData.workerID.trim()) {
      newErrors.workerID = 'Worker ID is required for insurance eligibility';
    } else if (formData.workerID.trim().length < 3) {
      newErrors.workerID = 'Worker ID must be at least 3 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle Input Change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (touched[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Handle Blur
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    validateForm();
  };

  // Handle Send OTP
  const handleSendOtp = async (e) => {
    e.preventDefault();
    
    if (!formData.email.trim()) {
      setErrors(prev => ({
        ...prev,
        email: 'Email is required'
      }));
      return;
    }

    if (!validateEmail(formData.email)) {
      setErrors(prev => ({
        ...prev,
        email: 'Please enter a valid email'
      }));
      return;
    }

    setSendingOtp(true);
    setOtpError('');
    setOtpMessage('');

    try {
      const response = await fetch('http://localhost:5000/api/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email.trim().toLowerCase()
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
        setErrors(prev => ({
          ...prev,
          email: data.message || 'Failed to send OTP'
        }));
      }
    } catch (error) {
      console.error('Error sending OTP:', error);
      setErrors(prev => ({
        ...prev,
        email: 'Connection error. Please check backend is running.'
      }));
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
          email: formData.email.trim().toLowerCase(),
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

  // Validate Worker ID format
  const validateWorkerIDFormat = (workerId) => {
    const trimmedId = workerId.trim().toUpperCase();
    if (!trimmedId) return 'Worker ID is required for insurance eligibility';
    if (trimmedId.length < 3) return 'Worker ID must be at least 3 characters';
    
    const isValidFormat = trimmedId.startsWith('SWG') || trimmedId.startsWith('ZMT');
    if (!isValidFormat) return 'Worker ID must start with SWG or ZMT (e.g., SWG12345)';
    
    return '';
  };

  // Verify Worker ID with backend
  const handleVerifyWorker = async () => {
    const validationError = validateWorkerIDFormat(formData.workerID);
    
    if (validationError) {
      setWorkerIDValidation(validationError);
      setIsWorkerVerified(false);
      return;
    }

    setVerifyingWorker(true);
    setWorkerIDValidation('');

    try {
      const response = await fetch('http://localhost:5000/api/auth/verify-worker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workerId: formData.workerID.trim().toUpperCase(),
          email: formData.email.trim().toLowerCase()
        }),
      });

      const data = await response.json();

      if (data.verified && data.status === 'verified') {
        console.log('✅ Worker Verified:', data);
        setIsWorkerVerified(true);
        setWorkerIDValidation('verified');
      } else {
        console.log('❌ Worker Verification Failed:', data);
        let errorMessage = 'Worker verification failed';
        
        switch (data.status) {
          case 'email_mismatch':
            errorMessage = 'Email does not match the worker record. Please verify your email address.';
            break;
          case 'not_found':
            errorMessage = 'Worker ID not found in our system. Please contact support.';
            break;
          case 'invalid':
            errorMessage = data.message || 'Invalid input provided';
            break;
          case 'error':
            errorMessage = 'Server error during verification. Please try again.';
            break;
          default:
            errorMessage = data.message || 'Worker verification failed';
        }
        
        setWorkerIDValidation(errorMessage);
        setIsWorkerVerified(false);
      }
    } catch (error) {
      console.error('Verification error:', error);
      setWorkerIDValidation('Connection error during verification. Please check your internet and try again.');
      setIsWorkerVerified(false);
    } finally {
      setVerifyingWorker(false);
      console.log('🔄 Verification Complete. State will update...');
    }
  };

  // Handle Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const isAllValid = isFormValid();
    console.log('📋 Submit Button Clicked');
    
    if (!isAllValid) {
      console.error('❌ Form validation failed');
      alert('Please complete all required fields:\n✓ All personal info\n✓ Email OTP verified\n✓ Worker ID verified');
      return;
    }

    console.log('✅ All validations passed, starting registration...');
    setLoading(true);
    
    try {
      const registrationPayload = {
        name: formData.fullName,
        email: formData.email,
        phone: formData.phone,
        city: formData.city,
        zone: formData.zone,
        platform: formData.platform
      };
      
      console.log('📤 Sending registration request:', registrationPayload);
      
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationPayload),
      });

      console.log('📥 Response Status:', response.status);
      const data = await response.json();
      console.log('📥 Response Data:', data);

      if (response.ok && data.token) {
        console.log('✅ Registration successful!');
        
        sessionStorage.setItem('user', JSON.stringify({
          user_id: data.user_id,
          name: data.name,
          email: formData.email,
          phone: data.phone,
          platform: data.platform,
          city: formData.city,
          walletBalance: data.wallet_balance || 0
        }));
        sessionStorage.setItem('token', data.token);
        sessionStorage.setItem('isLoggedIn', 'true');
        
        console.log('✅ Data stored in sessionStorage');
        console.log('🚀 Navigating to dashboard...');
        
        setLoading(false);
        navigate('/dashboard');
        
      } else {
        console.error('❌ Registration failed:', data.error);
        setLoading(false);
        alert('Registration failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      setLoading(false);
      alert('Error: ' + error.message + '\n\nPlease check that the backend is running on http://localhost:5000');
    }
  };

  // Check if form is completely valid
  const isFormValid = () => {
    const hasNoErrors = !Object.keys(errors).length;
    const allFieldsFilled = 
      formData.fullName?.trim() &&
      formData.email?.trim() &&
      formData.phone?.trim() &&
      formData.city?.trim() &&
      formData.zone?.trim() &&
      formData.platform?.trim() &&
      formData.workerID?.trim();
    const otpDone = isOtpVerified;
    const workerDone = isWorkerVerified;
    
    console.log('🔍 Form Validation:', {
      hasNoErrors,
      allFieldsFilled,
      otpVerified: otpDone,
      workerVerified: workerDone,
      canSubmit: hasNoErrors && allFieldsFilled && otpDone && workerDone
    });
    
    return hasNoErrors && allFieldsFilled && otpDone && workerDone;
  };

  // Calculate progress
  const filledFields = [
    formData.fullName?.trim(),
    formData.email?.trim(),
    formData.phone?.trim(),
    formData.city?.trim(),
    formData.zone?.trim(),
    formData.platform?.trim(),
    formData.workerID?.trim(),
  ].filter(Boolean).length;

  const progressPercent = Math.round((filledFields / 7) * 100);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-white via-orange-50 to-white overflow-y-auto overflow-x-hidden flex flex-col items-center py-8 px-4">
      <div className="w-full max-w-2xl mt-4 mb-8">
        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl border border-orange-100 p-8">
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="bg-gradient-to-br from-orange-400 to-red-500 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <ShieldCheck className="text-white w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">InsureX</h1>
            <p className="text-gray-600 mt-2 font-medium text-sm">
              Protect your gig work with smart insurance
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-semibold text-gray-700">Registration Progress</span>
              <span className="text-xs font-bold text-orange-600">{progressPercent}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* SECTION 1: Personal Information */}
            <div className="space-y-5 pb-6 border-b-2 border-orange-100">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <User className="h-5 w-5 text-orange-600" />
                Personal Information
              </h2>

              {/* Full Name */}
              <div className="space-y-2">
                <label htmlFor="fullName" className="block text-sm font-semibold text-gray-800">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="fullName"
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="E.g., Ravi Kumar"
                    maxLength="50"
                    autoComplete="off"
                    className={`w-full pl-12 pr-12 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none hover:border-orange-300 ${
                      touched.fullName && errors.fullName
                        ? 'border-red-300 focus:ring-2 focus:ring-red-200'
                        : touched.fullName && !errors.fullName && formData.fullName
                        ? 'border-green-400 focus:ring-2 focus:ring-green-200'
                        : 'border-gray-200 focus:ring-2 focus:ring-orange-200'
                    }`}
                  />
                  {touched.fullName && !errors.fullName && formData.fullName && (
                    <CheckCircle className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                </div>
                {touched.fullName && errors.fullName && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{errors.fullName}</span>
                  </div>
                )}
              </div>

              {/* Email with OTP */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-semibold text-gray-800">
                  Email
                </label>
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                    <input
                      id="email"
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      onBlur={() => setTouched(prev => ({ ...prev, email: true }))}
                      readOnly={isOtpSent}
                      placeholder="E.g., ravi@example.com"
                      className={`w-full pl-12 pr-4 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none hover:border-orange-300 ${
                        isOtpSent ? 'cursor-not-allowed opacity-60 border-gray-200' : 'border-gray-200'
                      } ${
                        touched.email && errors.email
                          ? 'border-red-300 focus:ring-2 focus:ring-red-200'
                          : isOtpVerified
                          ? 'border-green-400 focus:ring-2 focus:ring-green-200'
                          : 'focus:ring-2 focus:ring-orange-200'
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
                      className={`px-4 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 transition-all duration-300 whitespace-nowrap border-2 ${
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
                        setFormData({ ...formData, email: '' });
                      }}
                      className="px-4 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 transition-all duration-300 whitespace-nowrap border-2 bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 active:scale-95"
                    >
                      ← Change Email
                    </button>
                  )}
                </div>
                {touched.email && errors.email && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{errors.email}</span>
                  </div>
                )}
                {otpMessage && isOtpSent && !isOtpVerified && (
                  <div className="flex items-center gap-2 text-sm text-blue-700 bg-blue-50 p-2 rounded-lg border border-blue-200">
                    <CheckCircle className="h-4 w-4" />
                    <span>{otpMessage}</span>
                  </div>
                )}
              </div>

              {/* OTP Input Section */}
              {isOtpSent && !isOtpVerified && (
                <div className="space-y-4 p-5 bg-orange-50 rounded-2xl border-2 border-orange-200">
                  <label className="block text-sm font-bold text-gray-900">
                    🔐 Enter 6-Digit OTP
                  </label>
                  
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

              {/* Phone */}
              <div className="space-y-2">
                <label htmlFor="phone" className="block text-sm font-semibold text-gray-800">
                  Phone Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="phone"
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="10-digit phone number"
                    maxLength="10"
                    autoComplete="off"
                    className={`w-full pl-12 pr-12 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none hover:border-orange-300 ${
                      touched.phone && errors.phone
                        ? 'border-red-300 focus:ring-2 focus:ring-red-200'
                        : touched.phone && !errors.phone && formData.phone
                        ? 'border-green-400 focus:ring-2 focus:ring-green-200'
                        : 'border-gray-200 focus:ring-2 focus:ring-orange-200'
                    }`}
                  />
                  {touched.phone && !errors.phone && formData.phone && (
                    <CheckCircle className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                </div>
                {touched.phone && errors.phone && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{errors.phone}</span>
                  </div>
                )}
              </div>
            </div>

            {/* SECTION 2: Location */}
            <div className="space-y-5 pb-6 border-b-2 border-orange-100">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <MapPin className="h-5 w-5 text-orange-600" />
                Location Details
              </h2>

              {/* City */}
              <div className="space-y-2">
                <label htmlFor="city" className="block text-sm font-semibold text-gray-800">
                  City
                </label>
                <div className="relative">
                  <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="city"
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="E.g., Bangalore"
                    maxLength="30"
                    autoComplete="off"
                    className={`w-full pl-12 pr-12 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none hover:border-orange-300 ${
                      touched.city && errors.city
                        ? 'border-red-300 focus:ring-2 focus:ring-red-200'
                        : touched.city && !errors.city && formData.city
                        ? 'border-green-400 focus:ring-2 focus:ring-green-200'
                        : 'border-gray-200 focus:ring-2 focus:ring-orange-200'
                    }`}
                  />
                  {touched.city && !errors.city && formData.city && (
                    <CheckCircle className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                </div>
                {touched.city && errors.city && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{errors.city}</span>
                  </div>
                )}
              </div>

              {/* Zone */}
              <div className="space-y-2">
                <label htmlFor="zone" className="block text-sm font-semibold text-gray-800">
                  Zone / Area
                </label>
                <div className="relative">
                  <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="zone"
                    type="text"
                    name="zone"
                    value={formData.zone}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="E.g., Whitefield"
                    maxLength="30"
                    autoComplete="off"
                    className={`w-full pl-12 pr-12 py-3 bg-white border-2 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none hover:border-orange-300 ${
                      touched.zone && errors.zone
                        ? 'border-red-300 focus:ring-2 focus:ring-red-200'
                        : touched.zone && !errors.zone && formData.zone
                        ? 'border-green-400 focus:ring-2 focus:ring-green-200'
                        : 'border-gray-200 focus:ring-2 focus:ring-orange-200'
                    }`}
                  />
                  {touched.zone && !errors.zone && formData.zone && (
                    <CheckCircle className="absolute right-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                </div>
                {touched.zone && errors.zone && (
                  <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg border border-red-200">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{errors.zone}</span>
                  </div>
                )}
              </div>

              {/* Platform */}
              <div className="space-y-2">
                <label htmlFor="platform" className="block text-sm font-semibold text-gray-800">
                  Delivery Platform
                </label>
                <div className="relative">
                  <Briefcase className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none z-10" />
                  <select
                    id="platform"
                    name="platform"
                    value={formData.platform}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    className="w-full pl-12 pr-4 py-3 bg-white border-2 border-gray-200 rounded-2xl text-gray-900 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-200 hover:border-orange-300 appearance-none cursor-pointer"
                  >
                    <option value="Swiggy">🚴 Swiggy</option>
                    <option value="Zomato">🛵 Zomato</option>
                    <option value="Others">🚗 Others</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION 3: Work Verification */}
            <div className="space-y-5">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <BadgeCheck className="h-5 w-5 text-orange-600" />
                Work Verification
              </h2>

              {/* Worker ID */}
              <div className="space-y-2">
                <label htmlFor="workerID" className="block text-sm font-semibold text-gray-800">
                  Worker ID
                </label>
                <div className="relative">
                  <BadgeCheck className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-orange-500 pointer-events-none" />
                  <input
                    id="workerID"
                    type="text"
                    name="workerID"
                    value={formData.workerID}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="E.g., SWG12345"
                    maxLength="12"
                    className="w-full pl-12 pr-24 py-3 bg-white border-2 border-gray-200 rounded-2xl text-gray-900 placeholder-gray-500 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-200 hover:border-orange-300"
                  />
                  {formData.workerID && !workerIDValidation && (
                    <CheckCircle className="absolute right-24 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
                  )}
                  
                  {/* Verify Button */}
                  <button
                    type="button"
                    onClick={handleVerifyWorker}
                    disabled={verifyingWorker || !formData.workerID || isWorkerVerified}
                    className={`absolute right-0 top-0 bottom-0 px-4 rounded-r-2xl text-xs font-bold transition-all duration-300 border-l ${
                      isWorkerVerified
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white border-transparent'
                        : verifyingWorker
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
                        : formData.workerID
                        ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600 active:scale-95 border-transparent'
                        : 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
                    }`}
                  >
                    {verifyingWorker ? 'Verifying...' : isWorkerVerified ? '✓ Verified' : 'Verify'}
                  </button>
                </div>
              </div>

              {/* Worker ID Validation Message */}
              {workerIDValidation && workerIDValidation !== 'verified' && (
                <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-3 rounded-lg border border-red-200">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <span>{workerIDValidation}</span>
                </div>
              )}

              {/* Success Message */}
              {isWorkerVerified && (
                <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 p-3 rounded-lg border border-green-200">
                  <CheckCircle className="h-5 w-5 flex-shrink-0" />
                  <span className="font-semibold">✓ Verified Worker</span>
                </div>
              )}
            </div>

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading || !isFormValid()}
              className={`w-full mt-8 py-4 px-4 rounded-2xl font-bold text-white tracking-wide transition-all duration-300 flex items-center justify-center gap-3 border-2 ${
                isFormValid()
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 active:scale-95 shadow-lg border-transparent'
                  : 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200'
              }`}
            >
              {loading ? (
                <>
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Registering...</span>
                </>
              ) : (
                <>
                  <span>Complete Registration</span>
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="text-center text-sm text-gray-600 mt-8">
            Already have an account?{' '}
            <Link to="/login" className="text-orange-600 font-bold hover:text-orange-700 transition-colors">
              Login here
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

export default Register;
