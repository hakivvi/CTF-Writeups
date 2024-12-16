import axios from "axios";

const API_URL = "http://10.25.1.156:8000/api";

export const getFrameworks = async (token) => {
  try {
    const response = await axios.get(`${API_URL}/webframeworks`, {headers: {'Token': `Bearer ${token}`}});
    return response.data;
  } catch (err) {
    console.error("Error fetching frameworks:", err);
    throw err;
  }
};

export const getExperiences = async (token) => {
  try {
    const response = await axios.get(`${API_URL}/experiences`, {headers: {'Token': `Bearer ${token}`}});
    return response.data;
  } catch (err) {
    console.error("Error fetching experiences:", err);
    throw err;
  }
};

export const postExperience = async (token, experience) => {
  try {
    const response = await axios.post(
      `${API_URL}/experiences`, experience, {headers: {'Token': `Bearer ${token}`}}
    );
    return response.data;
  } catch (err) {
    console.error("Error posting experience:", err);
    throw err;
  }
};
