import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const NotificationsPage = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    slack_notifications: false,
    carbon_threshold_alerts: true,
    achievement_notifications: true,
    daily_digest: false,
    carbon_threshold: 100
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchNotifications();
      fetchPreferences();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications/list');
      setNotifications(response.data.notifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/notifications/preferences');
      setPreferences(response.data.preferences);
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePreferences = async () => {
    try {
      setSaving(true);
      await api.put('/notifications/preferences', preferences);
      alert('Preferences updated successfully!');
    } catch (error) {
      console.error('Failed to update preferences:', error);
      alert('Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/mark-as-read/${notificationId}`);
      setNotifications(notifications.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      ));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark-all-read');
      setNotifications(notifications.map(n => ({ ...n, read: true })));
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'achievement': return '🏆';
      case 'carbon_alert': return '🌍';
      case 'team_invite': return '👥';
      case 'webhook': return '🔗';
      default: return '📢';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'achievement': return 'text-yellow-400';
      case 'carbon_alert': return 'text-red-400';
      case 'team_invite': return 'text-blue-400';
      case 'webhook': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="w-8 h-8 spinner" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">🔔 Notifications</h1>
        <p className="text-gray-300">Stay updated on your sustainability progress and achievements</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Notifications List */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Recent Notifications</h2>
                <button
                  onClick={markAllAsRead}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                >
                  Mark All Read
                </button>
              </div>

              {notifications.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">📭</div>
                  <p className="text-gray-400 mb-2">No notifications yet</p>
                  <p className="text-gray-500 text-sm">You'll receive notifications for achievements and alerts here</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 rounded-lg border transition-colors ${
                        notification.read
                          ? 'bg-gray-700 border-gray-600'
                          : 'bg-gray-750 border-green-500/30'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`text-2xl ${getNotificationColor(notification.type)}`}>
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-white">{notification.title}</h3>
                            <span className="text-xs text-gray-400">
                              {new Date(notification.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-gray-300 text-sm mt-1">{notification.message}</p>
                          {!notification.read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="mt-2 px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors"
                            >
                              Mark as Read
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Preferences */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Notification Preferences</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-gray-300">Email Notifications</label>
                  <input
                    type="checkbox"
                    checked={preferences.email_notifications}
                    onChange={(e) => setPreferences({...preferences, email_notifications: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-gray-300">Slack Notifications</label>
                  <input
                    type="checkbox"
                    checked={preferences.slack_notifications}
                    onChange={(e) => setPreferences({...preferences, slack_notifications: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-gray-300">Carbon Threshold Alerts</label>
                  <input
                    type="checkbox"
                    checked={preferences.carbon_threshold_alerts}
                    onChange={(e) => setPreferences({...preferences, carbon_threshold_alerts: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-gray-300">Achievement Notifications</label>
                  <input
                    type="checkbox"
                    checked={preferences.achievement_notifications}
                    onChange={(e) => setPreferences({...preferences, achievement_notifications: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-gray-300">Daily Digest</label>
                  <input
                    type="checkbox"
                    checked={preferences.daily_digest}
                    onChange={(e) => setPreferences({...preferences, daily_digest: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Carbon Threshold (g CO₂)</label>
                  <input
                    type="number"
                    value={preferences.carbon_threshold}
                    onChange={(e) => setPreferences({...preferences, carbon_threshold: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    min="0"
                  />
                </div>

                <button
                  onClick={updatePreferences}
                  disabled={saving}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-gray-800 rounded-lg p-6 mt-6">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Notifications</span>
                  <span className="text-white">{notifications.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Unread</span>
                  <span className="text-yellow-400">{notifications.filter(n => !n.read).length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Achievements</span>
                  <span className="text-yellow-400">{notifications.filter(n => n.type === 'achievement').length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Alerts</span>
                  <span className="text-red-400">{notifications.filter(n => n.type === 'carbon_alert').length}</span>
                </div>
              </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationsPage;