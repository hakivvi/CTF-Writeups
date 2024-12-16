import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import HomePage from "./components/HomePage";
import ShareExperiencePage from "./components/ShareExperiencePage";

const App = () => {
  return (
    <Router>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/share-experience" element={<ShareExperiencePage />} />
      <Route path="/" element={<Navigate to="/login" />} />
    </Routes>
  </Router>
  );
};

export default App;
