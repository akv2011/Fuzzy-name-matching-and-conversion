import React, { useState } from "react";
import { searchName, suggestName } from "../services/api";
import { Card, CardHeader } from "./ui/Card";
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";
import VoiceSearchButton from "./ui/VoiceSearchButton"; // Import the Voice Search Button
import {
  Filter,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import ViewDetailsModal from "./ui/ViewDetailsModal"; // Import the modal component
import leftLogo from "/home/harisudhan/Documents/new fuzzy/fuzzy-name-matching-system/frontend/src/components/assets/mp logo.png"; // Import the left logo image
import rightLogo from "/home/harisudhan/Documents/new fuzzy/fuzzy-name-matching-system/frontend/src/components/assets/mp police logo.png"; // Import the right logo image

const PoliceDashboard = () => {
  const [inputName, setInputName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeFilters, setActiveFilters] = useState({
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
    setSelectedRecord(record); // Set the selected record
    setIsModalOpen(true); // Open the modal
  };

  const closeModal = () => {
    setIsModalOpen(false); // Close the modal
    setSelectedRecord(null); // Clear the selected record
  };

  const handleFilterChange = (type, value) => {
    setActiveFilters((prev) => ({
      ...prev,
      [type]: value,
    }));
  };

  const paginatedResults = searchResults.slice(
    (currentPage - 1) * RESULTS_PER_PAGE,
    currentPage * RESULTS_PER_PAGE
  );

  const totalPages = Math.ceil(searchResults.length / RESULTS_PER_PAGE) || 1;

  return (
    <div className="min-h-screen w-full flex flex-col items-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Banner Section */}
      <div className="relative w-full bg-gradient-to-r from-indigo-600 to-purple-600 h-36 flex items-center justify-between px-8 shadow-lg rounded-b-lg">
        <img
          src={leftLogo} // Use imported left logo image
          alt="Left Logo"
          className="h-16 w-auto"
        />
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white">MPPDS</h1>
          <p className="text-lg text-indigo-200 mt-1">
            The Integrated Fuzzy Name Matching System
          </p>
        </div>
        <img
          src={rightLogo} // Use imported right logo image
          alt="Right Logo"
          className="h-16 w-auto"
        />
      </div>

      <div className="w-full max-w-7xl px-4 py-8">
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

            {/* Filter Options */}
            {showFilters && (
              <div className="mt-4 space-y-4 bg-indigo-50 p-4 rounded-lg shadow">
                <div>
                  <label className="font-medium text-indigo-800">Location:</label>
                  <select
                    value={activeFilters.location}
                    onChange={(e) => handleFilterChange("location", e.target.value)}
                    className="ml-2 px-3 py-2 border rounded"
                  >
                    {filterOptions.locations.map((option, idx) => (
                      <option key={idx} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-medium text-indigo-800">Case Type:</label>
                  <select
                    value={activeFilters.caseType}
                    onChange={(e) => handleFilterChange("caseType", e.target.value)}
                    className="ml-2 px-3 py-2 border rounded"
                  >
                    {filterOptions.caseTypes.map((option, idx) => (
                      <option key={idx} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

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
            <div className="bg-white shadow-md p-4 rounded-lg">
              <table className="min-w-full text-left">
                <thead className="bg-indigo-100">
                  <tr>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Name</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Age</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Location</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Case Type</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Confidence Score</th>
                    <th className="px-4 py-2 text-sm font-semibold text-gray-800">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedResults.map((record, idx) => (
                    <tr key={idx} className="hover:bg-indigo-50">
                      <td className="px-4 py-2">{record.name}</td>
                      <td className="px-4 py-2">{record.age}</td>
                      <td className="px-4 py-2">{record.location}</td>
                      <td className="px-4 py-2">{record.caseType}</td>
                      <td className="px-4 py-2">
                        {record.confidence !== undefined && record.confidence !== null
                          ? record.confidence.toFixed(2)
                          : "N/A"}
                      </td>
                      <td className="px-4 py-2">
                        <Button
                          onClick={() => handleViewDetails(record)}
                          className="bg-indigo-500 hover:bg-indigo-600 text-white"
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex justify-between items-center mt-4">
              <Button
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <Button
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}

        {/* Modal for Viewing Details */}
        {isModalOpen && selectedRecord && (
          <ViewDetailsModal
            isOpen={isModalOpen} // Pass isOpen prop
            record={selectedRecord}
            onClose={closeModal}
          />
        )}
      </div>
    </div>
  );
};

export default PoliceDashboard;
