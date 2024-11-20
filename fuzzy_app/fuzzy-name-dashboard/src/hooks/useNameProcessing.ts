// src/hooks/useNameProcessing.ts
import { useState } from 'react';
import { nameService } from '../services/nameService';
import { ProcessedName, SearchResult } from '../types';

export const useNameProcessing = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processedName, setProcessedName] = useState<ProcessedName | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  const processName = async (name: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const processed = await nameService.processName(name);
      setProcessedName(processed);
      
      const results = await nameService.searchNames(name);
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    processedName,
    searchResults,
    processName
  };
};

