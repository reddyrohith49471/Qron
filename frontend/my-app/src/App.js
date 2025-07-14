import React from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "./LandingPage";
import EmailApp from "./EmailApp";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<EmailApp />} />
    </Routes>
  );
}

export default App;
