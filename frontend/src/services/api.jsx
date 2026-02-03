import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getQuestions = async () => {
  const res = await fetch(`${BASE_URL}/api/questions/`);
  return res.json();
};

export const submitAnswer = async (data) => {
  const res = await fetch(`${BASE_URL}/api/submit-answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return res.json();
};

export const getWordCloud = async () => {
  const res = await fetch(`${BASE_URL}/api/wordcloud`);
  return res.json();
};

// Word Cloud Game APIs
export const wordCloudApi = {
  createRound: (data, token) => axios.post(`${BASE_URL}/api/word-cloud/create/`, data, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  getRoundDetails: (shareToken) => axios.get(`${BASE_URL}/api/word-cloud/${shareToken}/details/`),
  submitResponse: (shareToken, data, token) => axios.post(`${BASE_URL}/api/word-cloud/${shareToken}/respond/`, data, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  getWordCloudData: (shareToken) => axios.get(`${BASE_URL}/api/word-cloud/${shareToken}/data/`),
  recordShare: (shareToken, data, token) => axios.post(`${BASE_URL}/api/word-cloud/${shareToken}/share/`, data, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  getLeaderboard: (shareToken) => axios.get(`${BASE_URL}/api/word-cloud/${shareToken}/leaderboard/`),
  endRound: (shareToken, token) => axios.post(`${BASE_URL}/api/word-cloud/${shareToken}/end/`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  })
};