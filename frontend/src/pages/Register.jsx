import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, User, Phone, MapPin, Briefcase } from 'lucide-react';
import api from '../services/api';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '', phone: '', city: '', zone: 'Zone-A', platform: 'Swiggy'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/auth/register', formData);
      if (res.data?.user_id) localStorage.setItem('user_id', res.data.user_id);
      if (res.data?.token) localStorage.setItem('token', res.data.token);
      navigate('/dashboard');
    } catch (err) {
      if (err.response?.status === 409) {
          try {
            const loginRes = await api.post('/auth/login', { phone: formData.phone });
            if (loginRes.data?.user_id) localStorage.setItem('user_id', loginRes.data.user_id);
            if (loginRes.data?.token) localStorage.setItem('token', loginRes.data.token);
            navigate('/dashboard');
          } catch(e) {}
      }
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
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">InsureX</h2>
          <p className="text-sm text-gray-500 font-medium mt-2">Protect your gig income instantly.</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="text-sm font-semibold text-gray-700">Full Name</label>
            <div className="relative">
              <User className="absolute inset-y-0 left-3 my-auto h-5 w-5 text-gray-400" />
              <input required placeholder="E.g., Ravi Kumar" value={formData.name} className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900" onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-semibold text-gray-700">Phone Number</label>
            <div className="relative">
              <Phone className="absolute inset-y-0 left-3 my-auto h-5 w-5 text-gray-400" />
              <input type="tel" required placeholder="+91 98765 43210" value={formData.phone} className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900" onChange={e => setFormData({...formData, phone: e.target.value})} />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">City</label>
              <div className="relative">
                <MapPin className="absolute inset-y-0 left-3 my-auto h-5 w-5 text-gray-400" />
                <input required placeholder="Hyderabad" value={formData.city} className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900" onChange={e => setFormData({...formData, city: e.target.value})} />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Risk Zone</label>
              <select value={formData.zone} className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900 cursor-pointer" onChange={e => setFormData({...formData, zone: e.target.value})}>
                <option value="Zone-A">Zone-A</option>
                <option value="Zone-B">Zone-B</option>
              </select>
            </div>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-sm font-semibold text-gray-700">Platform</label>
            <div className="relative">
               <Briefcase className="absolute inset-y-0 left-3 my-auto h-5 w-5 text-gray-400" />
               <select value={formData.platform} className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-gray-900 cursor-pointer" onChange={e => setFormData({...formData, platform: e.target.value})}>
                 <option value="Swiggy">Swiggy</option>
                 <option value="Zomato">Zomato</option>
               </select>
            </div>
          </div>

          <button type="submit" disabled={loading} className="w-full mt-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-md active:scale-95 transition-all duration-200 flex justify-center items-center">
            {loading ? 'Processing...' : 'Register Worker'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account? <Link to="/login" className="text-indigo-600 font-semibold hover:underline">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
