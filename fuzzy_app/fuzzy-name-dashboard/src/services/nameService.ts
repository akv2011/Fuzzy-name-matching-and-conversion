// src/services/nameService.ts
import api from './api';
import { ProcessedName, SearchResult } from '../types';

export const nameService = {
  processName: async (name: string): Promise<ProcessedName> => {
    const response = await api.post('/process-name', { name });
    return response.data;
  },

  searchNames: async (name: string): Promise<SearchResult[]> => {
    const response = await api.get(`/search-names?query=${encodeURIComponent(name)}`);
    return response.data;
  }
};
