import { useParams } from 'react-router-dom';
import ResumePreview from '../components/ResumePreview';
import type { Resume } from '../types';

const Preview = () => {
  const { id } = useParams<{ id: string }>();
  // TODO: Fetch resume data from API
  const resume: Resume = {
    fullName: 'John Doe',
    profileSummary: 'Sample resume preview',
    experience: [],
    education: [],
    skills: [],
    languages: [],
    certifications: [],
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Resume Preview</h1>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Download PDF
          </button>
        </div>
        <ResumePreview resume={resume} />
      </div>
    </div>
  );
};

export default Preview;

