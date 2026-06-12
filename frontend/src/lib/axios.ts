import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL,
  withCredentials: false,
  timeout: 60000, // 60s — LLM calls can be slow
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;