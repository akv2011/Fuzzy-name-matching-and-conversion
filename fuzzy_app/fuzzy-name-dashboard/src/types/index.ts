// src/types/index.ts
export interface ProcessedName {
  normalized: string;
  devanagari: string;
  roman: string;
  phonetic: string;
}

export interface SearchResult {
  name: string;
  roman: string;
  similarity: number;
}

