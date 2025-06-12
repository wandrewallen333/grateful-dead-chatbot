import React, { useState, useRef, useEffect } from 'react';
import { Send, Music, MessageCircle, Loader } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hey there, fellow Deadhead! 🌹💀⚡ Welcome to the cosmic journey through Grateful Dead knowledge. I'm your guide through 30 years of the Dead's music, history, and magic. What would you like to explore? Ask me about songs that'll blow your mind, legendary shows that changed everything, or the beautiful community that followed the music. Let's take this trip together!",
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking'); // 'checking', 'connected', 'disconnected'
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate session ID on component mount
  useEffect(() => {
    const newSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
  }, []);

  // Check API connection on component mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      const response = await fetch('/health');
      if (response.ok) {
        setApiStatus('connected');
      } else {
        setApiStatus('disconnected');
      }
    } catch (error) {
      setApiStatus('disconnected');
    }
  };

  // Call your Flask API
  const callChatbotAPI = async (userMessage) => {
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update session ID if server provided one
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
      }
      
      return data.response;
    } catch (error) {
      console.error('Error calling chatbot API:', error);
      setApiStatus('disconnected');
      return "Sorry, I'm having trouble connecting to the Dead knowledge base right now. Make sure your Flask API is running on http://localhost:5000! ⚡";
    }
  };

  const clearConversation = async () => {
    try {
      await fetch('/conversation/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
      
      // Reset to initial message
              setMessages([
        {
          id: 1,
          text: "Hey there, fellow Deadhead! 🌹💀⚡ Welcome to the cosmic journey through Grateful Dead knowledge. I'm your guide through 30 years of the Dead's music, history, and magic. What would you like to explore? Ask me about songs that'll blow your mind, legendary shows that changed everything, or the beautiful community that followed the music. Let's take this trip together!",
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputText,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Call your actual Python chatbot API
    try {
      const botResponseText = await callChatbotAPI(inputText);
      
      const botResponse = {
        id: messages.length + 2,
        text: botResponseText,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, botResponse]);
      setApiStatus('connected');
    } catch (error) {
      const errorResponse = {
        id: messages.length + 2,
        text: "Sorry, I'm having trouble connecting to the Dead knowledge base right now. Please try again! ⚡",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "Tell me about Jerry's magic ✨",
    "What makes Dark Star so cosmic? 🌟", 
    "Why is American Beauty perfect? 🌹",
    "What's the Deadhead experience like? 💫",
    "Recommend me a mind-blowing show 🎸"
  ];

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'connected': return 'text-green-400';
      case 'disconnected': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected': return 'Connected';
      case 'disconnected': return 'Disconnected';
      default: return 'Checking...';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <img src="/images/stealy.png" alt="Steal Your Face" className="logo-image" />
            </div>
            <div className="header-text">
              <h1>Ripple</h1>
              <p>Your AI assistant for all things Grateful Dead</p>
            </div>
          </div>
          <div className="header-right">
            <div className="api-status">
              <div className={`status-dot ${getStatusColor()}`}>●</div>
              <span className={getStatusColor()}>{getStatusText()}</span>
            </div>
            <button 
              onClick={clearConversation}
              className="clear-button"
              title="Clear Conversation"
            >
              Clear
            </button>
            <div className="header-music">
              <Music className="music-icon" />
              <span className="truckin-text">Keep on truckin'! 🎶</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-container">
        
        {/* Messages Container */}
        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-wrapper ${message.sender}`}
            >
              <div className={`message ${message.sender}`}>
                <p className="message-text">{message.text}</p>
                <p className="message-timestamp">{message.timestamp}</p>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="message-wrapper bot">
              <div className="message bot loading-message">
                <div className="loading-content">
                  <Loader className="loading-spinner" />
                  <span>Dead Bot is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="quick-questions">
            <p className="quick-questions-title">🌈 Start your journey with these cosmic questions:</p>
            <div className="quick-buttons">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputText(question)}
                  className="quick-button"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about the Dead's cosmic journey..."
              className="message-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isLoading}
              className="send-button"
            >
              <Send className="send-icon" />
              <span className="send-text">Send</span>
            </button>
          </div>
          
          <div className="input-footer">
            <div className="input-hint">
              <MessageCircle className="hint-icon" />
                                <span>Press Enter to send your message into the cosmos</span>
            </div>
            <span className="dead-emojis">🌹💀⚡</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;