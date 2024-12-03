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
