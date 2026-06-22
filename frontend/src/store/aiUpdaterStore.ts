import { create } from 'zustand';
import type { Resume } from '../types';

type Status = 'idle' | 'processing' | 'done' | 'error';

interface AIUpdaterState {
  status: Status;
  uploadedFile: File | null;
  supportingFile: File | null;
  instructions: string;
  updatedResume: Resume | null;
  changesMade: string[];
  error: string | null;

  setFile: (file: File | null) => void;
  setSupportingFile: (file: File | null) => void;
  setInstructions: (text: string) => void;
  setProcessing: () => void;
  setResult: (resume: Resume, changes: string[]) => void;
  setError: (message: string) => void;
  reset: () => void;
}

export const useAIUpdaterStore = create<AIUpdaterState>((set) => ({
  status: 'idle',
  uploadedFile: null,
  supportingFile: null,
  instructions: '',
  updatedResume: null,
  changesMade: [],
  error: null,

  setFile: (file) => set({ uploadedFile: file, status: 'idle', error: null }),
  setSupportingFile: (file) => set({ supportingFile: file, status: 'idle', error: null }),
  setInstructions: (text) => set({ instructions: text, error: null }),
  setProcessing: () => set({ status: 'processing', error: null }),
  setResult: (resume, changes) =>
    set({ status: 'done', updatedResume: resume, changesMade: changes }),
  setError: (message) =>
    set((state) => ({
      error: message || null,
      ...(state.status !== 'done' && message ? { status: 'error' as const } : {}),
    })),
  reset: () =>
    set({
      status: 'idle',
      uploadedFile: null,
      supportingFile: null,
      instructions: '',
      updatedResume: null,
      changesMade: [],
      error: null,
    }),
}));
