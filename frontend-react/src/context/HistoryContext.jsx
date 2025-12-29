import { createContext, useContext, useState, useEffect } from 'react';

const HistoryContext = createContext();

export const useHistory = () => {
  const context = useContext(HistoryContext);
  if (!context) {
    throw new Error('useHistory must be used within HistoryProvider');
  }
  return context;
};

export const HistoryProvider = ({ children }) => {
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('prediction_history');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('prediction_history', JSON.stringify(history));
  }, [history]);

  const addToHistory = (prediction) => {
    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...prediction
    };
    setHistory(prev => [entry, ...prev].slice(0, 50)); // Keep last 50
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('prediction_history');
  };

  const deleteHistoryItem = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  return (
    <HistoryContext.Provider value={{ history, addToHistory, clearHistory, deleteHistoryItem }}>
      {children}
    </HistoryContext.Provider>
  );
};
