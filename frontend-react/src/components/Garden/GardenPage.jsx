import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  FiHome, FiLogOut, FiTrash2, FiEdit2, FiRefreshCw, 
  FiEye, FiActivity, FiCheckCircle, FiUser, FiCalendar,
  FiFileText, FiSun, FiMoon
} from 'react-icons/fi';
import { BiLeaf } from 'react-icons/bi';
import { MdLocalHospital } from 'react-icons/md';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { gardenAPI } from '../../services/api';
import formatClassName from '../../utils/formatClassName';
import './GardenPage.css';

const GardenPage = () => {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPlant, setEditingPlant] = useState(null);
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState('');
  const [filter, setFilter] = useState('all');

  const { logout, user } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    loadPlants();
  }, []);

  const loadPlants = async () => {
    setLoading(true);
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'monitoring': return <FiEye className="status-icon monitoring" />;
      case 'treating': return <MdLocalHospital className="status-icon treating" />;
      case 'recovered': return <FiCheckCircle className="status-icon recovered" />;
      default: return <BiLeaf className="status-icon default" />;
    }
  };

  const filteredPlants = filter === 'all' 
    ? plants 
    : plants.filter(p => p.status === filter);

  const stats = {
    total: plants.length,
    monitoring: plants.filter(p => p.status === 'monitoring').length,
    treating: plants.filter(p => p.status === 'treating').length,
    recovered: plants.filter(p => p.status === 'recovered').length,
  };

  return (
    <div className={`garden-page ${isDark ? 'dark' : 'light'}`}>
      {/* Sidebar */}
      <aside className="garden-sidebar">
        <div className="sidebar-header">
          <BiLeaf className="sidebar-logo" />
          <h1>My Garden</h1>
        </div>

        <nav className="sidebar-nav">
          <button onClick={() => navigate('/')} className="nav-item">
            <FiHome /> Dashboard
          </button>
          <button onClick={loadPlants} className="nav-item">
            <FiRefreshCw /> Refresh
          </button>
          <motion.button 
            onClick={toggleTheme} 
            className="nav-item theme-toggle"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isDark ? <FiSun /> : <FiMoon />} 
            {isDark ? 'Light Mode' : 'Dark Mode'}
          </motion.button>
          <button onClick={logout} className="nav-item logout">
            <FiLogOut /> Logout
          </button>
        </nav>

        <div className="sidebar-stats">
          <h3>Statistics</h3>
          <div className={`stat-item ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
            <span><BiLeaf className="stat-icon" /> Total Plants</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className={`stat-item ${filter === 'monitoring' ? 'active' : ''}`} onClick={() => setFilter('monitoring')}>
            <span><FiEye className="stat-icon yellow" /> Monitoring</span>
            <span className="stat-value yellow">{stats.monitoring}</span>
          </div>
          <div className={`stat-item ${filter === 'treating' ? 'active' : ''}`} onClick={() => setFilter('treating')}>
            <span><MdLocalHospital className="stat-icon orange" /> Treating</span>
            <span className="stat-value orange">{stats.treating}</span>
          </div>
          <div className={`stat-item ${filter === 'recovered' ? 'active' : ''}`} onClick={() => setFilter('recovered')}>
            <span><FiCheckCircle className="stat-icon green" /> Recovered</span>
            <span className="stat-value green">{stats.recovered}</span>
          </div>
        </div>

        <div className="sidebar-user">
          <FiUser className="user-icon" />
          <span>{user?.username || user?.email}</span>
        </div>
      </aside>

      {/* Main Content */}
      <main className="garden-main">
        <header className="garden-header">
          <div className="header-left">
            <h2><BiLeaf className="header-icon" /> Your Plant Collection</h2>
            <p>Track and manage your diagnosed plants</p>
          </div>
          <div className="header-right">
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Plants ({stats.total})</option>
              <option value="monitoring">Monitoring ({stats.monitoring})</option>
              <option value="treating">Treating ({stats.treating})</option>
              <option value="recovered">Recovered ({stats.recovered})</option>
            </select>
          </div>
        </header>

        <div className="garden-content">
          {loading ? (
            <div className="garden-loading">
              <div className="spinner"></div>
              <p>Loading your garden...</p>
            </div>
          ) : filteredPlants.length === 0 ? (
            <motion.div 
              className="garden-empty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <BiLeaf className="empty-icon" />
              <h3>No plants {filter !== 'all' ? `with "${filter}" status` : 'in your garden yet'}</h3>
              <p>Diagnose plants and save them to track their health!</p>
              <button onClick={() => navigate('/')} className="btn btn-primary">
                Go to Dashboard
              </button>
            </motion.div>
          ) : (
            <div className="plants-grid">
              <AnimatePresence>
                {filteredPlants.map((plant, index) => (
                  <motion.div
                    key={plant.id}
                    className="plant-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -5, boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}
                  >
                    <div className="plant-header">
                      <div className="plant-icon">{getStatusIcon(plant.status)}</div>
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
                          <FiEdit2 />
                        </button>
                        <button 
                          onClick={() => handleDelete(plant.id)}
                          className="icon-btn delete"
                          title="Delete"
                        >
                          <FiTrash2 />
                        </button>
                      </div>
                    </div>

                    <div className="plant-disease">
                      <strong>Disease:</strong> 
                      <span>{formatClassName(plant.disease_name)}</span>
                    </div>

                    <div className="plant-confidence">
                      <div className="confidence-label">
                        <span>Confidence</span>
                        <span>{(plant.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="confidence-bar">
                        <motion.div 
                          className="confidence-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${plant.confidence * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.05 }}
                        />
                      </div>
                    </div>

                    {editingPlant === plant.id ? (
                      <motion.div 
                        className="edit-section"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                      >
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
                            className="btn btn-primary"
                          >
                            Save Changes
                          </button>
                          <button 
                            onClick={() => setEditingPlant(null)}
                            className="btn btn-secondary"
                          >
                            Cancel
                          </button>
                        </div>
                      </motion.div>
                    ) : (
                      <>
                        {plant.notes && (
                          <div className="plant-notes">
                            <strong><FiFileText className="notes-icon" /> Notes:</strong>
                            <p>{plant.notes}</p>
                          </div>
                        )}
                        <div className="plant-date">
                          <FiCalendar className="date-icon" />
                          {new Date(plant.diagnosed_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </div>
                      </>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default GardenPage;
