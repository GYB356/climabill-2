import React, { useState, useEffect, useRef } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIChat = ({ company }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: `Hello! I'm your ClimaBill AI assistant. I can help you analyze ${company.name}'s carbon footprint, suggest reduction strategies, and explain financial impacts. What would you like to know?`,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const sampleQuestions = [
    "What's our biggest source of emissions?",
    "How much could we save by switching to renewable energy?",
    "What are our carbon reduction opportunities?",
    "How do we compare to industry benchmarks?",
    "What's the ROI on our green initiatives?",
    "Help me understand our Scope 3 emissions"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${API}/companies/${company.id}/ai/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_id: company.id,
          query_text: message
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: 'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date(),
          error: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, I encountered a network error. Please check your connection and try again.',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">
          🤖 AI Carbon Intelligence Assistant
        </h1>
        <p className="text-gray-400">
          Ask questions about {company.name}'s carbon footprint, get insights, and discover reduction opportunities
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Chat Container */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col h-[600px]">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-green-600 text-white'
                      : message.error
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-700 text-gray-100'
                  }`}
                >
                  {message.type === 'ai' && (
                    <div className="flex items-center mb-2">
                      <span className="text-lg mr-2">🤖</span>
                      <span className="font-medium">ClimaBill AI</span>
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-70 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-700 text-gray-100 p-4 rounded-lg max-w-[80%]">
                  <div className="flex items-center mb-2">
                    <span className="text-lg mr-2">🤖</span>
                    <span className="font-medium">ClimaBill AI</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="animate-bounce h-2 w-2 bg-green-500 rounded-full"></div>
                    <div className="animate-bounce h-2 w-2 bg-green-500 rounded-full" style={{animationDelay: '0.1s'}}></div>
                    <div className="animate-bounce h-2 w-2 bg-green-500 rounded-full" style={{animationDelay: '0.2s'}}></div>
                    <span className="text-sm text-gray-400">Analyzing your data...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-700 p-4">
            <div className="flex space-x-4">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about carbon emissions, reduction strategies, financial impact..."
                className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                disabled={loading}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={loading || !inputMessage.trim()}
                className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Sample Questions */}
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-white mb-4">💡 Try asking:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sampleQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(question)}
                disabled={loading}
                className="text-left p-3 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg text-gray-300 hover:text-white transition-colors disabled:opacity-50"
              >
                <span className="text-green-400 mr-2">Q:</span>
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* AI Capabilities */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">🧠 AI Capabilities</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <div className="font-medium text-white mb-1">Data Analysis</div>
              <div className="text-sm text-gray-400">Analyze emissions patterns and trends</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">💡</div>
              <div className="font-medium text-white mb-1">Recommendations</div>
              <div className="text-sm text-gray-400">Suggest reduction strategies with ROI</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium text-white mb-1">Forecasting</div>
              <div className="text-sm text-gray-400">Predict future emissions and costs</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;