
  // src/utils/helpers.ts
  export const formatSimilarityScore = (score: number): string => {
    return (score * 100).toFixed(1) + '%';
  };
  
  export const normalizeString = (str: string): string => {
    return str.toLowerCase().replace(/[^a-zA-Z\s]/g, '');
  };
  
  export const delay = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  };