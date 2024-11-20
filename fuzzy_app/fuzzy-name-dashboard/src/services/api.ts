// src/services/api.ts
const API_URL = import.meta.env.VITE_API_URL;

export const api = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },
};
/*
// src/services/nameService.ts
import { api } from './api';
import { ProcessedName, SearchResult } from '@/types';

export const nameService = {
  async processName(name: string): Promise<ProcessedName> {
    return api.post<ProcessedName>('/process', { name });
  },

  async searchNames(name: string): Promise<SearchResult[]> {
    return api.post<SearchResult[]>('/search', { name });
  },
};
*/