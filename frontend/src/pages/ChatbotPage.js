import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
// import { FaMicrophone } from "react-icons/fa";
import "../styling/ChatbotPage.css";

function ChatbotPage({ onLogout }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [userName, setUserName] = useState(""); // To store user's name
  const [isListening, setIsListening] = useState(false); // To handle listening state
  const token = localStorage.getItem("token");
  const chatBoxRef = useRef(null);

  useEffect(() => {
    fetchUserData();
    fetchMessages();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_KEY}/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setUserName(response.data.name);
    } catch (error) {
      console.error("Error fetching user data:", error);
      alert("Failed to fetch user data. Please log in again.");
      onLogout(); // Log out the user if the request fails
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_KEY}/get_all_message`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessages(response.data);
    } catch (error) {
      console.error("Error fetching messages:", error);
      alert("Error fetching messages, try login again");
      onLogout(); // Log out the user if the request fails
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    try {
      await axios.post(
        `${process.env.REACT_APP_API_KEY}/send_message`,
        { msg: newMessage },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setNewMessage("");
      fetchMessages();
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Error sending message, try login again");
      onLogout(); // Log out the user if the request fails
    }
  };

  const deleteAllMessages = async () => {
    try {
      await axios.delete(
        `${process.env.REACT_APP_API_KEY}/delete_all_messages`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessages([]);
      alert("All messages have been deleted successfully!");
    } catch (error) {
      console.error("Error deleting messages:", error);
      alert("Failed to delete messages, try login again.");
      onLogout(); // Log out the user if the request fails
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(
        `${process.env.REACT_APP_API_KEY}/logout`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      localStorage.removeItem("token");
      onLogout();
    } catch (error) {
      console.error("Error during logout:", error);
      alert("Error");
    }
  };

  const handleSpeechToText = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Your browser does not support speech recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "pa-IN"; // Set language to Punjabi (India)

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setNewMessage(transcript);
    };

    recognition.onerror = (event) => {
      alert(`Error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const scrollToBottom = () => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  };

  return (
    <div className="chatbot-container">
      <div
        className="menu"
        onMouseEnter={() => setMenuOpen(true)}
        onMouseLeave={() => setMenuOpen(false)}
      >
        <span className="dots">•••</span>
        {menuOpen && (
          <div className="menu-options">
            <p className="menu-user">Logged in as: {userName || "User"}</p>
            <button onClick={deleteAllMessages}>Clear all messages</button>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </div>

      <h1>PHAMA ਫਾਮਾ</h1>
      <div className="chat-box" ref={chatBoxRef}>
        {messages.length > 0 ? (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-message ${
                msg.sender ? "bot-message" : "user-message"
              }`}
            >
              <span className="message-content">{msg.msg}</span>
              <span className="message-time">
                {new Date(msg.time_stamp).toLocaleTimeString()}
              </span>
            </div>
          ))
        ) : (
          <p>
            ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! {userName || "User"}, ਮੇਰਾ ਨਾਮ ਫਾਮਾ ਹੈ| ਤੁਸੀਂ ਮੈਨੂੰ
            ਪੰਜਾਬ ਵਿੱਚ ਖੇਤੀਬਾੜੀ ਬਾਰੇ ਆਪਣੇ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ|
            <br />
            Hello {userName || "User"}, My name is PHAMA you can ask me any
            questions about agriculture in Punjab.
          </p>
        )}

        <div className="input-area">
          
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="input-field"
          />
          <button
            onClick={handleSpeechToText}
            className="mic-button"
            style={{ color: isListening ? "red" : "#333" }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill={isListening ? "red" : "currentColor"}
              width="24px"
              height="24px"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3s-3 1.34-3 3v6c0 1.66 1.34 3 3 3zm4.3-3c0 2.89-2.4 5.3-5.3 5.3s-5.3-2.41-5.3-5.3H3c0 4.1 3.1 7.45 7 7.93V22h4v-2.07c3.9-.48 7-3.83 7-7.93h-2.7z" />
            </svg>
          </button>
          <button onClick={sendMessage} className="send-button">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatbotPage;
