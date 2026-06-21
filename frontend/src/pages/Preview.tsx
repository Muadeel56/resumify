import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ResumePreview from '../components/ResumePreview';
import type { Resume } from '../types';
import { getApiErrorMessage, getResume } from '../utils/api';

const Preview = () => {
  const { id } = useParams<{ id: string }>();
  const resumeId = Number(id);

  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id || Number.isNaN(resumeId)) {
      setError('Invalid resume ID.');
      setLoading(false);
      return;
    }

    const loadResume = async () => {
      setLoading(true);
      setError('');
      try {
        const saved = await getResume(resumeId);
        setResume(saved.data);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load resume.'));
      } finally {
        setLoading(false);
      }
    };

    loadResume();
  }, [id, resumeId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading preview...</p>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Resume not found.'}</p>
          <Link to="/builder" className="text-blue-600 hover:text-blue-700">
            Back to Builder
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Resume Preview</h1>
          <div className="flex gap-3">
            <Link
              to={`/builder/${id}`}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100"
            >
              Edit
            </Link>
          </div>
        </div>
        <ResumePreview resume={resume} />
      </div>
    </div>
  );
};

export default Preview;
