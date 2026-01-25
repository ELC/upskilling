import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usersApi } from '../services/api';
import { User, Mail, Edit2, Save, X, Shield } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function MyBioPage() {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.fullName || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSave = async () => {
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      await usersApi.updateMe({ fullName, bio });
      await refreshUser();
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })
        .response?.data?.detail;
      setError(detail || 'Failed to update profile.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFullName(user?.fullName || '');
    setBio(user?.bio || '');
    setIsEditing(false);
    setError('');
  };

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold text-dark-100">My Profile</h1>
        <p className="mt-2 text-dark-400">Manage your account information and bio.</p>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">
          {success}
        </div>
      )}

      {/* Profile card */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-600 to-secondary-600 flex items-center justify-center">
              <span className="text-white text-3xl font-bold">
                {user?.fullName?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-dark-100">{user?.fullName}</h2>
              <p className="text-dark-400">{user?.email}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {user?.roles.map((role) => (
                  <span
                    key={role.roleId}
                    className="px-2 py-1 text-xs font-medium bg-primary-600/20 text-primary-400 rounded-full"
                  >
                    {role.name}
                  </span>
                ))}
              </div>
            </div>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="btn btn-secondary flex items-center gap-2"
            >
              <Edit2 className="w-4 h-4" />
              Edit
            </button>
          )}
        </div>

        <div className="space-y-6">
          {/* Full name */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              <User className="w-4 h-4 inline mr-2" />
              Full Name
            </label>
            {isEditing ? (
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input"
                placeholder="Your full name"
              />
            ) : (
              <p className="text-dark-100 py-2">{user?.fullName}</p>
            )}
          </div>

          {/* Email (read-only) */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              <Mail className="w-4 h-4 inline mr-2" />
              Email Address
            </label>
            <p className="text-dark-100 py-2">{user?.email}</p>
            <p className="text-xs text-dark-500">Email cannot be changed</p>
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              <Shield className="w-4 h-4 inline mr-2" />
              Bio
            </label>
            {isEditing ? (
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="input min-h-[120px] resize-none"
                placeholder="Tell us about yourself, your experience, and your career goals..."
              />
            ) : (
              <p className="text-dark-400 py-2">
                {user?.bio || 'No bio added yet. Click Edit to add one!'}
              </p>
            )}
          </div>

          {/* Action buttons */}
          {isEditing && (
            <div className="flex items-center gap-3 pt-4 border-t border-dark-800">
              <button
                onClick={handleSave}
                disabled={isLoading}
                className="btn btn-primary flex items-center gap-2"
              >
                {isLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                Save Changes
              </button>
              <button
                onClick={handleCancel}
                disabled={isLoading}
                className="btn btn-ghost flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Account info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-100 mb-4">Account Information</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center py-3 border-b border-dark-800">
            <span className="text-dark-400">Member since</span>
            <span className="text-dark-100">
              {user?.createdAt
                ? new Date(user.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })
                : '-'}
            </span>
          </div>
          <div className="flex justify-between items-center py-3">
            <span className="text-dark-400">Roles</span>
            <span className="text-dark-100">
              {user?.roles.map((r) => r.name).join(', ') || 'No roles assigned'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
