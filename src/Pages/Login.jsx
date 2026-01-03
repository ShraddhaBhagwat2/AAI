import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Phone, ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';
import emblem from '../assets/emblem.svg';
import { loginUser } from '../utils/api';

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState('citizen'); // citizen, officer, admin
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    mobile: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await loginUser({
        mobile_number: formData.mobile,
        password: formData.password
      });

      // Store role locally for UI purposes
      localStorage.setItem('userRole', role);

      // Navigate based on role
      if (role === 'citizen') navigate('/citizen');
      if (role === 'officer') navigate('/officer');
      if (role === 'admin') navigate('/admin');
      
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        
        {/* Header */}
        <div className="bg-blue-600 p-6 text-center">
          <div className="mx-auto bg-white w-14 h-14 rounded-full flex items-center justify-center mb-3">
            <img src={emblem} alt="emblem" className="w-10 h-10" />
          </div>
          <h1 className="text-2xl font-bold text-white">CivicConnect</h1>
          <p className="text-blue-100 text-sm">Unified Grievance Redressal Portal</p>
        </div>

        {/* Login Form */}
        <div className="p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          {/* Role Selector */}
          <div className="flex bg-slate-100 p-1 rounded-lg mb-6">
            {['citizen', 'officer', 'admin'].map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRole(r)}
                className={`flex-1 py-2 text-sm font-bold capitalize rounded-md transition-all ${
                  role === r ? 'bg-white shadow text-blue-600' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Mobile Number */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                {role === 'citizen' ? 'Mobile Number' : 'Official ID / Mobile'}
              </label>
              <div className="relative">
                <div className="absolute left-3 top-3 text-slate-400">
                  <Phone size={18} />
                </div>
                <input 
                  type="text"
                  name="mobile"
                  value={formData.mobile}
                  onChange={handleChange}
                  placeholder={role === 'citizen' ? "+91 98765 43210" : "EMP-ID or Mobile"}
                  required
                  className="w-full pl-10 p-3 bg-slate-50 border border-slate-200 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute left-3 top-3 text-slate-400">
                  <Shield size={18} />
                </div>
                <input 
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••"
                  required
                  className="w-full pl-10 pr-10 p-3 bg-slate-50 border border-slate-200 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="text-right">
              <Link to="/forgot-password" className="text-xs text-blue-600 hover:text-blue-700 font-semibold hover:underline">
                Forgot Password?
              </Link>
            </div>

            {/* Submit Button */}
            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Logging in...
                </>
              ) : (
                <>
                  Login as {role} <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Signup Link */}
          <div className="mt-6 text-center text-sm text-slate-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 font-bold hover:text-blue-700 hover:underline">
              Sign Up
            </Link>
          </div>

          {/* WhatsApp Option for Citizens */}
          {role === 'citizen' && (
            <div className="mt-4 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
              Or login via <span className="text-green-600 font-bold cursor-pointer hover:underline">WhatsApp Bot</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}