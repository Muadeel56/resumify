export function downloadResumePdf(): void {
  const element = document.getElementById('resume-preview-print');
  if (!element) {
    throw new Error('Resume preview not found. Please update your resume first.');
  }
  window.print();
}
