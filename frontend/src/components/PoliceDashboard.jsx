import React, { useState } from "react";
import { searchName, suggestName } from "../services/api";
import { Card, CardHeader } from "./ui/Card";
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";
import VoiceSearchButton from "./ui/VoiceSearchButton"; // Import the Voice Search Button
import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import ViewDetailsModal from "./ui/ViewDetailsModal"; // Import the modal component

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
  const [nameSuggestions, setNameSuggestions] = useState([]);
  const [isSuggestionsLoading, setIsSuggestionsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal visibility
  const [selectedRecord, setSelectedRecord] = useState(null); // State to store selected record

  const RESULTS_PER_PAGE = 5;

  const filterOptions = {
    timeframes: ["1 Month", "3 Months", "1 Year", "5 Years"],
    locations: ["All Stations", "Indore", "Bhopal", "Gwalior", "Sagar", "Dewas", "Ujjain", "Jabalpur", "Rewa"],
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
      const filteredResults = results.filter((record) => {
        const matchesLocation =
          activeFilters.location === "All Stations" ||
          record.location.includes(activeFilters.location);
        const matchesCaseType =
          activeFilters.caseType === "All Types" ||
          record.caseType === activeFilters.caseType;

        return matchesLocation && matchesCaseType;
      });

      setSearchResults(filteredResults);
      setCurrentPage(1);
    } catch (error) {
      console.error("Search Error:", error.message);
      alert("Failed to fetch search results. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = async (e) => {
    const query = e.target.value;
    setInputName(query);

    if (query.length > 2) {
      setIsSuggestionsLoading(true);
      try {
        const suggestions = await suggestName(query);
        setNameSuggestions(suggestions);
      } catch (error) {
        console.error("Error fetching suggestions:", error);
      } finally {
        setIsSuggestionsLoading(false);
      }
    } else {
      setNameSuggestions([]);
    }
  };

  const handleVoiceInput = async (transcript) => {
    setInputName(transcript); // Update input field with transcribed text
    try {
      setIsLoading(true);
      const results = await searchName(transcript); // Fetch results based on voice input
      setSearchResults(results);
    } catch (error) {
      console.error("Voice Search Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputName(suggestion);
    setNameSuggestions([]);
  };

  const handleViewDetails = (record) => {
    setSelectedRecord(record);
    setIsModalOpen(true); // Open the modal when "View" is clicked
  };

  const closeModal = () => {
    setIsModalOpen(false); // Close the modal
    setSelectedRecord(null); // Clear the selected record
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
                onChange={handleInputChange}
                className="flex-1 text-lg"
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />
              <Button
                onClick={handleSearch}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6"
                disabled={isLoading}
              >
                {isLoading ? "Searching..." : "Search"}
              </Button>
              <VoiceSearchButton onVoiceInput={handleVoiceInput} /> {/* Add Voice Search Button */}
            </div>

            {/* Suggestions List */}
            {inputName && (
              <ul className="bg-white shadow-lg mt-2 rounded-lg max-h-48 overflow-y-auto">
                {isSuggestionsLoading ? (
                  <li className="p-2 text-gray-500">Loading...</li>
                ) : (
                  nameSuggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-2 hover:bg-indigo-50 cursor-pointer"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </li>
                  ))
                )}
              </ul>
            )}
          </CardHeader>
        </Card>

        {/* Results */}
        {searchResults.length > 0 && (
          <div className="mt-6 w-full space-y-4">
            <div className="overflow-x-auto rounded-lg border border-indigo-200">
              <table className="min-w-full table-auto">
                <thead className="bg-indigo-50 text-indigo-700">
                  <tr>
                    <th className="px-4 py-2 text-left">Name</th>
                    <th className="px-4 py-2 text-left">Age</th>
                    <th className="px-4 py-2 text-left">Case Type</th>
                    <th className="px-4 py-2 text-left">Location</th>
                    <th className="px-4 py-2 text-left">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedResults.map((record, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2">{record.name}</td>
                      <td className="px-4 py-2">{record.age}</td>
                      <td className="px-4 py-2">{record.caseType}</td>
                      <td className="px-4 py-2">{record.location}</td>
                      <td className="px-4 py-2">
                        <Button
                          onClick={() => handleViewDetails(record)}
                          className="bg-indigo-600 hover:bg-indigo-700 text-white"
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-between items-center">
              <Button
                className="px-4 py-2"
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span className="text-lg">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                className="px-4 py-2"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}

        {/* Modal */}
        {isModalOpen && (
          <ViewDetailsModal
            isOpen={isModalOpen}
            onClose={closeModal}
            record={selectedRecord}
          />
        )}
      </div>
    </div>
  );
};

export default PoliceDashboard;
  