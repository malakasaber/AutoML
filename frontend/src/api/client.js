import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for long-running training requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for error handling
client.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default client;