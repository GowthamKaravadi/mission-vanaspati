import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUser, FiLogOut } from 'react-icons/fi';
import { BiLeaf } from 'react-icons/bi';
import { MdAdminPanelSettings } from 'react-icons/md';
import './ProfileDropdown.css';

const ProfileDropdown = ({ user, isAdmin, onLogout, onAdminClick, onMyGardenClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMenuClick = (action) => {
    action();
    setIsOpen(false);
  };

  return (
    <div className="profile-dropdown" ref={dropdownRef}>
      <motion.button
        className="profile-btn"
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title={user?.username}
      >
        <FiUser className="profile-icon" />
        <span className="username-text">{user?.username}</span>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="dropdown-menu"
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div className="dropdown-header">
              <div className="dropdown-user-icon">
                <FiUser />
              </div>
              <div className="dropdown-user-info">
                <p className="dropdown-username">{user?.username}</p>
                <p className="dropdown-email">{user?.email || 'User'}</p>
              </div>
            </div>

            <div className="dropdown-divider"></div>

            <motion.button
              className="dropdown-item"
              onClick={() => handleMenuClick(onMyGardenClick)}
              whileHover={{ x: 4 }}
              transition={{ duration: 0.2 }}
            >
              <BiLeaf className="dropdown-icon" />
              <span>My Garden</span>
            </motion.button>

            {isAdmin && (
              <motion.button
                className="dropdown-item admin-item"
                onClick={() => handleMenuClick(onAdminClick)}
                whileHover={{ x: 4 }}
                transition={{ duration: 0.2 }}
              >
                <MdAdminPanelSettings className="dropdown-icon" />
                <span>Admin Panel</span>
              </motion.button>
            )}

            <div className="dropdown-divider"></div>

            <motion.button
              className="dropdown-item logout-item"
              onClick={() => handleMenuClick(onLogout)}
              whileHover={{ x: 4 }}
              transition={{ duration: 0.2 }}
            >
              <FiLogOut className="dropdown-icon" />
              <span>Logout</span>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProfileDropdown;
