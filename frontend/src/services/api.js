import axios from "axios";

const BASE_URL = "http://localhost:5000";

export const searchName = async (name) => {
  try {
    const response = await axios.post(`${BASE_URL}/search`, { name });
    console.log("Full API Response:", response); // Debugging log
    return response.data.results || []; // Ensure results is an array
  } catch (error) {
    console.error("API Error:", error.response?.data || error.message);
    throw new Error(
      error.response?.data?.message || "An error occurred while fetching data."
    );
  }
};
