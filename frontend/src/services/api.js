import axios from "axios";

const BASE_URL = "http://localhost:5000";

// Function to search for a name and handle API request
export const searchName = async (name) => {
  try {
    const response = await axios.post(`${BASE_URL}/search`, { name });
    console.log("Full API Response:", response);
    return response.data.results || [];
  } catch (error) {
    handleApiError(error, "fetching data");
  }
};

// Function to suggest names
export const suggestName = async (name) => {
  try {
    const response = await axios.get(`${BASE_URL}/suggest`, {
      params: { name },
    });
    console.log("Suggestion API Response:", response);
    if (response.data.suggestions && Array.isArray(response.data.suggestions)) {
      return response.data.suggestions.map((item) => item.name);
    }
    return [];
  } catch (error) {
    handleApiError(error, "fetching suggestions");
  }
};

// Function to add no match data to the backend
export const addNoMatchData = async (data) => {
  try {
    const response = await axios.post(`${BASE_URL}/add-no-match`, data);
    console.log("Add No Match Data API Response:", response);
    return response.data; // Return the response data to confirm successful submission
  } catch (error) {
    handleApiError(error, "adding no match data");
  }
};

// Function to add a new record
export const addNewRecord = async (data) => {
  try {
    const response = await axios.post(`${BASE_URL}/add-record`, data);
    console.log("Add Record API Response:", response);
    return response.data;
  } catch (error) {
    handleApiError(error, "adding a new record");
  }
};

// Utility function to handle API errors
const handleApiError = (error, action) => {
  if (error.response) {
    console.error(`API Response Error while ${action}:`, error.response);
    console.error("Error Data:", error.response.data);
    console.error("Error Status:", error.response.status);
    console.error("Error Headers:", error.response.headers);
  } else if (error.request) {
    console.error(`API Request Error while ${action}:`, error.request);
  } else {
    console.error(`Error while ${action}:`, error.message);
  }
  throw new Error(error.response?.data?.message || `An error occurred while ${action}.`);
};




/*
import axios from "axios";

const BASE_URL = "http://localhost:5000";

// Function to search for a name and handle API request
export const searchName = async (name) => {
  try {
    const response = await axios.post(`${BASE_URL}/search`, { name });
    console.log("Full API Response:", response);
    return response.data.results || [];
  } catch (error) {
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
    throw new Error(error.response?.data?.message || "An error occurred while fetching data.");
  }
};

export const suggestName = async (name) => {
  try {
    const response = await axios.get(`${BASE_URL}/suggest`, {
      params: { name },
    });
    console.log("Suggestion API Response:", response);
    if (response.data.suggestions && Array.isArray(response.data.suggestions)) {
      return response.data.suggestions.map(item => item.name);
    }
    return [];
  } catch (error) {
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
    throw new Error(error.response?.data?.message || "An error occurred while fetching suggestions.");
  }
};

// Function to add no match data to the backend
export const addNoMatchData = async (data) => {
  try {
    const response = await axios.post(`${BASE_URL}/add-no-match`, data);
    console.log("Add No Match Data API Response:", response);
    return response.data; // Return the response data to confirm successful submission
  } catch (error) {
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
    throw new Error(error.response?.data?.message || "An error occurred while adding no match data.");
  }
};
*/

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
*/

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