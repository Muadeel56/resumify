import { create } from 'zustand';
import {
  clearTokens,
  getStoredUsername,
  isAuthenticated,
  login as apiLogin,
  register as apiRegister,
} from '../utils/api';

interface AuthState {
  username: string | null;
  isAuthenticated: boolean;
  initialize: () => void;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  username: null,
  isAuthenticated: false,

  initialize: () => {
    set({
      isAuthenticated: isAuthenticated(),
      username: getStoredUsername(),
    });
  },

  login: async (username, password) => {
    await apiLogin(username, password);
    set({ isAuthenticated: true, username });
  },

  register: async (username, email, password) => {
    await apiRegister(username, email, password);
  },

  logout: () => {
    clearTokens();
    set({ isAuthenticated: false, username: null });
  },
}));
