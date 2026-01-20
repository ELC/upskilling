import { useEffect, useState } from 'react';
import { teamsApi, progressApi } from '../services/api';
import type { TeamWithMembers, MenteeProgressSummary } from '../types';
import { Users, UserPlus, TrendingUp, AlertCircle, ChevronRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function TeamManagementPage() {
  const [teams, setTeams] = useState<TeamWithMembers[]>([]);
  const [teamProgress, setTeamProgress] = useState<MenteeProgressSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teamsData, progressData] = await Promise.all([
          teamsApi.getMyTeams(),
          progressApi.getTeamProgress(),
        ]);
        setTeams(teamsData);
        setTeamProgress(progressData);
        if (teamsData.length > 0) {
          setSelectedTeam(teamsData[0].team_id);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const currentTeam = teams.find((t) => t.team_id === selectedTeam);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-100">Team Management</h1>
          <p className="mt-2 text-dark-400">Manage your team members and track their progress.</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <UserPlus className="w-4 h-4" />
          Add Member
        </button>
      </div>

      {teams.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <Users className="w-8 h-8 text-dark-500" />
          </div>
          <h3 className="text-lg font-medium text-dark-100 mb-2">No teams yet</h3>
          <p className="text-dark-500">You don't manage any teams currently.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Team selector */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-sm font-medium text-dark-400 uppercase tracking-wider">
              Your Teams
            </h2>
            {teams.map((team) => (
              <button
                key={team.team_id}
                onClick={() => setSelectedTeam(team.team_id)}
                className={`w-full card card-hover text-left ${
                  selectedTeam === team.team_id ? 'border-primary-600/50 bg-dark-900/80' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
                      <Users className="w-5 h-5 text-primary-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-dark-100">{team.name}</h3>
                      <p className="text-dark-500 text-sm">{team.members.length} members</p>
                    </div>
                  </div>
                  <ChevronRight
                    className={`w-5 h-5 ${
                      selectedTeam === team.team_id ? 'text-primary-400' : 'text-dark-500'
                    }`}
                  />
                </div>
              </button>
            ))}
          </div>

          {/* Team details and progress */}
          <div className="lg:col-span-2 space-y-6">
            {currentTeam && (
              <>
                {/* Team header */}
                <div className="card">
                  <h2 className="text-xl font-semibold text-dark-100 mb-4">{currentTeam.name}</h2>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-dark-800/50 rounded-lg">
                      <p className="text-2xl font-bold text-dark-100">
                        {currentTeam.members.length}
                      </p>
                      <p className="text-dark-500 text-sm">Members</p>
                    </div>
                    <div className="text-center p-4 bg-dark-800/50 rounded-lg">
                      <p className="text-2xl font-bold text-primary-400">
                        {teamProgress.filter((p) => p.pending_validation > 0).length}
                      </p>
                      <p className="text-dark-500 text-sm">Pending Reviews</p>
                    </div>
                    <div className="text-center p-4 bg-dark-800/50 rounded-lg">
                      <p className="text-2xl font-bold text-green-400">
                        {Math.round(
                          teamProgress.reduce((sum, p) => sum + p.overall_progress_percent, 0) /
                            (teamProgress.length || 1)
                        )}
                        %
                      </p>
                      <p className="text-dark-500 text-sm">Avg Progress</p>
                    </div>
                  </div>
                </div>

                {/* Team members progress */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-dark-100 mb-4">Member Progress</h3>
                  <div className="space-y-4">
                    {teamProgress.length === 0 ? (
                      <p className="text-dark-500 text-center py-8">
                        No progress data available for team members.
                      </p>
                    ) : (
                      teamProgress.map((member) => (
                        <div
                          key={member.user_id}
                          className="p-4 bg-dark-800/50 rounded-lg hover:bg-dark-800 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-600 to-secondary-600 flex items-center justify-center">
                                <span className="text-white font-medium">
                                  {member.full_name.charAt(0).toUpperCase()}
                                </span>
                              </div>
                              <div>
                                <h4 className="font-medium text-dark-100">{member.full_name}</h4>
                                <p className="text-dark-500 text-sm">{member.career_name}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              {member.pending_validation > 0 && (
                                <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-yellow-500/20 text-yellow-400 rounded-full">
                                  <AlertCircle className="w-3 h-3" />
                                  {member.pending_validation} pending
                                </span>
                              )}
                              <span className="text-lg font-bold text-dark-100">
                                {member.overall_progress_percent}%
                              </span>
                            </div>
                          </div>

                          <div className="progress-bar mb-2">
                            <div
                              className="progress-bar-fill"
                              style={{ width: `${member.overall_progress_percent}%` }}
                            />
                          </div>

                          <div className="flex items-center justify-between text-xs text-dark-500">
                            <span>
                              {member.paths_completed}/{member.paths_total} paths completed
                            </span>
                            <span>
                              {new Date(member.start_date).toLocaleDateString()} -{' '}
                              {new Date(member.end_date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
