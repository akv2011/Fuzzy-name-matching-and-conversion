// src/components/dashboard/ProcessingSection.tsx
import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { ProcessedName } from '@/types';

interface ProcessingSectionProps {
  processedName: ProcessedName;
}

const ProcessingSection: React.FC<ProcessingSectionProps> = ({ processedName }) => {
  return (
    <Card className="mb-6">
      <CardHeader>Name Processing</CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>Normalized: {processedName.normalized}</div>
          <div>Devanagari: {processedName.devanagari}</div>
          <div>Roman Script: {processedName.roman}</div>
          <div>Phonetic: {processedName.phonetic}</div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcessingSection;