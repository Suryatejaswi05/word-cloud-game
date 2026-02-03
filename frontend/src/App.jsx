import { Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "./pages/LoginPage.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import SelectQuestionPage from "./pages/SelectQuestionPage.jsx";
import RespondPage from "./pages/RespondPage.jsx";
import RoundDashboardPage from "./pages/RoundDashboardPage.jsx";
import StartGame from "./pages/startGame.jsx";
import WordCloudPage from "./pages/WordCloudPage.jsx";
import WordCloudGamePage from "./pages/WordCloudGamePage.jsx";
import SampleCloudPageWrapper from "./pages/SampleCloudPageWrapper.jsx";
import RequireAuth from "./auth/RequireAuth.jsx";

function App() {
  return (
    <Routes>
      {/* ---------------- PUBLIC ROUTES ---------------- */}
      <Route path="/login" element={<LoginPage />} />

      {/* ---------------- PROTECTED ROUTES ---------------- */}

      {/* Home / Landing */}
      <Route
        path="/"
        element={
          <RequireAuth>
            <LandingPage />
          </RequireAuth>
        }
      />

      <Route
        path="/landing"
        element={
          <RequireAuth>
            <LandingPage />
          </RequireAuth>
        }
      />

      <Route
        path="/select-question"
        element={
          <RequireAuth>
            <SelectQuestionPage />
          </RequireAuth>
        }
      />

      <Route
        path="/game"
        element={
          <RequireAuth>
            <StartGame />
          </RequireAuth>
        }
      />

      <Route
        path="/round/:id"
        element={
          <RequireAuth>
            <RoundDashboardPage />
          </RequireAuth>
        }
      />

      <Route
        path="/word-cloud"
        element={
          <RequireAuth>
            <WordCloudPage />
          </RequireAuth>
        }
      />

      <Route
        path="/word-cloud/:roundToken"
        element={
          <RequireAuth>
            <WordCloudGamePage />
          </RequireAuth>
        }
      />

      <Route
        path="/sample-cloud"
        element={<SampleCloudPageWrapper />}
      />

      {/* ---------------- PUBLIC RESPOND LINK ---------------- */}
      <Route path="/respond/:token" element={<RespondPage />} />

      {/* ---------------- FALLBACK ---------------- */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
