import React, { useState } from "react";
import { FaMicrophone } from "react-icons/fa"; // Import microphone icon

const SpeechInput = () => {
  const [newMessage, setNewMessage] = useState("");
  const [isListening, setIsListening] = useState(false);

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
      setNewMessage((prevMessage) => prevMessage + transcript);
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

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginTop: "50px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Punjabi Speech-to-Text with Input</h1>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          border: "1px solid #ccc",
          borderRadius: "5px",
          padding: "10px",
          width: "300px",
          marginTop: "20px",
        }}
      >
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
          style={{
            flex: 1,
            border: "none",
            outline: "none",
            fontSize: "16px",
          }}
        />
        <button
          onClick={handleSpeechToText}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: isListening ? "red" : "#333",
            fontSize: "20px",
            marginLeft: "10px",
          }}
        >
          <FaMicrophone />
        </button>
      </div>
    </div>
  );
};

export default SpeechInput;
