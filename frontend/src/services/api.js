import axios from "axios";

const BASE_URL = "http://localhost:5000";

// Function to search for a name and handle API request
export const searchName = async (name) => {
  try {
    // Making the POST request to the Flask backend with the search term
    const response = await axios.post(`${BASE_URL}/search`, { name });

    // Debugging: Log the full response to inspect it
    console.log("Full API Response:", response);

    // Check if response has data and results, then return them
    return response.data.results || []; // Ensure results is an array
  } catch (error) {
    // Detailed error handling
    if (error.response) {
      // If the error comes from the response, log detailed info
      console.error("API Response Error:", error.response);
      console.error("Error Data:", error.response.data);
      console.error("Error Status:", error.response.status);
      console.error("Error Headers:", error.response.headers);
    } else if (error.request) {
      // If the error is related to the request not receiving a response
      console.error("API Request Error:", error.request);
    } else {
      // For other types of errors
      console.error("Error:", error.message);
    }

    // Throw a more descriptive error to the calling function
    throw new Error(error.response?.data?.message || "An error occurred while fetching data.");
  }
};
export const suggestName = async (name) => {
  try {
    // Making the GET request to the Flask backend for name suggestions
    const response = await axios.get(`${BASE_URL}/suggest`, {
      params: { name },  // Pass name as query parameter
    });

    // Debugging: Log the full response to inspect it
    console.log("Suggestion API Response:", response);

    // Check if response contains suggestions, and return only the 'name' property from each suggestion
    if (response.data.suggestions && Array.isArray(response.data.suggestions)) {
      return response.data.suggestions.map(item => item.name); // Return just the name
    }

    // If no suggestions are found, return an empty array
    return [];
  } catch (error) {
    // Detailed error handling
    if (error.response) {
      console.error("API Response Error:", error.response);
      console.error("Error Data:", error.response.data);
      console.error("Error Status:", error.response.status);
      console.error("Error Headers:", error.response.headers);
    } else if (error.request) {
      console.error("API Request Error:", error.request);
    } else {
      console.error("Error:", error.message);
    }

    // Throw a more descriptive error to the calling function
    throw new Error(error.response?.data?.message || "An error occurred while fetching suggestions.");
  }
};



/*
import axios from "axios";

const BASE_URL = "http://localhost:5000";

// Function to search for a name and handle API request
export const searchName = async (name) => {
  try {
    // Making the POST request to the Flask backend with the search term
    const response = await axios.post(`${BASE_URL}/search`, { name });

    // Debugging: Log the full response to inspect it
    console.log("Full API Response:", response);

    // Check if response has data and results, then return them
    return response.data.results || []; // Ensure results is an array
  } catch (error) {
    // Detailed error handling
    if (error.response) {
      // If the error comes from the response, log detailed info
      console.error("API Response Error:", error.response);
      console.error("Error Data:", error.response.data);
      console.error("Error Status:", error.response.status);
      console.error("Error Headers:", error.response.headers);
    } else if (error.request) {
      // If the error is related to the request not receiving a response
      console.error("API Request Error:", error.request);
    } else {
      // For other types of errors
      console.error("Error:", error.message);
    }

    // Throw a more descriptive error to the calling function
    throw new Error(error.response?.data?.message || "An error occurred while fetching data.");
  }
};
*/