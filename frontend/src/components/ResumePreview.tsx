import React from 'react';
import type {
  Certification,
  Contact,
  Education,
  Experience,
  Language,
  Resume,
} from '../types';

interface ResumePreviewProps {
  resume: Resume;
  previewId?: string;
}

function formatDateRange(start: string, end: string): string {
  const startTrimmed = start?.trim();
  const endTrimmed = end?.trim();
  if (startTrimmed && endTrimmed) return `${startTrimmed} – ${endTrimmed}`;
  return startTrimmed || endTrimmed || '';
}

function renderDescription(description: string) {
  const lines = description
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) return null;

  if (lines.length === 1) {
    return <p className="text-gray-700 text-sm mt-1 leading-relaxed">{lines[0]}</p>;
  }

  return (
    <ul className="mt-2 space-y-1 list-disc list-outside ml-4 text-sm text-gray-700 leading-relaxed">
      {lines.map((line, index) => {
        const bullet = line.replace(/^[-•*]\s*/, '');
        return <li key={index}>{bullet}</li>;
      })}
    </ul>
  );
}

function ExperienceItem({ item }: { item: Experience }) {
  const dates = formatDateRange(item.startDate, item.endDate);

  return (
    <div className="mb-4 last:mb-0">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-baseline gap-1">
        <h3 className="font-semibold text-gray-900">
          {item.position}
          {item.company && (
            <span className="font-normal text-gray-700"> · {item.company}</span>
          )}
        </h3>
        {dates && <span className="text-sm text-gray-500 shrink-0">{dates}</span>}
      </div>
      {item.description && renderDescription(item.description)}
    </div>
  );
}

function EducationItem({ item }: { item: Education }) {
  const dates = formatDateRange(item.startDate, item.endDate);
  const degreeLine = [item.degree, item.field].filter(Boolean).join(' in ');

  return (
    <div className="mb-4 last:mb-0">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-baseline gap-1">
        <div>
          {degreeLine && <h3 className="font-semibold text-gray-900">{degreeLine}</h3>}
          {item.institution && (
            <p className="text-gray-700 text-sm">{item.institution}</p>
          )}
          {item.grade && <p className="text-gray-700 text-sm">GPA: {item.grade}</p>}
        </div>
        {dates && <span className="text-sm text-gray-500 shrink-0">{dates}</span>}
      </div>
    </div>
  );
}

function CertificationItem({ item }: { item: Certification }) {
  return (
    <div className="mb-3 last:mb-0 flex flex-col sm:flex-row sm:justify-between sm:items-baseline gap-1">
      <div>
        <span className="font-medium text-gray-900">{item.name}</span>
        {item.issuer && (
          <span className="text-gray-700 text-sm"> · {item.issuer}</span>
        )}
      </div>
      {item.date && <span className="text-sm text-gray-500 shrink-0">{item.date}</span>}
    </div>
  );
}

function LanguageItem({ item }: { item: Language }) {
  return (
    <span className="inline-flex items-center gap-1 mr-4 mb-2 text-sm text-gray-700">
      <span className="font-medium text-gray-900">{item.name}</span>
      {item.proficiency && (
        <span className="text-gray-500">({item.proficiency})</span>
      )}
    </span>
  );
}

function ContactBlock({ contact }: { contact: Contact }) {
  const phone = contact.phone?.trim();
  const email = contact.email?.trim();
  const location = contact.location?.trim();

  if (!phone && !email && !location) return null;

  return (
    <div className="text-sm text-gray-700">
      <div className="flex flex-wrap justify-center gap-x-2 gap-y-1">
        {location && <span className="whitespace-pre-line">{location}</span>}
        {location && (phone || email) && <span className="text-gray-400">|</span>}
        {phone && <span>{phone}</span>}
        {phone && email && <span className="text-gray-400">|</span>}
        {email && <span>{email}</span>}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6 last:mb-0">
      <h2 className="text-sm font-extrabold uppercase tracking-widest text-gray-900">
        {title === 'WorkExperience' ? 'Experience' : title}
      </h2>
      <hr className="resume-section-line my-2 border-0 border-t-2 border-gray-900" />
      {children}
    </section>
  );
}

const ResumePreview: React.FC<ResumePreviewProps> = ({ resume, previewId }) => {
  const contact = resume.contact;
  const experience = resume.experience ?? [];
  const education = resume.education ?? [];
  const skills = resume.skills ?? [];
  const languages = resume.languages ?? [];
  const certifications = resume.certifications ?? [];
  const extracurricular = resume.extracurricular ?? [];

  return (
    <div
      id={previewId}
      className="bg-white p-8 sm:p-10 rounded-lg shadow-md max-w-4xl mx-auto print:shadow-none print:p-0"
    >
      <header className="text-center mb-6">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-wide text-gray-900">
          {resume.fullName || 'Your Name'}
        </h1>
        {contact && (
          <div className="mt-2">
            <ContactBlock contact={contact} />
          </div>
        )}
        <hr className="resume-section-line mt-4 border-0 border-t-2 border-gray-900" />
      </header>

      {resume.profileSummary && (
        <Section title="Professional Summary">
          <p className="text-gray-800 leading-relaxed text-sm sm:text-base">
            {resume.profileSummary}
          </p>
        </Section>
      )}

      {education.length > 0 && (
        <Section title="Education">
          {education.map((item, index) => (
            <EducationItem key={item.id ?? index} item={item} />
          ))}
        </Section>
      )}

      {experience.length > 0 && (
        <Section title="WorkExperience">
          {experience.map((item, index) => (
            <ExperienceItem key={item.id ?? index} item={item} />
          ))}
        </Section>
      )}

      {skills.length > 0 && (
        <Section title="Skills">
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-800">
            {skills.map((skill, index) => (
              <span key={index} className="whitespace-nowrap">
                {skill}
              </span>
            ))}
          </div>
        </Section>
      )}

      {certifications.length > 0 && (
        <Section title="Certifications">
          {certifications.map((item, index) => (
            <CertificationItem key={item.id ?? index} item={item} />
          ))}
        </Section>
      )}

      {languages.length > 0 && (
        <Section title="Languages">
          <div className="flex flex-wrap">
            {languages.map((item, index) => (
              <LanguageItem key={item.id ?? index} item={item} />
            ))}
          </div>
        </Section>
      )}

      {extracurricular.length > 0 && (
        <Section title="Extracurricular">
          <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-gray-800">
            {extracurricular.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
};

export default ResumePreview;
