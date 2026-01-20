import { useEffect, useState } from 'react';
import { careersApi, pathsApi } from '../services/api';
import type { Career, PathTemplate } from '../types';
import { Clock, BookOpen, ChevronRight, Filter } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function LearningPathsPage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [paths, setPaths] = useState<PathTemplate[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
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

    fetchData();
  }, []);

  const filteredPaths = selectedCareer
    ? paths.filter((p) => p.career_id === selectedCareer)
    : paths;

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
        <h1 className="text-3xl font-bold text-dark-100">Learning Paths</h1>
        <p className="mt-2 text-dark-400">
          Explore available learning paths and courses for your career development.
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-dark-400">
          <Filter className="w-4 h-4" />
          <span className="text-sm font-medium">Filter by career:</span>
        </div>
        <button
          onClick={() => setSelectedCareer(null)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selectedCareer === null
              ? 'bg-primary-600 text-white'
              : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
          }`}
        >
          All Paths
        </button>
        {careers.map((career) => (
          <button
            key={career.career_id}
            onClick={() => setSelectedCareer(career.career_id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCareer === career.career_id
                ? 'bg-primary-600 text-white'
                : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
            }`}
          >
            {career.name}
          </button>
        ))}
      </div>

      {/* Paths grid */}
      {filteredPaths.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📚</span>
          </div>
          <h3 className="text-lg font-medium text-dark-100 mb-2">No paths found</h3>
          <p className="text-dark-500">
            {selectedCareer
              ? 'No learning paths available for this career yet.'
              : 'No learning paths available.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPaths.map((path) => {
            const career = careers.find((c) => c.career_id === path.career_id);
            return (
              <div
                key={path.path_template_id}
                className="card card-hover group cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600/30 to-secondary-600/30 flex items-center justify-center">
                    <BookOpen className="w-6 h-6 text-primary-400" />
                  </div>
                  <span className="px-3 py-1 text-xs font-medium bg-dark-800 text-dark-300 rounded-full">
                    {career?.name || 'Unknown'}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-dark-100 mb-2 group-hover:text-primary-400 transition-colors">
                  {path.name}
                </h3>
                <p className="text-dark-400 text-sm mb-4 line-clamp-2">{path.description}</p>

                <div className="flex items-center justify-between pt-4 border-t border-dark-800">
                  <div className="flex items-center gap-2 text-dark-500">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">{path.duration_hours} hours</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-dark-500 group-hover:text-primary-400 transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
