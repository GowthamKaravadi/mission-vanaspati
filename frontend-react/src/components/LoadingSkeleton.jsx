import { motion } from 'framer-motion';
import './LoadingSkeleton.css';

export const CardSkeleton = () => (
  <motion.div 
    className="skeleton-card"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <div className="skeleton skeleton-header"></div>
    <div className="skeleton skeleton-text"></div>
    <div className="skeleton skeleton-text short"></div>
  </motion.div>
);

export const ResultSkeleton = () => (
  <motion.div 
    className="skeleton-result"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0 }}
  >
    <div className="skeleton skeleton-title"></div>
    <div className="skeleton skeleton-bar"></div>
    <div className="skeleton skeleton-text"></div>
    <div className="skeleton skeleton-text"></div>
    <div className="skeleton skeleton-text short"></div>
  </motion.div>
);

export const TableSkeleton = () => (
  <div className="skeleton-table">
    {[...Array(5)].map((_, i) => (
      <div key={i} className="skeleton-row">
        <div className="skeleton skeleton-cell"></div>
        <div className="skeleton skeleton-cell"></div>
        <div className="skeleton skeleton-cell"></div>
        <div className="skeleton skeleton-cell"></div>
      </div>
    ))}
  </div>
);
