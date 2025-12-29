import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import './Dashboard.css';

const Results = ({ results, mode }) => {
  const [remedies, setRemedies] = useState({});

  useEffect(() => {
    axios.get('http://localhost:8000/remedies')
      .then(res => {
        const remediesMap = {};
        res.data.forEach(item => {
          remediesMap[item.class_name] = {
            description: item.description,
            remedies: item.remedies
          };
        });
        setRemedies(remediesMap);
      })
      .catch(err => console.error('Failed to load remedies:', err));
  }, []);

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
  };

  const getRemedyInfo = (className) => {
    console.log('Looking for remedy:', className);
    console.log('Available remedies:', Object.keys(remedies));
    const remedy = remedies[className];
    if (!remedy) {
      console.warn('Remedy not found for:', className);
    }
    return remedy || { description: 'No information available', remedies: [] };
  };

  if (!results || (Array.isArray(results) && results.length === 0)) {
    return null;
  }

  if (mode === 'single') {
    const result = Array.isArray(results) ? results[0] : results;
    console.log('Full result object:', result);
    const className = result.predicted_class || result.class;
    const confidence = result.confidence;
    const alternatives = result.top_predictions || result.alternatives || [];
    const remedyInfo = getRemedyInfo(className);
    
    return (
      <div className="results-container">
        <div className="result-card">
          <h2>Analysis Results</h2>
          
          <div className="prediction-main">
            <h3 className="prediction-name">{className}</h3>
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
                  <span>{alt.class || alt.predicted_class}</span>
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
                <h4>{className}</h4>
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
                      <span>{alt.class || alt.predicted_class}</span>
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
