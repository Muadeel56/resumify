import React from 'react';
import type { Resume } from '../types';
import InputField from './InputField';

interface ResumeFormProps {
  resume: Resume;
  onChange: (resume: Resume) => void;
}

const ResumeForm: React.FC<ResumeFormProps> = ({ resume, onChange }) => {
  const handleChange = (field: keyof Resume, value: any) => {
    onChange({ ...resume, [field]: value });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Resume Information</h2>
      
      <InputField
        label="Full Name"
        name="fullName"
        value={resume.fullName}
        onChange={(e) => handleChange('fullName', e.target.value)}
        placeholder="John Doe"
        required
      />

      <InputField
        label="Profile Summary"
        name="profileSummary"
        value={resume.profileSummary}
        onChange={(e) => handleChange('profileSummary', e.target.value)}
        placeholder="Brief summary about yourself..."
        textarea
      />

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Experience</h3>
        <p className="text-gray-500 text-sm">Experience section - to be implemented</p>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Education</h3>
        <p className="text-gray-500 text-sm">Education section - to be implemented</p>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Skills</h3>
        <p className="text-gray-500 text-sm">Skills section - to be implemented</p>
      </div>
    </div>
  );
};

export default ResumeForm;

