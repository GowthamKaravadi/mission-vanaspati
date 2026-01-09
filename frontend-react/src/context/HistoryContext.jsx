import { createContext, useContext, useState, useEffect } from 'react';
import { historyAPI } from '../services/api';
import toast from 'react-hot-toast';

const HistoryContext = createContext();

export const useHistory = () => {
  const context = useContext(HistoryContext);
  if (!context) {
    throw new Error('useHistory must be used within HistoryProvider');
  }
  return context;
};

export const HistoryProvider = ({ children }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Fetch history from database on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return;
        }

        const response = await historyAPI.getHistory(50, 0);
        setHistory(response.data.history);
        setTotal(response.data.total);
      } catch (error) {
        console.error('Failed to load history:', error);
        if (error.response?.status !== 401) {
          toast.error('Failed to load diagnosis history');
        }
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const addToHistory = async (entry) => {
    try {
      // Save to database
      const response = await historyAPI.saveHistory({
        diagnosis_type: entry.type || 'single',
        image_name: entry.imageName || 'unknown',
        disease_name: entry.disease,
        confidence: entry.confidence,
        alternatives: entry.alternatives || [],
        remedy_info: entry.remedyInfo || {},
        notes: entry.notes || null,
      });

      // Add to local state with the database ID
      const newEntry = {
        id: response.data.diagnosis_id,
        diagnosis_type: entry.type || 'single',
        image_name: entry.imageName || 'unknown',
        disease_name: entry.disease,
        confidence: entry.confidence,
        alternatives: entry.alternatives || [],
        remedy_info: entry.remedyInfo || {},
        diagnosed_at: new Date().toISOString(),
        notes: entry.notes || null,
        status: 'active',
      };

      setHistory((prev) => [newEntry, ...prev]);
      setTotal((prev) => prev + 1);
      
      return response.data.diagnosis_id;
    } catch (error) {
      console.error('Failed to save to history:', error);
      toast.error('Failed to save diagnosis to history');
      throw error;
    }
  };

  const clearHistory = async () => {
    try {
      await historyAPI.clearHistory();
      setHistory([]);
      setTotal(0);
      toast.success('History cleared successfully');
    } catch (error) {
      console.error('Failed to clear history:', error);
      toast.error('Failed to clear history');
      throw error;
    }
  };

  const deleteHistoryItem = async (id) => {
    try {
      await historyAPI.deleteHistory(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
      setTotal((prev) => prev - 1);
      toast.success('Item deleted successfully');
    } catch (error) {
      console.error('Failed to delete history item:', error);
      toast.error('Failed to delete item');
      throw error;
    }
  };

  return (
    <HistoryContext.Provider value={{ history, addToHistory, clearHistory, deleteHistoryItem, loading, total }}>
      {children}
    </HistoryContext.Provider>
  );
};
