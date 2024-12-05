import React from "react";

const VoiceSearchButton = ({ onVoiceInput }) => {
  const handleVoiceSearch = () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onVoiceInput(transcript); // Pass the transcribed text to the parent component
    };
    recognition.start();
  };

  return (
    <button
      onClick={handleVoiceSearch}
      className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-4 py-2 flex items-center space-x-2 shadow-md"
    >
      <span>🎤</span>
      <span>Voice Search</span>
    </button>
  );
};

export default VoiceSearchButton;
