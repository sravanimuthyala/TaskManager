import axios from "axios";

const API_URL = "https://taskmanager-uihb.onrender.com";

// CRUD
export const getTasks = () => axios.get(`${API_URL}/tasks`);

export const addTask = (title) =>
  axios.post(`${API_URL}/tasks`, {
    title,
    description: "",
    completed: false,
  });

export const updateTask = (id, title, completed) =>
  axios.put(`${API_URL}/tasks/${id}`, {
    title,
    description: "",
    completed,
  });

export const deleteTask = (id) => axios.delete(`${API_URL}/tasks/${id}`);

// AI
export const generateTask = (prompt) =>
  axios.post(`${API_URL}/generate_task`, { prompt });

export const getRecommendations = () =>
  axios.get(`${API_URL}/recommendations`);
