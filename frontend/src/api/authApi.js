import { httpJson } from "./http.js";

export function apiLogin({ username, password }) {
  return httpJson("/api/login", {
    method: "POST",
    body: { username, password },
  });
}

export function apiMe({ token }) {
  return httpJson("/api/me", {
    method: "GET",
    token,
  });
}

export function apiLogout({ token }) {
  return httpJson("/api/logout", {
    method: "POST",
    token,
  });
}

export function apiOtpRequest({ channel, phone, email, team_no }) {
  return httpJson("/api/otp/request", {
    method: "POST",
    body: { channel, phone, email, team_no },
  });
}

export function apiOtpVerify({ challenge_id, otp }) {
  return httpJson("/api/otp/verify", {
    method: "POST",
    body: { challenge_id, otp },
  });
}

/* ---------- Questions ---------- */

export function apiQuestions({ token }) {
  return httpJson("/api/questions", {
    method: "GET",
    token,
  });
}

/* ---------- Word Cloud Game APIs ---------- */

export function apiCreateRound({ token, question }) {
  return httpJson("/api/create-round", {
    method: "POST",
    token,
    body: { question },
  });
}

export function apiGetRoundDetails({ roundId }) {
  return httpJson(`/api/round/${roundId}`, {
    method: "GET",
  });
}

export function apiGetWordCloud({ roundId }) {
  return httpJson(`/api/round/${roundId}/wordcloud`, {
    method: "GET",
  });
}

export function apiSubmitResponse({ shareToken, word, playerId }) {
  return httpJson(`/respond/${shareToken}`, {
    method: "POST",
    body: { word, player_id: playerId },
  });
}

export function apiRecordShare({ roundId, playerId }) {
  return httpJson(`/api/round/${roundId}/share`, {
    method: "POST",
    body: { player_id: playerId },
  });
}

export function apiGetLeaderboard({ roundId }) {
  return httpJson(`/api/round/${roundId}/leaderboard`, {
    method: "GET",
  });
}

export function apiEndRound({ token, roundId }) {
  return httpJson(`/api/round/${roundId}/end`, {
    method: "POST",
    token,
  });
}
