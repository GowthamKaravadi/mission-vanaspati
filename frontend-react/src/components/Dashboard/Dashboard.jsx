import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { BiSun, BiMoon } from 'react-icons/bi';
import { MdLibraryBooks } from 'react-icons/md';
import { FiMessageSquare } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useHistory } from '../../context/HistoryContext';
import { predictionAPI } from '../../services/api';
import ImageUpload from './ImageUpload';
import Results from './Results';
import History from './History';
import Feedback from '../Feedback/Feedback';
import DiseaseLibrary from './DiseaseLibrary';
import ProfileDropdown from './ProfileDropdown';
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
        
        // Save to history with proper structure
        try {
          await addToHistory({
            type: 'single',
            disease: response.data.predicted_class,
            confidence: response.data.confidence,
            imageName: response.data.filename || files[0].name,
            alternatives: response.data.top_predictions || [],
            remedyInfo: {}, // Will be fetched separately when viewing details
          });
        } catch (historyErr) {
          console.error('Failed to save to history:', historyErr);
          // Don't block the user flow if history save fails
        }
        
        toast.success('Analysis complete!');
      } else {
        const response = await predictionAPI.predictBatch(files);
        setResults(response.data.predictions);
        
        // Save batch results to history
        try {
          for (const pred of response.data.predictions) {
            await addToHistory({
              type: 'batch',
              disease: pred.predicted_class,
              confidence: pred.confidence,
              imageName: pred.filename,
              alternatives: pred.top_predictions || [],
              remedyInfo: {},
            });
          }
        } catch (historyErr) {
          console.error('Failed to save batch to history:', historyErr);
        }
        
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
              className="theme-toggle-large"
              onClick={toggleTheme}
              whileHover={{ scale: 1.1, rotate: 180 }}
              whileTap={{ scale: 0.9 }}
              transition={{ duration: 0.3 }}
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDark ? <BiSun className="theme-icon" /> : <BiMoon className="theme-icon" />}
            </motion.button>
            <motion.button 
              className="icon-btn"
              onClick={() => setShowDiseaseLibrary(true)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Disease Library"
            >
              <MdLibraryBooks className="header-icon" />
            </motion.button>
            <ProfileDropdown
              user={user}
              isAdmin={isAdmin}
              onLogout={handleLogout}
              onAdminClick={() => navigate('/admin')}
              onMyGardenClick={() => navigate('/garden')}
            />
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

        {/* Feedback Button at Bottom */}
        <motion.div 
          className="feedback-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <motion.button
            className="btn-feedback-large"
            onClick={() => setShowFeedback(true)}
            whileHover={{ scale: 1.05, y: -4 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiMessageSquare className="feedback-icon" />
            <span>Send Feedback</span>
          </motion.button>
        </motion.div>
      </main>

      {showFeedback && <Feedback onClose={() => setShowFeedback(false)} />}
      {showDiseaseLibrary && <DiseaseLibrary onClose={() => setShowDiseaseLibrary(false)} />}
    </motion.div>
  );
};

export default Dashboard;
    