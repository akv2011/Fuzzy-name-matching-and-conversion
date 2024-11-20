// src/components/dashboard/Dashboard.tsx
import React from 'react';
import SearchSection from './SearchSection';
import ProcessingSection from './ProcessingSection';
import ResultsTable from './ResultsTable';
import useNameProcessing from '@/hooks/useNameProcessing';

const Dashboard = () => {
  const {
    inputName,
    setInputName,
    processedName,
    searchResults,
    handleSearch,
  } = useNameProcessing();

  return (
    <div className="max-w-7xl mx-auto p-4">
      <header className="flex items-center mb-6">
        <svg className="w-12 h-12 mr-4" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="#4a90e2" />
          <text x="50" y="50" className="text-white text-4xl" textAnchor="middle" dominantBaseline="central">
            FNC
          </text>
        </svg>
        <h1 className="text-2xl text-gray-800">Fuzzy Name Conversion Dashboard</h1>
      </header>
      
      <SearchSection 
        inputName={inputName}
        setInputName={setInputName}
        onSearch={handleSearch}
      />
      
      <ProcessingSection processedName={processedName} />
      
      <ResultsTable results={searchResults} />
    </div>
  );
};

export default Dashboard;



