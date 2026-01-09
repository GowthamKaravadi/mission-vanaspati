import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiImage, FiFolder, FiTrash2 } from 'react-icons/fi';
import { useHistory } from '../../context/HistoryContext';
import formatClassName from '../../utils/formatClassName';
import './History.css';

const History = () => {
  const { history, clearHistory, deleteHistoryItem, loading } = useHistory();

  if (loading) {
    return (
      <motion.div 
        className="history-empty"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="loader"></div>
        <p>Loading history...</p>
      </motion.div>
    );
  }

  if (history.length === 0) {
    return (
      <motion.div 
        className="history-empty"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <FiClock className="empty-icon" />
        <p>No analysis history yet</p>
        <small>Your predictions will appear here</small>
      </motion.div>
    );
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  return (
    <motion.div 
      className="history-container"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <div className="history-header">
        <h3><FiClock className="header-icon" /> Analysis History</h3>
        <motion.button 
          onClick={clearHistory} 
          className="btn-clear-history"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Clear All
        </motion.button>
      </div>

      <div className="history-list">
        <AnimatePresence>
          {history.map((item) => (
            <motion.div
              key={item.id}
              className="history-item"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              layout
            >
              <div className="history-item-content">
                <div className="history-item-header">
                  <span className="history-type-badge">
                    {item.diagnosis_type === 'single' ? <><FiImage /> Single</> : <><FiFolder /> Batch</>}
                  </span>
                  <span className="history-timestamp">{formatDate(item.diagnosed_at || item.timestamp)}</span>
                </div>

                <div className="history-result">
                  <strong>{formatClassName(item.disease_name || item.result?.predicted_class || 'Unknown')}</strong>
                  <span className="confidence-badge">
                    {((item.confidence || item.result?.confidence || 0) * 100).toFixed(1)}%
                  </span>
                </div>

                {item.image_name && (
                  <small className="history-filename">{item.image_name}</small>
                )}
              </div>

              <motion.button
                onClick={() => deleteHistoryItem(item.id)}
                className="btn-delete-history"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Delete"
              >
                <FiTrash2 />
              </motion.button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default History;
