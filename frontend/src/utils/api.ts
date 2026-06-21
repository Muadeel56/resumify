import axios from 'axios';
import type { Resume } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface BackendResume {
  id: number;
  user: number;
  title: string;
  data: Resume;
  created_at: string;
  updated_at: string;
}

export interface AIUpdateResult {
  updated_resume: Resume;
  changes_made: string[];
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
}

export function getStoredUsername(): string | null {
  return localStorage.getItem('username');
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}

export async function login(username: string, password: string): Promise<void> {
  const response = await api.post<TokenPair>('/token/', { username, password });
  setTokens(response.data.access, response.data.refresh);
  localStorage.setItem('username', username);
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<void> {
  await api.post('/register/', { username, email, password });
}

export async function createResume(title: string, data: Resume): Promise<BackendResume> {
  const response = await api.post<BackendResume>('/resumes/', { title, data });
  return response.data;
}

export async function getResume(id: number): Promise<BackendResume> {
  const response = await api.get<BackendResume>(`/resumes/${id}/`);
  return response.data;
}

export async function updateResume(
  id: number,
  title: string,
  data: Resume
): Promise<BackendResume> {
  const response = await api.patch<BackendResume>(`/resumes/${id}/`, { title, data });
  return response.data;
}

export async function updateResumeWithAI(
  file: File,
  instructions: string
): Promise<AIUpdateResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('instructions', instructions);

  const response = await api.post<AIUpdateResult>('/ai-updater/update/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (data && typeof data === 'object') {
      if ('error' in data && typeof data.error === 'string') return data.error;
      if ('detail' in data && typeof data.detail === 'string') return data.detail;
    }
  }
  return fallback;
}

export default api;
