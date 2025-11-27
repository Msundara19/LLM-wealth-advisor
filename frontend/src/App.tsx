import React, { useState } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import Portfolio from './components/Portfolio';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { AuthProvider, useAuth } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import Login from './components/Login';
import { Toaster } from 'react-hot-toast';

function AppContent() {
  const { isAuthenticated, user } = useAuth();
  const [activeView, setActiveView] = useState('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen}
        activeView={activeView}
        onViewChange={setActiveView}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header 
          user={user}
          onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        {/* Content Area */}
        <main className="flex-1 overflow-hidden">
          {activeView === 'chat' && <ChatInterface />}
          {activeView === 'portfolio' && <Portfolio />}
          {activeView === 'recommendations' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Investment Recommendations</h2>
              {/* Recommendations component will go here */}
            </div>
          )}
          {activeView === 'reports' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Reports & Analytics</h2>
              {/* Reports component will go here */}
            </div>
          )}
        </main>
      </div>

      <Toaster position="top-right" />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <AppContent />
      </WebSocketProvider>
    </AuthProvider>
  );
}

export default App;