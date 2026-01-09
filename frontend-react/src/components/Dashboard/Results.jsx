import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { BiLeaf } from 'react-icons/bi';
import { FiDownload, FiSave } from 'react-icons/fi';
import api, { gardenAPI } from '../../services/api';
import { generateDiagnosisReport, generateBatchReport } from '../../utils/pdfGenerator';
import formatClassName from '../../utils/formatClassName';
import './Dashboard.css';

const Results = ({ results, mode }) => {
  const [remedies, setRemedies] = useState({});
  const [savingToGarden, setSavingToGarden] = useState(false);

  useEffect(() => {
    api.get('/remedies')
      .then(res => {
        const remediesMap = {};
        res.data.forEach(item => {
          remediesMap[item.class_name] = {
            description: item.description,
            remedies: item.remedies,
            products: item.products || []
          };
        });
        setRemedies(remediesMap);
      })
      .catch(() => {});
  }, []);

  const saveToGarden = async (className, confidence) => {
    setSavingToGarden(true);
    try {
      const plantName = className.split('___')[0]; // Extract plant name
      await gardenAPI.savePlant(plantName, className, confidence, null, 'monitoring');
      toast.success('Plant saved to your garden!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save plant');
    } finally {
      setSavingToGarden(false);
    }
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
  };

  const getRemedyInfo = (className) => {
    const remedy = remedies[className];
    return remedy || { description: 'No information available', remedies: [], products: [] };
  };

  const handleDownloadPDF = () => {
    if (mode === 'single') {
      const result = Array.isArray(results) ? results[0] : results;
      const className = result.predicted_class || result.class;
      const remedyInfo = getRemedyInfo(className);
      generateDiagnosisReport(result, remedyInfo);
      toast.success('PDF downloaded successfully!');
    } else {
      generateBatchReport(results, remedies);
      toast.success('Batch report downloaded!');
    }
  };

  if (!results || (Array.isArray(results) && results.length === 0)) {
    return null;
  }

  if (mode === 'single') {
    const result = Array.isArray(results) ? results[0] : results;
    const className = result.predicted_class || result.class;
    const confidence = result.confidence;
    const alternatives = result.top_predictions || result.alternatives || [];
    const remedyInfo = getRemedyInfo(className);
    
    return (
      <div className="results-container">
        <div className="result-card">
          <h2>Analysis Results</h2>
          
          <div className="prediction-main">
            <h3 className="prediction-name">{formatClassName(className)}</h3>
            <div className="confidence-container">
              <span className="confidence-label">Confidence:</span>
              <div className="confidence-bar">
                <motion.div 
                  className={`confidence-fill ${getConfidenceClass(confidence)}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${confidence * 100}%` }}
                  transition={{ duration: 1, ease: "easeOut", type: "spring", stiffness: 50 }}
                >
                  {(confidence * 100).toFixed(1)}%
                </motion.div>
              </div>
            </div>
          </div>

          {alternatives && alternatives.length > 0 && (
            <div className="alternatives">
              <h4>Alternative Predictions:</h4>
              {alternatives.map((alt, idx) => (
                <motion.div 
                  key={idx} 
                  className="alternative-item"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <span>{formatClassName(alt.class || alt.predicted_class)}</span>
                  <span className="alt-confidence">{(alt.confidence * 100).toFixed(1)}%</span>
                </motion.div>
              ))}
            </div>
          )}

          <div className="disease-info">
            <h3>About this condition</h3>
            <p>{remedyInfo.description}</p>
            
            {remedyInfo.remedies && remedyInfo.remedies.length > 0 && (
              <>
                <h4>Recommended Actions:</h4>
                <ul className="remedies-list">
                  {remedyInfo.remedies.map((remedy, idx) => (
                    <li key={idx}>{remedy}</li>
                  ))}
                </ul>
              </>
            )}

            {remedyInfo.products && remedyInfo.products.length > 0 && (
              <div className="products-section">
                <h4>🛒 Recommended Products:</h4>
                <div className="products-grid">
                  {remedyInfo.products.map((product, idx) => (
                    <motion.a
                      key={idx}
                      href={product.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="product-card"
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      <span className="product-icon">🛍️</span>
                      <div className="product-info">
                        <strong>{product.name}</strong>
                        <small>{product.type}</small>
                      </div>
                      <span className="product-arrow">→</span>
                    </motion.a>
                  ))}
                </div>
              </div>
            )}

            <div className="action-buttons-row">
              <motion.button
                className="btn btn-primary save-to-garden-btn"
                onClick={() => saveToGarden(className, confidence)}
                disabled={savingToGarden}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                {savingToGarden ? <><FiSave className="btn-icon spin" /> Saving...</> : <><BiLeaf className="btn-icon" /> Save to My Garden</>}
              </motion.button>
              
              <motion.button
                className="btn btn-secondary download-pdf-btn"
                onClick={handleDownloadPDF}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <FiDownload className="btn-icon" /> Download PDF Report
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Batch mode
  return (
    <div className="results-container">
      <div className="batch-results-header">
        <h2>Batch Analysis Results</h2>
        <div className="stats-summary">
          <div className="stat">
            <span className="stat-value">{results.length}</span>
            <span className="stat-label">Images Analyzed</span>
          </div>
          <motion.button
            className="btn btn-secondary download-pdf-btn"
            onClick={handleDownloadPDF}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            📄 Download Batch Report
          </motion.button>
        </div>
      </div>

      <div className="batch-results-grid">
        {results.map((result, idx) => {
          const className = result.predicted_class || result.class;
          const alternatives = result.top_predictions || result.alternatives || [];
          const remedyInfo = getRemedyInfo(className);
          
          return (
            <motion.div 
              key={idx} 
              className="batch-result-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.1, duration: 0.3 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="batch-result-header">
                <h4>{formatClassName(className)}</h4>
                <motion.span 
                  className={`badge ${getConfidenceClass(result.confidence)}`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: idx * 0.1 + 0.2, type: "spring", stiffness: 200 }}
                >
                  {(result.confidence * 100).toFixed(1)}%
                </motion.span>
              </div>
              
              <div className="batch-description">
                <p>{remedyInfo.description}</p>
              </div>
              
              {remedyInfo.remedies && remedyInfo.remedies.length > 0 && (
                <div className="batch-remedies">
                  <h5>Remedies:</h5>
                  <ul>
                    {remedyInfo.remedies.slice(0, 3).map((remedy, i) => (
                      <motion.li 
                        key={i}
                        initial={{ x: -10, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: idx * 0.1 + i * 0.05 }}
                      >
                        {remedy}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              )}
              
              {alternatives && alternatives.length > 0 && (
                <div className="batch-alternatives">
                  <small>Alternatives:</small>
                  {alternatives.slice(0, 2).map((alt, i) => (
                    <div key={i} className="batch-alt">
                      <span>{formatClassName(alt.class || alt.predicted_class)}</span>
                      <span>{(alt.confidence * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default Results;
