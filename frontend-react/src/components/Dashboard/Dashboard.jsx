import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useHistory } from '../../context/HistoryContext';
import { predictionAPI } from '../../services/api';
import ImageUpload from './ImageUpload';
import Results from './Results';
import History from './History';
import Feedback from '../Feedback/Feedback';
import DiseaseLibrary from './DiseaseLibrary';
import { ResultSkeleton } from '../LoadingSkeleton';
import './Dashboard.css';

const Dashboard = () => {
  const [mode, setMode] = useState('single');
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [showDiseaseLibrary, setShowDiseaseLibrary] = useState(false);
  
  const { user, logout, isAdmin } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const { addToHistory } = useHistory();
  const navigate = useNavigate();

  const handleFilesSelected = (selectedFiles) => {
    setFiles(selectedFiles);
    setResults(null);
  };

  const handleAnalyze = async () => {
    if (files.length === 0) return;
    
    setLoading(true);
    
    try {
      if (mode === 'single') {
        const response = await predictionAPI.predict(files[0]);
        setResults(response.data);
        addToHistory({
          type: 'single',
          result: response.data,
          filename: files[0].name
        });
        toast.success('Analysis complete!');
      } else {
        const response = await predictionAPI.predictBatch(files);
        setResults(response.data.predictions);
        addToHistory({
          type: 'batch',
          results: response.data.predictions,
          count: files.length
        });
        toast.success(`Analyzed ${files.length} images!`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <motion.div 
      className="dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">MV</span>
            <h1>Mission Vanaspati</h1>
          </div>
          <div className="header-actions">
            <motion.button 
              className="theme-toggle"
              onClick={toggleTheme}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              {isDark ? '○' : '●'}
            </motion.button>
            <motion.button 
              className="icon-btn"
              onClick={() => setShowDiseaseLibrary(true)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Disease Library"
            >
              📖
            </motion.button>
            <motion.button 
              className="icon-btn"
              onClick={() => setShowFeedback(true)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Report Feedback"
            >
              ✎
            </motion.button>
            <span className="user-email">{user?.username}</span>
            {isAdmin && (
              <motion.button 
                onClick={() => navigate('/admin')} 
                className="btn btn-secondary"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Admin Panel
              </motion.button>
            )}
            <motion.button 
              onClick={handleLogout} 
              className="btn btn-outline"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Logout
            </motion.button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <motion.div 
          className="mode-selector"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <motion.button 
            className={`mode-btn ${mode === 'single' ? 'active' : ''}`}
            onClick={() => { setMode('single'); setFiles([]); setResults(null); }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Single Image
          </motion.button>
          <motion.button 
            className={`mode-btn ${mode === 'batch' ? 'active' : ''}`}
            onClick={() => { setMode('batch'); setFiles([]); setResults(null); }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Batch Upload
          </motion.button>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <ImageUpload 
            mode={mode}
            onFilesSelected={handleFilesSelected}
          />
        </motion.div>

        {files.length > 0 && (
          <motion.button 
            onClick={handleAnalyze} 
            disabled={loading}
            className="btn btn-primary btn-analyze"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? 'Analyzing...' : `Analyze ${files.length} Image${files.length > 1 ? 's' : ''}`}
          </motion.button>
        )}

        {loading && <ResultSkeleton mode={mode} />}
        
        {!loading && results && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Results results={results} mode={mode} />
          </motion.div>
        )}

        <History />
      </main>

      {showFeedback && <Feedback onClose={() => setShowFeedback(false)} />}
      {showDiseaseLibrary && <DiseaseLibrary onClose={() => setShowDiseaseLibrary(false)} />}
    </motion.div>
  );
};

export default Dashboard;
    