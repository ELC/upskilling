import { useEffect, useState } from 'react';
import { progressApi } from '../services/api';
import type { UserPathAssignmentDetail } from '../types';
import { CheckCircle, XCircle, Clock, User, Calendar, ChevronDown, ChevronUp } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function MentorValidationPage() {
  const [pendingAssignments, setPendingAssignments] = useState<UserPathAssignmentDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    fetchPendingValidations();
  }, []);

  const fetchPendingValidations = async () => {
    try {
      const data = await progressApi.getPendingValidations();
      setPendingAssignments(data);
    } catch (error) {
      console.error('Failed to fetch pending validations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (assignmentId: number) => {
    setActionLoading(assignmentId);
    try {
      await progressApi.approveAssignment(assignmentId);
      setPendingAssignments((prev) =>
        prev.filter((a) => a.user_path_assignment_id !== assignmentId)
      );
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (assignmentId: number) => {
    setActionLoading(assignmentId);
    try {
      await progressApi.rejectAssignment(assignmentId);
      setPendingAssignments((prev) =>
        prev.filter((a) => a.user_path_assignment_id !== assignmentId)
      );
    } catch (error) {
      console.error('Failed to reject:', error);
    } finally {
      setActionLoading(null);
    }
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
        <h1 className="text-3xl font-bold text-dark-100">Mentor Validation</h1>
        <p className="mt-2 text-dark-400">
          Review and validate completed learning paths from your mentees.
        </p>
      </div>

      {/* Stats */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-yellow-600/20 flex items-center justify-center">
            <Clock className="w-6 h-6 text-yellow-400" />
          </div>
          <div>
            <p className="text-dark-500 text-sm">Pending Validations</p>
            <p className="text-2xl font-bold text-dark-100">{pendingAssignments.length}</p>
          </div>
        </div>
      </div>

      {/* Pending validations list */}
      {pendingAssignments.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-400" />
          </div>
          <h3 className="text-lg font-medium text-dark-100 mb-2">All caught up!</h3>
          <p className="text-dark-500">No pending validations at the moment.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingAssignments.map((assignment) => (
            <div key={assignment.user_path_assignment_id} className="card">
              <div
                className="flex items-start justify-between cursor-pointer"
                onClick={() =>
                  setExpandedId(
                    expandedId === assignment.user_path_assignment_id
                      ? null
                      : assignment.user_path_assignment_id
                  )
                }
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
                    <User className="w-6 h-6 text-primary-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-dark-100">
                      {assignment.path_template?.name || `Path #${assignment.path_template_id}`}
                    </h3>
                    <p className="text-dark-400 text-sm">
                      Completed on {new Date(assignment.deadline).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-3 py-1 text-xs font-medium bg-yellow-500/20 text-yellow-400 rounded-full">
                    Pending Review
                  </span>
                  {expandedId === assignment.user_path_assignment_id ? (
                    <ChevronUp className="w-5 h-5 text-dark-500" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-dark-500" />
                  )}
                </div>
              </div>

              {/* Expanded details */}
              {expandedId === assignment.user_path_assignment_id && (
                <div className="mt-6 pt-6 border-t border-dark-800">
                  {/* Assignment details */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-dark-500" />
                      <span className="text-dark-400 text-sm">Start:</span>
                      <span className="text-dark-200 text-sm">
                        {new Date(assignment.start_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-dark-500" />
                      <span className="text-dark-400 text-sm">Deadline:</span>
                      <span className="text-dark-200 text-sm">
                        {new Date(assignment.deadline).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Step progress */}
                  {assignment.step_progress && assignment.step_progress.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-dark-400 uppercase tracking-wider mb-3">
                        Completed Steps
                      </h4>
                      <div className="space-y-2">
                        {assignment.step_progress.map((sp) => (
                          <div
                            key={sp.user_step_progress_id}
                            className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <CheckCircle className="w-4 h-4 text-green-400" />
                              <span className="text-dark-200 text-sm">
                                {sp.step?.name || `Step #${sp.step_id}`}
                              </span>
                            </div>
                            <span className="text-dark-400 text-sm">{sp.progress_percent}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleApprove(assignment.user_path_assignment_id);
                      }}
                      disabled={actionLoading === assignment.user_path_assignment_id}
                      className="btn btn-primary flex items-center gap-2"
                    >
                      {actionLoading === assignment.user_path_assignment_id ? (
                        <LoadingSpinner size="sm" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
                      )}
                      Approve
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReject(assignment.user_path_assignment_id);
                      }}
                      disabled={actionLoading === assignment.user_path_assignment_id}
                      className="btn bg-red-600/20 text-red-400 hover:bg-red-600/30 flex items-center gap-2"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
