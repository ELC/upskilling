import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { progressApi } from '../services/api';
import type { DashboardStats } from '../types';
import { TrendingUp, Target, Award, Clock } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await progressApi.getDashboard();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div>
        <h1 className="text-3xl font-bold text-dark-100">
          Welcome back, {user?.full_name?.split(' ')[0]}!
        </h1>
        <p className="mt-2 text-dark-400">
          Track your progress and continue your career development journey.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-600/20 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <p className="text-dark-500 text-sm">Overall Progress</p>
              <p className="text-2xl font-bold text-dark-100">{stats?.overall_progress || 0}%</p>
            </div>
          </div>
          <div className="mt-4 progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${stats?.overall_progress || 0}%` }}
            />
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-secondary-600/20 flex items-center justify-center">
              <Target className="w-6 h-6 text-secondary-400" />
            </div>
            <div>
              <p className="text-dark-500 text-sm">Current Path</p>
              <p className="text-lg font-semibold text-dark-100 truncate max-w-[150px]">
                {stats?.current_path || 'No active path'}
              </p>
            </div>
          </div>
          <div className="mt-4 progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${stats?.current_path_progress || 0}%` }}
            />
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-600/20 flex items-center justify-center">
              <Award className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-dark-500 text-sm">Skills Obtained</p>
              <p className="text-2xl font-bold text-dark-100">{stats?.skills_obtained || 0}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-600/20 flex items-center justify-center">
              <Clock className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-dark-500 text-sm">Paths Remaining</p>
              <p className="text-2xl font-bold text-dark-100">{stats?.paths_remaining || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Current career */}
      {stats?.current_career && (
        <div className="card">
          <h2 className="text-xl font-semibold text-dark-100 mb-4">Current Career Track</h2>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
            <div>
              <h3 className="text-lg font-medium text-dark-100">{stats.current_career}</h3>
              <p className="text-dark-400">
                {stats.current_path
                  ? `Currently working on: ${stats.current_path}`
                  : 'Ready to start your next path'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a
          href="/development-plans"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-600/20 flex items-center justify-center group-hover:bg-primary-600/30 transition-colors">
              <span className="text-xl">📚</span>
            </div>
            <div>
              <h3 className="text-dark-100 font-medium group-hover:text-primary-400 transition-colors">
                View Development Plans
              </h3>
              <p className="text-dark-500 text-sm">Track your assigned paths</p>
            </div>
          </div>
        </a>

        <a
          href="/learning-paths"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-secondary-600/20 flex items-center justify-center group-hover:bg-secondary-600/30 transition-colors">
              <span className="text-xl">🎓</span>
            </div>
            <div>
              <h3 className="text-dark-100 font-medium group-hover:text-secondary-400 transition-colors">
                Browse Learning Paths
              </h3>
              <p className="text-dark-500 text-sm">Explore available courses</p>
            </div>
          </div>
        </a>

        <a
          href="/my-bio"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-600/20 flex items-center justify-center group-hover:bg-blue-600/30 transition-colors">
              <span className="text-xl">👤</span>
            </div>
            <div>
              <h3 className="text-dark-100 font-medium group-hover:text-blue-400 transition-colors">
                Update Profile
              </h3>
              <p className="text-dark-500 text-sm">Manage your bio and settings</p>
            </div>
          </div>
        </a>
      </div>
    </div>
  );
}
