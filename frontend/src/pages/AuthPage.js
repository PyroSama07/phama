import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styling/AuthPage.css";

function AuthPage({ setAuthenticated }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    username: "",
    password: "",
  });

  const navigate = useNavigate(); // Hook for navigation the chatbot page

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (isLogin) {
        // Login logic
        const loginData = new URLSearchParams();
        loginData.append("username", formData.username.trim()); // trime user name of the additional spaces
        loginData.append("password", formData.password);
        const response = await axios.post(
          `${process.env.REACT_APP_API_KEY}/token`,
          loginData,
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          }
        );

        if (response.status === 200) {
          console.log(response.data);
          localStorage.setItem("token", response.data.access_token);
          setAuthenticated(true);
          navigate("/"); // Redirect to Chatbot page
        }
      } else {
        // Signup logic
        const signupData = {
          name: formData.name.trim(),
          username: formData.username.trim(),
          hashed_password: formData.password,
        };

        const response = await axios.post(
          `${process.env.REACT_APP_API_KEY}/create_user/`,
          signupData,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (response.status === 200 || response.status === 201) {
          alert("User created successfully! Please log in.");
          console.log(response.data);
          setIsLogin(true);
        }
      }
    } catch (error) {
      console.error("Authentication error:", error);
      alert("Authentication failed. Please try again.");
    }
  };

  return (
    <div className="auth-container">
      <form onSubmit={handleSubmit}>
        <h1>{isLogin ? "Login" : "Sign Up"}</h1>

        {!isLogin && (
          <input
            type="text"
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        )}
        <input
          type="text"
          placeholder="Username"
          value={formData.username}
          onChange={(e) =>
            setFormData({ ...formData, username: e.target.value })
          }
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          required
        />

        <button className="login-button" type="submit">
          {isLogin ? "Login" : "Signup"}
        </button>

        <button className="switch-button" onClick={() => setIsLogin(!isLogin)}>
          {isLogin ? "Dont't have an account? Sign Up" : "Click here to Login"}
        </button>
      </form>
    </div>
  );
}

export default AuthPage;
