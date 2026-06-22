import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import type { Resume } from '../types';
import ResumeForm from '../components/ResumeForm';
import ResumePreview from '../components/ResumePreview';
import TemplateSelector from '../components/TemplateSelector';
import { createResume, getApiErrorMessage, getResume, updateResume } from '../utils/api';

const emptyResume = (): Resume => ({
  fullName: '',
  profileSummary: '',
  contact: { phone: '', email: '', location: '' },
  experience: [],
  education: [],
  skills: [],
  languages: [],
  certifications: [],
  extracurricular: [],
});

const ResumeBuilder = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const resumeId = id ? Number(id) : null;

  const [resume, setResume] = useState<Resume>(emptyResume());
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [loading, setLoading] = useState(!!resumeId);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!resumeId) return;

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
  }, [resumeId]);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    const title = resume.fullName.trim() || 'Untitled Resume';

    try {
      if (resumeId) {
        await updateResume(resumeId, title, resume);
        navigate(`/preview/${resumeId}`);
      } else {
        const saved = await createResume(title, resume);
        navigate(`/preview/${saved.id}`);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save resume.'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading resume...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Resume Builder</h1>
          <div className="flex gap-3">
            {resumeId && (
              <Link
                to={`/preview/${resumeId}`}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100"
              >
                Preview
              </Link>
            )}
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
            >
              {saving ? 'Saving...' : 'Save Resume'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        <div className="mb-6">
          <TemplateSelector
            selectedTemplate={selectedTemplate}
            onSelectTemplate={setSelectedTemplate}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <ResumeForm resume={resume} onChange={setResume} />
          </div>
          <div>
            <ResumePreview resume={resume} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilder;
