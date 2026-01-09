import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BiLeaf } from 'react-icons/bi';
import { FiArrowLeft, FiCheck, FiAlertTriangle, FiShield } from 'react-icons/fi';
import { MdLocalHospital, MdBugReport } from 'react-icons/md';
import './DiseaseLibrary.css';

const DiseaseLibrary = ({ onClose }) => {
  const [diseases, setDiseases] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDisease, setSelectedDisease] = useState(null);
  const [filteredDiseases, setFilteredDiseases] = useState([]);

  useEffect(() => {
    // Load class mapping to get all diseases
    const loadDiseases = async () => {
      try {
        const response = await fetch('/remedies.json');
        const data = await response.json();
        
        // Parse disease names and organize them
        const diseaseList = data.map(item => ({
          name: item.disease,
          displayName: item.disease.replace(/_/g, ' '),
          plant: item.disease.split('___')[0].replace(/_/g, ' '),
          condition: item.disease.split('___')[1]?.replace(/_/g, ' ') || 'Healthy',
          fungicide: item.fungicide || 'None required',
          pesticide: item.pesticide || 'None required',
          organic: item.organic || [],
          prevention: item.prevention || []
        }));

        setDiseases(diseaseList);
        setFilteredDiseases(diseaseList);
      } catch (error) {
        console.error('Error loading diseases:', error);
      }
    };

    loadDiseases();
  }, []);

  useEffect(() => {
    if (searchTerm === '') {
      setFilteredDiseases(diseases);
    } else {
      const filtered = diseases.filter(disease =>
        disease.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        disease.plant.toLowerCase().includes(searchTerm.toLowerCase()) ||
        disease.condition.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredDiseases(filtered);
    }
  }, [searchTerm, diseases]);

  // Group diseases by plant
  const groupedDiseases = filteredDiseases.reduce((acc, disease) => {
    if (!acc[disease.plant]) {
      acc[disease.plant] = [];
    }
    acc[disease.plant].push(disease);
    return acc;
  }, {});

  return (
    <motion.div 
      className="disease-library-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div 
        className="disease-library-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="library-header">
          <h2>DISEASE LIBRARY</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="library-search">
          <input
            type="text"
            placeholder="Search diseases, plants, conditions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-count">
            {filteredDiseases.length} disease{filteredDiseases.length !== 1 ? 's' : ''} found
          </span>
        </div>

        <div className="library-content">
          {selectedDisease ? (
            <motion.div 
              className="disease-detail"
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
            >
              <button 
                className="back-btn" 
                onClick={() => setSelectedDisease(null)}
              >
                <FiArrowLeft /> Back to List
              </button>
              
              <h3>{selectedDisease.displayName}</h3>
              
              <div className="detail-section">
                <h4><BiLeaf className="section-icon" /> PLANT</h4>
                <p>{selectedDisease.plant}</p>
              </div>

              <div className="detail-section">
                <h4><MdBugReport className="section-icon" /> CONDITION</h4>
                <p>{selectedDisease.condition}</p>
              </div>

              <div className="detail-section">
                <h4><MdLocalHospital className="section-icon" /> CHEMICAL TREATMENT</h4>
                <p><strong>Fungicide:</strong> {selectedDisease.fungicide}</p>
                <p><strong>Pesticide:</strong> {selectedDisease.pesticide}</p>
              </div>

              {selectedDisease.organic.length > 0 && (
                <div className="detail-section">
                  <h4><BiLeaf className="section-icon organic" /> ORGANIC TREATMENT</h4>
                  <ul>
                    {selectedDisease.organic.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedDisease.prevention.length > 0 && (
                <div className="detail-section">
                  <h4><FiShield className="section-icon" /> PREVENTION</h4>
                  <ul>
                    {selectedDisease.prevention.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="disease-list">
              {Object.keys(groupedDiseases).length === 0 ? (
                <div className="no-results">
                  <p>No diseases found matching "{searchTerm}"</p>
                </div>
              ) : (
                Object.entries(groupedDiseases).map(([plant, plantDiseases]) => (
                  <div key={plant} className="plant-group">
                    <h3 className="plant-name">{plant}</h3>
                    <div className="disease-grid">
                      {plantDiseases.map((disease) => (
                        <motion.div
                          key={disease.name}
                          className="disease-card"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setSelectedDisease(disease)}
                        >
                          <div className="disease-name">{disease.condition}</div>
                          <div className={`health-indicator ${disease.condition.toLowerCase().includes('healthy') ? 'healthy' : 'diseased'}`}>
                            {disease.condition.toLowerCase().includes('healthy') ? <FiCheck /> : <FiAlertTriangle />}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default DiseaseLibrary;
