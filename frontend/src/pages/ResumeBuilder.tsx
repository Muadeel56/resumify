import { useState } from 'react';
import type { Resume } from '../types';
import ResumeForm from '../components/ResumeForm';
import ResumePreview from '../components/ResumePreview';
import TemplateSelector from '../components/TemplateSelector';

const ResumeBuilder = () => {
  const [resume, setResume] = useState<Resume>({
    fullName: '',
    profileSummary: '',
    experience: [],
    education: [],
    skills: [],
    languages: [],
    certifications: [],
  });

  const [selectedTemplate, setSelectedTemplate] = useState('modern');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Resume Builder</h1>
        
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

