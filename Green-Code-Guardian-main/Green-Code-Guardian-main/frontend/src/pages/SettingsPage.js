import React, { useState, useEffect } from 'react';
import { Settings, Lock, BarChart3, Save, AlertCircle, CheckCircle, Eye, EyeOff, Leaf } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

const Section = ({ icon: Icon, title, children }) => (
  <div className="bg-gray-800 rounded-lg p-6 mb-6">
    <div className="flex items-center gap-2 mb-5">
      <Icon size={18} className="text-green-400" />
      <h2 className="text-lg font-semibold text-white">{title}</h2>
    </div>
    {children}
  </div>
);

const InputField = ({ label, value, onChange, type = 'text', placeholder, hint, error, showToggle, isShown, onToggleShow }) => {
  return (
    <div className="mb-4">
      <label className="block text-gray-300 text-sm font-medium mb-2">{label}</label>
      <div className="relative">
        <input
          type={showToggle && isShown ? 'text' : type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full bg-gray-700 border ${error ? 'border-red-500' : 'border-gray-600'} text-white rounded-lg px-4 py-2.5 text-sm
            placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all pr-10`}
        />
        {showToggle && (
          <button
            type="button"
            onClick={onToggleShow}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200"
          >
            {isShown ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
      {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
      {hint && <p className="text-gray-400 text-xs mt-1">{hint}</p>}
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon }) => (
  <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-xs uppercase mb-1">{label}</p>
        <p className="text-white text-2xl font-bold">{value}</p>
      </div>
      <Icon size={24} className="text-green-400" />
    </div>
  </div>
);

const TabButton = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
      active
        ? 'bg-green-600 text-white'
        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
    }`}
  >
    {children}
  </button>
);

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('password');
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  
  // Password state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordError, setPasswordError] = useState('');
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  
  // Usage stats state
  const [usageStats, setUsageStats] = useState({
    totalScans: 0,
    totalCO2Saved: '0.00',
    teamsJoined: 0,
    projectsTracked: 0,
    avgGreenScore: 0
  });

  // Load usage stats on mount
  useEffect(() => {
    fetchUsageStats();
  }, []);

  const fetchUsageStats = async () => {
    try {
      setStatsLoading(true);
      const response = await api.get('/users/usage-stats');
      setUsageStats(response.data);
    } catch (error) {
      console.error('Error fetching usage stats:', error);
      toast.error('Failed to load usage statistics');
    } finally {
      setStatsLoading(false);
    }
  };

  const updatePasswordField = (field, value) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
    setPasswordError('');
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const validatePassword = () => {
    if (!passwordData.currentPassword) {
      setPasswordError('Current password is required');
      return false;
    }
    if (!passwordData.newPassword) {
      setPasswordError('New password is required');
      return false;
    }
    if (passwordData.newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters');
      return false;
    }
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError('Passwords do not match');
      return false;
    }
    if (passwordData.currentPassword === passwordData.newPassword) {
      setPasswordError('New password must be different from current password');
      return false;
    }
    return true;
  };

  const handleChangePassword = async () => {
    if (!validatePassword()) return;

    try {
      setLoading(true);
      setPasswordSuccess(false);
      
      await api.post('/auth/change-password', {
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword
      });
      
      toast.success('Password changed successfully');
      setPasswordSuccess(true);
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      
      setTimeout(() => setPasswordSuccess(false), 5000);
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to change password';
      setPasswordError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-2 mb-8">
        <Settings size={24} className="text-green-400" />
        <h1 className="text-2xl font-bold text-white">Account Settings</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-700">
        <TabButton 
          active={activeTab === 'password'} 
          onClick={() => setActiveTab('password')}
        >
          <Lock size={16} className="inline mr-2" />
          Password
        </TabButton>
        <TabButton 
          active={activeTab === 'usage'} 
          onClick={() => setActiveTab('usage')}
        >
          <BarChart3 size={16} className="inline mr-2" />
          Usage Statistics
        </TabButton>
      </div>

      {/* Password Change Tab */}
      {activeTab === 'password' && (
        <Section icon={Lock} title="Change Password">
          <div className="space-y-4">
            {passwordSuccess && (
              <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle size={20} className="text-green-400" />
                <p className="text-green-300 font-medium">Password changed successfully!</p>
              </div>
            )}
            
            {passwordError && (
              <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle size={20} className="text-red-400" />
                <p className="text-red-300 font-medium">{passwordError}</p>
              </div>
            )}

            <InputField
              label="Current Password"
              value={passwordData.currentPassword}
              onChange={(e) => updatePasswordField('currentPassword', e.target.value)}
              type="password"
              placeholder="Enter your current password"
              showToggle={true}
              isShown={showPasswords.current}
              onToggleShow={() => togglePasswordVisibility('current')}
              hint="Required for security verification"
            />

            <InputField
              label="New Password"
              value={passwordData.newPassword}
              onChange={(e) => updatePasswordField('newPassword', e.target.value)}
              type="password"
              placeholder="Enter your new password"
              showToggle={true}
              isShown={showPasswords.new}
              onToggleShow={() => togglePasswordVisibility('new')}
              hint="Minimum 8 characters"
            />

            <InputField
              label="Confirm New Password"
              value={passwordData.confirmPassword}
              onChange={(e) => updatePasswordField('confirmPassword', e.target.value)}
              type="password"
              placeholder="Confirm your new password"
              showToggle={true}
              isShown={showPasswords.confirm}
              onToggleShow={() => togglePasswordVisibility('confirm')}
              hint="Must match your new password"
            />

            <button
              onClick={handleChangePassword}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2 mt-6"
            >
              <Save size={18} />
              {loading ? 'Changing Password...' : 'Change Password'}
            </button>
          </div>
        </Section>
      )}

      {/* Usage Statistics Tab */}
      {activeTab === 'usage' && (
        <Section icon={BarChart3} title="Your Usage Statistics">
          {statsLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-green-400"></div>
              <p className="ml-3 text-gray-300">Loading statistics...</p>
            </div>
          ) : (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <StatCard
                  label="Total Scans"
                  value={usageStats.totalScans}
                  icon={Leaf}
                />
                <StatCard
                  label="CO₂ Saved (kg)"
                  value={usageStats.totalCO2Saved}
                  icon={Leaf}
                />
                <StatCard
                  label="Teams Joined"
                  value={usageStats.teamsJoined}
                  icon={Leaf}
                />
                <StatCard
                  label="Projects Tracked"
                  value={usageStats.projectsTracked}
                  icon={Leaf}
                />
              </div>

              <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm uppercase mb-2">Average Green Score</p>
                    <div className="flex items-end gap-2">
                      <span className="text-4xl font-bold text-white">{usageStats.avgGreenScore}</span>
                      <span className="text-gray-400 text-lg mb-1">/100</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-24 h-24 rounded-full border-8 border-green-400 flex items-center justify-center">
                      <span className="text-2xl font-bold text-green-400">{usageStats.avgGreenScore}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={fetchUsageStats}
                disabled={statsLoading}
                className="w-full mt-6 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 rounded-lg transition-all"
              >
                Refresh Statistics
              </button>
            </div>
          )}
        </Section>
      )}

      <div className="text-center text-gray-400 text-xs pt-4 border-t border-gray-700">
        <p>Your account information is secure and encrypted</p>
      </div>
    </div>
  );
}
