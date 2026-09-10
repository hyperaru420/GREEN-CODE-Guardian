import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import MetricCard from '../components/MetricCard';

const TeamsPage = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamAnalytics, setTeamAnalytics] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTeam, setNewTeam] = useState({
    name: '',
    description: '',
    public: false
  });
  const [inviteEmail, setInviteEmail] = useState('');
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) fetchTeams();
  }, [user]);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const userId = user?.id;
      const response = await api.get(`/teams/list?user_id=${userId}`);
      setTeams(response.data.teams);
    } catch (error) {
      console.error('Failed to fetch teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTeam = async () => {
    try {
      const userId = user?.id;
      await api.post('/teams/create', {
        ...newTeam,
        owner_id: userId
      });
      setShowCreateForm(false);
      setNewTeam({ name: '', description: '', public: false });
      fetchTeams();
      alert('Team created successfully!');
    } catch (error) {
      console.error('Failed to create team:', error);
      alert('Failed to create team');
    }
  };

  const inviteMember = async (teamId) => {
    if (!inviteEmail) {
      alert('Please enter an email address');
      return;
    }

    try {
      const userId = user?.id;
      await api.post('/teams/invite', {
        team_id: teamId,
        user_email: inviteEmail,
        inviter_id: userId
      });
      setInviteEmail('');
      alert('Invitation sent!');
    } catch (error) {
      console.error('Failed to invite member:', error);
      alert('Failed to send invitation');
    }
  };

  const fetchTeamAnalytics = async (teamId) => {
    try {
      const response = await api.get(`/teams/${teamId}/analytics`);
      setTeamAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch team analytics:', error);
    }
  };

  const selectTeam = async (team) => {
    setSelectedTeam(team);
    await fetchTeamAnalytics(team.id);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">👥 Teams</h1>
          <p className="text-gray-300">Collaborate on sustainability goals with your team</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Teams List */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Your Teams</h2>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  + Create
                </button>
              </div>

              {loading ? (
                <div className="flex justify-center items-center h-32">
                  <div className="w-6 h-6 spinner" />
                </div>
              ) : teams.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-gray-400 mb-2">No teams yet</p>
                  <p className="text-gray-500 text-sm">Create your first team to start collaborating</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {teams.map((team) => (
                    <div
                      key={team.id}
                      onClick={() => selectTeam(team)}
                      className={`p-4 rounded-lg cursor-pointer transition-colors ${
                        selectedTeam?.id === team.id
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">{team.name}</h3>
                          <p className="text-sm opacity-75">{team.member_count} members</p>
                        </div>
                        {team.owner && (
                          <span className="text-xs bg-yellow-500 text-black px-2 py-1 rounded">
                            Owner
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Team Details */}
          <div className="lg:col-span-2">
            {selectedTeam ? (
              <div className="space-y-6">
                {/* Team Header */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-semibold text-white">{selectedTeam.name}</h2>
                      <p className="text-gray-400">{selectedTeam.member_count} members</p>
                    </div>
                    {selectedTeam.owner && (
                      <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-sm font-medium">
                        Team Owner
                      </span>
                    )}
                  </div>

                  {/* Invite Member */}
                  {selectedTeam.owner && (
                    <div className="flex space-x-2">
                      <input
                        type="email"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        placeholder="Enter email to invite"
                        className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                      <button
                        onClick={() => inviteMember(selectedTeam.id)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Invite
                      </button>
                    </div>
                  )}
                </div>

                {/* Team Analytics */}
                {teamAnalytics && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <MetricCard
                      title="Team Green Score"
                      value={teamAnalytics.avg_green_score}
                      unit=""
                      icon="🌿"
                      color="green"
                    />
                    <MetricCard
                      title="Total Carbon"
                      value={teamAnalytics.total_carbon}
                      unit="g CO₂"
                      icon="🌍"
                      color="red"
                    />
                    <MetricCard
                      title="Total Scans"
                      value={teamAnalytics.total_scans}
                      unit=""
                      icon="📊"
                      color="blue"
                    />
                    <MetricCard
                      title="Active Projects"
                      value={teamAnalytics.total_projects}
                      unit=""
                      icon="📁"
                      color="purple"
                    />
                  </div>
                )}

                {/* Best Project */}
                {teamAnalytics?.best_project && (
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-2">🏆 Best Project</h3>
                    <p className="text-green-400 text-xl font-bold">{teamAnalytics.best_project}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg p-6 text-center">
                <div className="text-6xl mb-4">👥</div>
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Select a Team</h3>
                <p className="text-gray-500">Choose a team from the list to view details and analytics</p>
              </div>
            )}
          </div>
        </div>

        {/* Create Team Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold text-white mb-4">Create New Team</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Team Name</label>
                  <input
                    type="text"
                    value={newTeam.name}
                    onChange={(e) => setNewTeam({...newTeam, name: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Enter team name"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    value={newTeam.description}
                    onChange={(e) => setNewTeam({...newTeam, description: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Team description (optional)"
                    rows="3"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newTeam.public}
                    onChange={(e) => setNewTeam({...newTeam, public: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500"
                  />
                  <label className="ml-2 text-gray-300">Public team (anyone can join)</label>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={createTeam}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Create Team
                  </button>
                  <button
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
  );
};

export default TeamsPage;