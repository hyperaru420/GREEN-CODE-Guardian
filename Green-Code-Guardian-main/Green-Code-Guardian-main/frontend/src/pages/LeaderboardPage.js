import React, { useState, useEffect } from 'react';
import api from '../services/api';
import MetricCard from '../components/MetricCard';

const LeaderboardPage = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [period, setPeriod] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/leaderboard/me?period=${period}&limit=20`);
      setLeaderboard(response.data.leaderboard);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (score) => {
    if (score >= 90) return '#10B981'; // Green
    if (score >= 80) return '#3B82F6'; // Blue
    if (score >= 70) return '#F59E0B'; // Yellow
    if (score >= 60) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  const getGradeLetter = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">🏆 My Leaderboard</h1>
        <p className="text-gray-300">Your own project rankings based on your sustainability scans</p>
      </div>

      {/* Period Selector */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {['all', 'month', 'week'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === p
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {p === 'all' ? 'All Time' : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Leaderboard */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="w-8 h-8 spinner" />
        </div>
      ) : (
        <div className="space-y-4">
          {leaderboard.map((entry, index) => (
            <div
              key={entry.project}
              className={`bg-gray-800 rounded-lg p-6 border-l-4 ${
                index === 0 ? 'border-yellow-500 bg-gradient-to-r from-yellow-500/10 to-transparent' :
                index === 1 ? 'border-gray-400 bg-gradient-to-r from-gray-400/10 to-transparent' :
                index === 2 ? 'border-orange-600 bg-gradient-to-r from-orange-600/10 to-transparent' :
                'border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                    index === 0 ? 'bg-yellow-500 text-black' :
                    index === 1 ? 'bg-gray-400 text-black' :
                    index === 2 ? 'bg-orange-600 text-white' :
                    'bg-gray-600 text-white'
                  }`}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${entry.rank}`}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">{entry.project}</h3>
                    <p className="text-gray-400 text-sm">
                      {entry.total_scans} scans • Last: {new Date(entry.last_scan).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center font-bold text-xl mb-1"
                      style={{ backgroundColor: getGradeColor(entry.green_score) }}
                    >
                      {getGradeLetter(entry.green_score)}
                    </div>
                    <p className="text-gray-300 text-sm">Grade</p>
                  </div>

                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">
                      {entry.green_score.toFixed(1)}
                    </div>
                    <p className="text-gray-300 text-sm">Green Score</p>
                  </div>

                  <div className="text-center">
                    <div className="text-xl font-semibold text-green-400">
                      {entry.carbon_emissions.toFixed(1)}g
                    </div>
                    <p className="text-gray-300 text-sm">CO₂</p>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {leaderboard.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏆</div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">No projects yet</h3>
              <p className="text-gray-500">Be the first to scan a project and claim the top spot!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LeaderboardPage;