import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import ChatbotPage from "./pages/ChatbotPage";
import AuthPage from "./pages/AuthPage";


function App() {
  const [authenticated, setAuthenticated] = useState(
    !!localStorage.getItem("token")
  );

  const handleLogout = () => {
    localStorage.removeItem("token"); // token stored in local storage of browser
    setAuthenticated(false);
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            authenticated ? (
              <ChatbotPage onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" />
            )
          }
        />
        <Route
          path="/auth"
          element={<AuthPage setAuthenticated={setAuthenticated} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
