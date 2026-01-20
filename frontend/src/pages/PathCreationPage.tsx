import { useEffect, useState } from 'react';
import { careersApi, pathsApi } from '../services/api';
import type { Career, PathTemplate, PathTemplateWithSteps } from '../types';
import { Plus, Edit2, Trash2, BookOpen, Clock, ChevronDown, ChevronUp, Save } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function PathCreationPage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [paths, setPaths] = useState<PathTemplate[]>([]);
  const [selectedPath, setSelectedPath] = useState<PathTemplateWithSteps | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedPathId, setExpandedPathId] = useState<number | null>(null);

  // Form state
  const [showNewPathForm, setShowNewPathForm] = useState(false);
  const [newPath, setNewPath] = useState({
    name: '',
    description: '',
    career_id: 0,
    duration_hours: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [careersRes, pathsRes] = await Promise.all([
        careersApi.list(1, 100),
        pathsApi.list(1, 100),
      ]);
      setCareers(careersRes.items);
      setPaths(pathsRes.items);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExpandPath = async (pathId: number) => {
    if (expandedPathId === pathId) {
      setExpandedPathId(null);
      setSelectedPath(null);
      return;
    }

    try {
      const pathData = await pathsApi.get(pathId);
      setSelectedPath(pathData);
      setExpandedPathId(pathId);
    } catch (error) {
      console.error('Failed to fetch path details:', error);
    }
  };

  const handleCreatePath = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await pathsApi.create(newPath);
      setShowNewPathForm(false);
      setNewPath({ name: '', description: '', career_id: 0, duration_hours: 0 });
      fetchData();
    } catch (error) {
      console.error('Failed to create path:', error);
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
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-100">Path Creation</h1>
          <p className="mt-2 text-dark-400">Create and manage learning path templates.</p>
        </div>
        <button
          onClick={() => setShowNewPathForm(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Path
        </button>
      </div>

      {/* New path form */}
      {showNewPathForm && (
        <div className="card">
          <h2 className="text-lg font-semibold text-dark-100 mb-4">Create New Path</h2>
          <form onSubmit={handleCreatePath} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Path Name
                </label>
                <input
                  type="text"
                  value={newPath.name}
                  onChange={(e) => setNewPath({ ...newPath, name: e.target.value })}
                  className="input"
                  placeholder="e.g., React Fundamentals"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Career Track
                </label>
                <select
                  value={newPath.career_id}
                  onChange={(e) => setNewPath({ ...newPath, career_id: parseInt(e.target.value) })}
                  className="input"
                  required
                >
                  <option value={0}>Select a career...</option>
                  {careers.map((career) => (
                    <option key={career.career_id} value={career.career_id}>
                      {career.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Description</label>
              <textarea
                value={newPath.description}
                onChange={(e) => setNewPath({ ...newPath, description: e.target.value })}
                className="input min-h-[80px] resize-none"
                placeholder="Describe what learners will achieve..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Duration (hours)
              </label>
              <input
                type="number"
                value={newPath.duration_hours || ''}
                onChange={(e) =>
                  setNewPath({ ...newPath, duration_hours: parseInt(e.target.value) || 0 })
                }
                className="input w-32"
                min="1"
                required
              />
            </div>

            <div className="flex items-center gap-3 pt-4 border-t border-dark-800">
              <button type="submit" className="btn btn-primary flex items-center gap-2">
                <Save className="w-4 h-4" />
                Create Path
              </button>
              <button
                type="button"
                onClick={() => setShowNewPathForm(false)}
                className="btn btn-ghost"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Career sections */}
      {careers.map((career) => {
        const careerPaths = paths.filter((p) => p.career_id === career.career_id);
        if (careerPaths.length === 0) return null;

        return (
          <div key={career.career_id} className="space-y-4">
            <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary-500" />
              {career.name}
              <span className="text-dark-500 font-normal text-sm">
                ({careerPaths.length} paths)
              </span>
            </h2>

            <div className="space-y-3">
              {careerPaths.map((path) => (
                <div key={path.path_template_id} className="card">
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => handleExpandPath(path.path_template_id)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-primary-400" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-dark-100">{path.name}</h3>
                        <div className="flex items-center gap-3 text-dark-500 text-sm">
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {path.duration_hours} hours
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Edit functionality would go here
                        }}
                        className="p-2 text-dark-500 hover:text-dark-100 hover:bg-dark-800 rounded-lg transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      {expandedPathId === path.path_template_id ? (
                        <ChevronUp className="w-5 h-5 text-dark-500" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-dark-500" />
                      )}
                    </div>
                  </div>

                  {/* Expanded path details */}
                  {expandedPathId === path.path_template_id && selectedPath && (
                    <div className="mt-6 pt-6 border-t border-dark-800">
                      <p className="text-dark-400 mb-4">{selectedPath.description}</p>

                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-medium text-dark-400 uppercase tracking-wider">
                          Steps ({selectedPath.steps.length})
                        </h4>
                        <button className="btn btn-secondary btn-sm flex items-center gap-2">
                          <Plus className="w-4 h-4" />
                          Add Step
                        </button>
                      </div>

                      {selectedPath.steps.length === 0 ? (
                        <p className="text-dark-500 text-center py-8">
                          No steps defined yet. Add steps to complete this path template.
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {selectedPath.steps.map((step, index) => (
                            <div
                              key={step.step_id}
                              className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg"
                            >
                              <div className="flex items-center gap-4">
                                <span className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center text-dark-300 text-sm font-medium">
                                  {index + 1}
                                </span>
                                <div>
                                  <p className="font-medium text-dark-100">{step.name}</p>
                                  {step.duration_hours && (
                                    <p className="text-dark-500 text-sm">
                                      {step.duration_hours} hours
                                    </p>
                                  )}
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <button className="p-2 text-dark-500 hover:text-dark-100 hover:bg-dark-700 rounded-lg transition-colors">
                                  <Edit2 className="w-4 h-4" />
                                </button>
                                <button className="p-2 text-dark-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {paths.length === 0 && (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-dark-500" />
          </div>
          <h3 className="text-lg font-medium text-dark-100 mb-2">No paths created yet</h3>
          <p className="text-dark-500 mb-6">
            Create your first learning path template to get started.
          </p>
          <button
            onClick={() => setShowNewPathForm(true)}
            className="btn btn-primary inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Path
          </button>
        </div>
      )}
    </div>
  );
}
