import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { gardenAPI } from '../../services/api';
import './MyGarden.css';

const MyGarden = ({ onClose }) => {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPlant, setEditingPlant] = useState(null);
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    loadPlants();
  }, []);

  const loadPlants = async () => {
    try {
      const response = await gardenAPI.getPlants();
      setPlants(response.data.plants || []);
    } catch (err) {
      toast.error('Failed to load garden');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (plantId) => {
    if (!confirm('Remove this plant from your garden?')) return;
    
    try {
      await gardenAPI.deletePlant(plantId);
      toast.success('Plant removed');
      loadPlants();
    } catch (err) {
      toast.error('Failed to delete plant');
    }
  };

  const handleUpdatePlant = async (plantId) => {
    try {
      await gardenAPI.updatePlant(plantId, notes || null, status || null);
      toast.success('Plant updated');
      setEditingPlant(null);
      setNotes('');
      setStatus('');
      loadPlants();
    } catch (err) {
      toast.error('Failed to update plant');
    }
  };

  const startEdit = (plant) => {
    setEditingPlant(plant.id);
    setNotes(plant.notes || '');
    setStatus(plant.status);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'monitoring': return '#ffc107';
      case 'treating': return '#ff5722';
      case 'recovered': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  return (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="my-garden-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>🌿 My Garden</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="loading-garden">Loading your garden...</div>
          ) : plants.length === 0 ? (
            <div className="empty-garden">
              <span className="empty-icon">🌱</span>
              <p>No plants in your garden yet</p>
              <small>Diagnose plants and save them to track their health!</small>
            </div>
          ) : (
            <div className="plants-grid">
              <AnimatePresence>
                {plants.map((plant, index) => (
                  <motion.div
                    key={plant.id}
                    className="plant-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="plant-header">
                      <div className="plant-title">
                        <h3>{plant.plant_name}</h3>
                        <span 
                          className="status-badge"
                          style={{ background: getStatusColor(plant.status) }}
                        >
                          {plant.status}
                        </span>
                      </div>
                      <div className="plant-actions">
                        <button 
                          onClick={() => startEdit(plant)}
                          className="icon-btn"
                          title="Edit"
                        >
                          ✎
                        </button>
                        <button 
                          onClick={() => handleDelete(plant.id)}
                          className="icon-btn delete-btn"
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    <div className="plant-disease">
                      <strong>Disease:</strong> {plant.disease_name}
                    </div>

                    <div className="plant-confidence">
                      <span>Confidence:</span>
                      <div className="confidence-bar-mini">
                        <div 
                          className="confidence-fill-mini"
                          style={{ width: `${plant.confidence * 100}%` }}
                        >
                          {(plant.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    {editingPlant === plant.id ? (
                      <div className="edit-section">
                        <select 
                          value={status}
                          onChange={(e) => setStatus(e.target.value)}
                          className="status-select"
                        >
                          <option value="monitoring">Monitoring</option>
                          <option value="treating">Treating</option>
                          <option value="recovered">Recovered</option>
                        </select>
                        <textarea
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          placeholder="Add notes about treatment..."
                          className="notes-textarea"
                          rows="3"
                        />
                        <div className="edit-actions">
                          <button 
                            onClick={() => handleUpdatePlant(plant.id)}
                            className="btn btn-sm btn-primary"
                          >
                            Save
                          </button>
                          <button 
                            onClick={() => setEditingPlant(null)}
                            className="btn btn-sm btn-secondary"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {plant.notes && (
                          <div className="plant-notes">
                            <strong>Notes:</strong>
                            <p>{plant.notes}</p>
                          </div>
                        )}
                        <div className="plant-dates">
                          <small>
                            Diagnosed: {new Date(plant.diagnosed_at).toLocaleDateString()}
                          </small>
                        </div>
                      </>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MyGarden;
