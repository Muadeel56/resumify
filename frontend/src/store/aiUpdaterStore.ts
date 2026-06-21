import { create } from 'zustand';
import type { Resume } from '../types';

type Status = 'idle' | 'processing' | 'done' | 'error';

interface AIUpdaterState {
  status: Status;
  uploadedFile: File | null;
  instructions: string;
  updatedResume: Resume | null;
  changesMade: string[];
  error: string | null;

  setFile: (file: File | null) => void;
  setInstructions: (text: string) => void;
  setProcessing: () => void;
  setResult: (resume: Resume, changes: string[]) => void;
  setError: (message: string) => void;
  reset: () => void;
}

export const useAIUpdaterStore = create<AIUpdaterState>((set) => ({
  status: 'idle',
  uploadedFile: null,
  instructions: '',
  updatedResume: null,
  changesMade: [],
  error: null,

  setFile: (file) => set({ uploadedFile: file, status: 'idle', error: null }),
  setInstructions: (text) => set({ instructions: text }),
  setProcessing: () => set({ status: 'processing', error: null }),
  setResult: (resume, changes) =>
    set({ status: 'done', updatedResume: resume, changesMade: changes }),
  setError: (message) => set({ status: 'error', error: message }),
  reset: () =>
    set({
      status: 'idle',
      uploadedFile: null,
      instructions: '',
      updatedResume: null,
      changesMade: [],
      error: null,
    }),
}));
