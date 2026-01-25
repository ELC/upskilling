import { useEffect, useState } from 'react';
import { progressApi } from '../services/api';
import type { UserCareerPathDetail, UserPathAssignment } from '../types';
import { Calendar, ChevronRight, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function DevelopmentPlansPage() {
  const [careerPaths, setCareerPaths] = useState<UserCareerPathDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const data = await progressApi.getCareerPaths();
        setCareerPaths(data);
      } catch (error) {
        console.error('Failed to fetch career paths:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPaths();
  }, []);

  const getStatusIcon = (status: string, validationStatus: string) => {
    if (validationStatus === 'Approved') {
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    }
    if (status === 'Completed') {
      return <Clock className="w-5 h-5 text-yellow-400" />;
    }
    if (status === 'In Progress') {
      return <AlertCircle className="w-5 h-5 text-primary-400" />;
    }
    return <Clock className="w-5 h-5 text-dark-500" />;
  };

  const getStatusBadge = (status: string, validationStatus: string) => {
    if (validationStatus === 'Approved') {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded-full">
          Approved
        </span>
      );
    }
    if (validationStatus === 'Rejected') {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-400 rounded-full">
          Rejected
        </span>
      );
    }
    if (status === 'Completed') {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-yellow-500/20 text-yellow-400 rounded-full">
          Pending Review
        </span>
      );
    }
    if (status === 'In Progress') {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-primary-500/20 text-primary-400 rounded-full">
          In Progress
        </span>
      );
    }
    return (
      <span className="px-2 py-1 text-xs font-medium bg-dark-700 text-dark-400 rounded-full">
        Pending
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-dark-100">Development Plans</h1>
        <p className="mt-2 text-dark-400">
          Track your career progress and assigned learning paths.
        </p>
      </div>

      {careerPaths.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📋</span>
          </div>
          <h3 className="text-lg font-medium text-dark-100 mb-2">No development plans yet</h3>
          <p className="text-dark-500">
            Your mentor will assign you a career path to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {careerPaths.map((careerPath) => (
            <div key={careerPath.userCareerPathId} className="card">
              {/* Career path header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-dark-100">
                      {careerPath.careerName}
                    </h2>
                    {careerPath.careerSpecialization && (
                      <p className="text-dark-400">{careerPath.careerSpecialization}</p>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-dark-100">
                    {careerPath.overallProgressPercent}%
                  </p>
                  <p className="text-dark-500 text-sm">overall progress</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="mb-6">
                <div className="progress-bar h-3">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${careerPath.overallProgressPercent}%` }}
                  />
                </div>
              </div>

              {/* Dates */}
              <div className="flex items-center gap-6 mb-6 text-sm">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-dark-500" />
                  <span className="text-dark-400">Started:</span>
                  <span className="text-dark-200">
                    {new Date(careerPath.startDate).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-dark-500" />
                  <span className="text-dark-400">Target:</span>
                  <span className="text-dark-200">
                    {new Date(careerPath.endDate).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Path assignments */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-dark-400 uppercase tracking-wider">
                  Learning Paths
                </h3>
                {careerPath.pathAssignments.map((assignment) => (
                  <div
                    key={assignment.userPathAssignmentId}
                    className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg hover:bg-dark-800 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center gap-4">
                      {getStatusIcon(assignment.status, assignment.mentorValidationStatus)}
                      <div>
                        <p className="font-medium text-dark-100">
                          Path #{assignment.pathTemplateId}
                        </p>
                        <p className="text-sm text-dark-500">
                          {new Date(assignment.startDate).toLocaleDateString()} -{' '}
                          {new Date(assignment.deadline).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-medium text-dark-100">{assignment.progressPercent}%</p>
                        {getStatusBadge(assignment.status, assignment.mentorValidationStatus)}
                      </div>
                      <ChevronRight className="w-5 h-5 text-dark-500 group-hover:text-dark-300 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
