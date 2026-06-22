import { useRef, useState } from 'react';
import ResumePreview from '../components/ResumePreview';
import { useAIUpdaterStore } from '../store/aiUpdaterStore';
import { createResume, getApiErrorMessage, updateResumeWithAI } from '../utils/api';
import { downloadResumePdf } from '../utils/printResume';

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];
const ALLOWED_MIMES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file: File): string | null {
  const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
  const hasValidExtension = ALLOWED_EXTENSIONS.includes(extension);
  const hasValidMime = !file.type || ALLOWED_MIMES.includes(file.type);

  if (!hasValidExtension && !hasValidMime) {
    return 'Only PDF and DOCX files are supported.';
  }

  if (file.size > MAX_FILE_SIZE) {
    return 'File too large. Maximum size is 5MB.';
  }

  return null;
}

const AIResumeUpdater = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const supportingFileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [saving, setSaving] = useState(false);

  const {
    status,
    uploadedFile,
    supportingFile,
    instructions,
    updatedResume,
    changesMade,
    error,
    setFile,
    setSupportingFile,
    setInstructions,
    setProcessing,
    setResult,
    setError,
    reset,
  } = useAIUpdaterStore();

  const isProcessing = status === 'processing';

  const handleFileSelect = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setFile(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
    e.target.value = '';
  };

  const handleSupportingFileSelect = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setSupportingFile(file);
  };

  const handleSupportingInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleSupportingFileSelect(file);
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!isProcessing) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (isProcessing) return;

    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleSubmit = async () => {
    if (!uploadedFile) {
      setError('Please upload your resume file.');
      return;
    }

    if (!instructions.trim()) {
      setError('Please describe what changes you want.');
      return;
    }

    setProcessing();

    try {
      const data = await updateResumeWithAI(uploadedFile, instructions.trim(), supportingFile);
      setResult(data.updated_resume, data.changes_made);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Something went wrong. Please try again.'));
    }
  };

  const handleSave = async () => {
    if (!updatedResume) return;

    setSaving(true);
    try {
      await createResume(`${updatedResume.fullName} — Updated`, updatedResume);
      alert('Resume saved successfully!');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save resume.'));
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPdf = () => {
    if (!updatedResume) return;
    try {
      downloadResumePdf();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open print dialog.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-6 no-print">AI Resume Updater</h1>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg no-print">
            {error}
          </div>
        )}

        {status !== 'done' && (
          <>
            <div className="bg-white rounded-lg shadow-md p-6 mb-6 no-print">
              <h2 className="text-xl font-semibold mb-4">Step 1 — Upload Your Resume</h2>
              <div
                role="button"
                tabIndex={0}
                onClick={() => !isProcessing && fileInputRef.current?.click()}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    if (!isProcessing) fileInputRef.current?.click();
                  }
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragging
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleInputChange}
                  className="hidden"
                  disabled={isProcessing}
                />
                {uploadedFile ? (
                  <div>
                    <p className="text-gray-900 font-medium">{uploadedFile.name}</p>
                    <p className="text-gray-500 text-sm mt-1">
                      {formatFileSize(uploadedFile.size)}
                    </p>
                    <p className="text-blue-600 text-sm mt-2">Click or drag to replace</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-700">
                      Drag and drop your resume here, or click to browse
                    </p>
                    <p className="text-gray-500 text-sm mt-2">PDF or DOCX, max 5MB</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6 no-print">
              <h2 className="text-xl font-semibold mb-4">
                Step 2 — Optional Supporting Document
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Upload an internship certificate or reference to help the AI add missing experience.
              </p>

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  {supportingFile ? (
                    <>
                      <p className="text-gray-900 font-medium">{supportingFile.name}</p>
                      <p className="text-gray-500 text-sm mt-1">
                        {formatFileSize(supportingFile.size)}
                      </p>
                    </>
                  ) : (
                    <p className="text-gray-600 text-sm">No supporting file selected.</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <input
                    ref={supportingFileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleSupportingInputChange}
                    className="hidden"
                    disabled={isProcessing}
                  />
                  <button
                    type="button"
                    onClick={() => !isProcessing && supportingFileInputRef.current?.click()}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 disabled:opacity-50"
                    disabled={isProcessing}
                  >
                    {supportingFile ? 'Replace file' : 'Choose file'}
                  </button>
                  {supportingFile && (
                    <button
                      type="button"
                      onClick={() => setSupportingFile(null)}
                      className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 disabled:opacity-50"
                      disabled={isProcessing}
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mb-6 no-print">
              <h2 className="text-xl font-semibold mb-4">Step 3 — Describe Your Changes</h2>
              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                disabled={isProcessing}
                rows={5}
                placeholder="Add HSE Intern experience at D.G. Khan Cement Company Limited (Nishat Group), Khairpur Plant, based on the supporting document. Keep all existing jobs and overall layout unchanged. Place the new internship at the top of Work Experience."
                className="w-full border border-gray-300 rounded-lg p-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            <div className="no-print">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isProcessing}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Update My Resume
              </button>
            </div>

            {isProcessing && (
              <div className="mt-6 flex items-center gap-3 no-print">
                <div className="h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-600">AI is updating your resume...</p>
              </div>
            )}
          </>
        )}

        {status === 'done' && updatedResume && (
          <>
            <div className="bg-white rounded-lg shadow-md p-6 mb-6 no-print">
              <h2 className="text-xl font-semibold mb-4">Changes Applied</h2>
              {changesMade.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-gray-700">
                  {changesMade.map((change, index) => (
                    <li key={index}>{change}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No specific changes were listed.</p>
              )}
            </div>

            <div className="flex flex-wrap gap-3 mb-6 no-print">
              <button
                type="button"
                onClick={handleSave}
                disabled={saving}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save to My Resumes'}
              </button>
              <button
                type="button"
                onClick={handleDownloadPdf}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100"
              >
                Download PDF
              </button>
              <button
                type="button"
                onClick={reset}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100"
              >
                Start over
              </button>
            </div>

            <div className="mb-2 no-print">
              <h2 className="text-xl font-semibold">Updated Resume Preview</h2>
              <p className="text-sm text-gray-500 mt-1">
                Review the full resume below before saving or printing.
              </p>
            </div>

            <ResumePreview resume={updatedResume} previewId="resume-preview-print" />
          </>
        )}
      </div>
    </div>
  );
};

export default AIResumeUpdater;
