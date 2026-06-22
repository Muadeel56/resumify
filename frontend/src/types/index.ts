export type Resume = {
  id?: number;
  fullName: string;
  profileSummary: string;
  contact: Contact;
  experience: Experience[];
  education: Education[];
  skills: string[];
  languages: Language[];
  certifications: Certification[];
  extracurricular: string[];
};

export type Contact = {
  phone: string;
  email: string;
  location: string;
};

export type Experience = {
  id?: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  description: string;
};

export type Education = {
  id?: string;
  institution: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string;
  grade?: string;
};

export type Language = {
  id?: string;
  name: string;
  proficiency: string;
};

export type Certification = {
  id?: string;
  name: string;
  issuer: string;
  date: string;
};
