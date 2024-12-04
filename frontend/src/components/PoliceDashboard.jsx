import React, { useState } from "react";
import { searchName } from "../services/api";
import { Card, CardHeader, CardContent } from "./ui/Card";
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";
import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Database,
} from "lucide-react";

const PoliceDashboard = () => {
  const [inputName, setInputName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeFilters, setActiveFilters] = useState({
    timeframe: "1 Year",
    location: "All Stations",
    caseType: "All Types",
  });
  const [showFilters, setShowFilters] = useState(false);

  const RESULTS_PER_PAGE = 5;

  const filterOptions = {
    timeframes: ["1 Month", "3 Months", "1 Year", "5 Years"],
    locations: ["All Stations", "Delhi", "Mumbai", "Bangalore", "Kolkata"],
    caseTypes: ["All Types", "Criminal", "Witness", "Suspect", "Victim"],
  };

  const handleSearch = async () => {
    if (!inputName.trim()) {
      alert("Please enter a name to search.");
      return;
    }

    setIsLoading(true);

    try {
      const results = await searchName(inputName);
      console.log("API Results:", results); // Debugging log

      const filteredResults = results.filter((record) => {
        const matchesLocation =
          activeFilters.location === "All Stations" ||
          record.location.includes(activeFilters.location);
        const matchesCaseType =
          activeFilters.caseType === "All Types" ||
          record.caseType === activeFilters.caseType;

        return matchesLocation && matchesCaseType;
      });

      console.log("Filtered Results:", filteredResults); // Debugging log
      setSearchResults(filteredResults);
      setCurrentPage(1);
    } catch (error) {
      console.error("Search Error:", error.message);
      alert("Failed to fetch search results. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleFilter = (filterType, value) => {
    setActiveFilters((prevFilters) => ({
      ...prevFilters,
      [filterType]: value,
    }));
  };

  const resetFilters = () => {
    setActiveFilters({
      timeframe: "1 Year",
      location: "All Stations",
      caseType: "All Types",
    });
  };

  const paginatedResults = searchResults.slice(
    (currentPage - 1) * RESULTS_PER_PAGE,
    currentPage * RESULTS_PER_PAGE
  );

  const totalPages = Math.ceil(searchResults.length / RESULTS_PER_PAGE) || 1;

  return (
    <div className="min-h-screen w-full flex flex-col items-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="w-full max-w-7xl px-4 py-8">
        {/* Header */}
        <header className="text-center bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 rounded-xl shadow-lg mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            Integrated Name Matching System
          </h1>
          <p className="text-indigo-200 mt-2">
            Enhanced Fuzzy Search & Cross-Referencing
          </p>
        </header>

        {/* Search Section */}
        <Card className="w-full shadow-xl border border-indigo-100">
          <CardHeader className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-indigo-900">
                Name Search & Cross-Referencing
              </h2>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center hover:bg-indigo-50"
              >
                <Filter className="mr-2 h-4 w-4" />
                Filters
                {showFilters ? (
                  <ChevronUp className="ml-2 h-4 w-4" />
                ) : (
                  <ChevronDown className="ml-2 h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="flex gap-3 w-full">
              <Input
                placeholder="Enter name to search..."
                value={inputName}
                onChange={(e) => setInputName(e.target.value)}
                className="flex-1 text-lg"
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />
              <Button
                onClick={handleSearch}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-5 w-5 border-2 border-t-transparent border-white rounded-full"></div>
                    Searching...
                  </div>
                ) : (
                  "Search"
                )}
              </Button>
            </div>
          </CardHeader>

          {/* Filters */}
          {showFilters && (
            <CardContent className="border-t border-indigo-100">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4">
                {Object.entries(filterOptions).map(([filterType, options]) => (
                  <div key={filterType} className="space-y-3">
                    <label className="block text-sm font-semibold text-indigo-900 uppercase tracking-wide">
                      {filterType}
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {options.map((option) => (
                        <Button
                          key={option}
                          variant={
                            activeFilters[filterType] === option
                              ? "default"
                              : "outline"
                          }
                          size="sm"
                          className={`w-full ${
                            activeFilters[filterType] === option
                              ? "bg-indigo-600"
                              : "hover:bg-indigo-50"
                          }`}
                          onClick={() => toggleFilter(filterType, option)}
                        >
                          {option}
                        </Button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <Button
                onClick={resetFilters}
                className="bg-red-500 text-white mt-4 hover:bg-red-600"
              >
                Reset Filters
              </Button>
            </CardContent>
          )}
        </Card>

        {/* Results */}
        {searchResults.length > 0 ? (
          <Card className="w-full mt-8 shadow-xl border border-indigo-100">
            <CardHeader className="flex items-center border-b border-indigo-100 bg-indigo-50/50">
              <Database className="mr-3 text-indigo-600" />
              <span className="text-xl font-semibold text-indigo-900">
                Matching Records ({searchResults.length})
              </span>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-indigo-50/50">
                      <th className="p-4 text-left text-indigo-900 font-semibold">
                        Name
                      </th>
                      <th className="p-4 text-left text-indigo-900 font-semibold">
                        Case Type
                      </th>
                      <th className="p-4 text-left text-indigo-900 font-semibold">
                        FIR
                      </th>
                      <th className="p-4 text-left text-indigo-900 font-semibold">
                        Location
                      </th>
                      <th className="p-4 text-left text-indigo-900 font-semibold">
                        Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedResults.map((result, index) => (
                      <tr
                        key={index}
                        className="border-b border-indigo-100 hover:bg-indigo-50/30 transition-colors"
                      >
                        <td className="p-4">
                          <div className="font-semibold text-indigo-900">
                            {result.name}
                          </div>
                          <div className="text-sm text-indigo-600">
                            Age: {result.age}
                          </div>
                        </td>
                        <td className="p-4">{result.case_type}</td>
                        <td className="p-4">{result.fir}</td>
                        <td className="p-4">{result.location}</td>
                        <td className="p-4">{result.confidence}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="w-full mt-8 flex flex-col justify-center items-center">
            <AlertTriangle className="h-12 w-12 text-indigo-600" />
            <span className="ml-4 text-lg font-semibold text-indigo-900 text-center">
              {isLoading
                ? "Loading..."
                : inputName
                ? "No results found. Try refining your filters or using a different name."
                : "Please enter a name to begin your search."}
            </span>
          </div>
        )}

        {/* Pagination */}
        <div className="flex justify-center items-center mt-4">
          <Button
            disabled={currentPage === 1 || paginatedResults.length === 0}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </Button>
          <span className="mx-4 text-indigo-800">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            disabled={
              currentPage === totalPages || paginatedResults.length === 0
            }
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PoliceDashboard;
