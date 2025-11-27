import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', type: 'ai', content: 'Hello! I\'m your AI Wealth Advisor. How can I help you today?', timestamp: new Date() },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), type: 'user', content: inputValue, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    setTimeout(() => {
      const aiMsg: Message = { id: (Date.now() + 1).toString(), type: 'ai', content: 'Mock response to: ' + inputValue, timestamp: new Date() };
      setMessages((prev) => [...prev, aiMsg]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-2xl rounded-lg px-4 py-3 ${msg.type === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-gray-900'}`}>
              <p className="text-sm">{msg.content}</p>
              <span className="text-xs opacity-70 mt-1 block">{msg.timestamp.toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t bg-white p-4">
        <div className="flex space-x-4">
          <textarea value={inputValue} onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask about investments..." className="flex-1 resize-none border rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500" rows={3} />
          <button onClick={handleSend} disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 self-end">
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;