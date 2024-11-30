import axios from "axios";

const BASE_URL = "http://localhost:5000"; // Update with your backend URL

export const searchName = async (name) => {
  try {
    const response = await axios.post(`${BASE_URL}/search`, { name });
    return response.data.results;
  } catch (error) {
    console.error("Error searching for the name:", error);
    throw error;
  }
};
