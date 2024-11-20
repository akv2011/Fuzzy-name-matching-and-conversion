
// src/components/dashboard/SearchSection.tsx
import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface SearchSectionProps {
  inputName: string;
  setInputName: (name: string) => void;
  onSearch: () => void;
}

const SearchSection: React.FC<SearchSectionProps> = ({ 
  inputName, 
  setInputName, 
  onSearch 
}) => {
  return (
    <Card className="mb-6">
      <CardHeader>Input Name</CardHeader>
      <CardContent>
        <div className="flex gap-4">
          <Input
            placeholder="Enter name to search"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            className="flex-1"
          />
          <Button onClick={onSearch}>Process & Search</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchSection;
