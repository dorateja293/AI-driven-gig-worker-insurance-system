import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, LogOut } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const isActive = (path) => location.pathname === path ? 'text-indigo-600 bg-indigo-50 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50 font-medium';

  const handleLogout = () => {
    localStorage.clear();
    navigate('/register');
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans selection:bg-indigo-100 flex flex-col">
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="h-8 w-8 text-indigo-600" />
              <span className="text-xl font-extrabold text-gray-900 tracking-tight">InsureX</span>
            </div>
            
            {localStorage.getItem('user_id') && (
              <div className="flex items-center space-x-1 sm:space-x-3">
                <Link to="/dashboard" className={`px-4 py-2 rounded-lg text-sm transition-all duration-200 ${isActive('/dashboard')}`}>Dashboard</Link>
                <Link to="/buy-policy" className={`px-4 py-2 rounded-lg text-sm transition-all duration-200 ${isActive('/buy-policy')}`}>Buy Policy</Link>
                <Link to="/admin" className={`px-4 py-2 rounded-lg text-sm transition-all duration-200 ${isActive('/admin')}`}>Admin</Link>
                <button onClick={handleLogout} className="ml-2 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200" title="Logout">
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>
      
      <main className="flex-grow w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-10 animate-in fade-in zoom-in-95 duration-300">
        {children}
      </main>
    </div>
  );
};

export default Layout;
