import React from 'react';
import type { Resume } from '../types';

interface ResumePreviewProps {
  resume: Resume;
}

const ResumePreview: React.FC<ResumePreviewProps> = ({ resume }) => {
  return (
    <div className="bg-white p-8 rounded-lg shadow-md max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">{resume.fullName || 'Your Name'}</h1>
        {resume.profileSummary && (
          <p className="text-gray-700">{resume.profileSummary}</p>
        )}
      </div>

      {resume.experience && resume.experience.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">Experience</h2>
          <p className="text-gray-500 text-sm">Experience items - to be implemented</p>
        </div>
      )}

      {resume.education && resume.education.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">Education</h2>
          <p className="text-gray-500 text-sm">Education items - to be implemented</p>
        </div>
      )}

      {resume.skills && resume.skills.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">Skills</h2>
          <p className="text-gray-500 text-sm">Skills list - to be implemented</p>
        </div>
      )}
    </div>
  );
};

export default ResumePreview;

