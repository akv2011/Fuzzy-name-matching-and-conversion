// src/components/dashboard/ResultsTable.tsx
import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { SearchResult } from '@/types';

interface ResultsTableProps {
  results: SearchResult[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  return (
    <Card>
      <CardHeader>Search Results</CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="border p-2 bg-gray-50">Devanagari Name</th>
                <th className="border p-2 bg-gray-50">Roman Script</th>
                <th className="border p-2 bg-gray-50">Similarity Score</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index}>
                  <td className="border p-2">{result.name}</td>
                  <td className="border p-2">{result.roman}</td>
                  <td className="border p-2">{result.similarity.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResultsTable;