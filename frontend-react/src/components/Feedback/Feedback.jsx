import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import axiosInstance from '../../services/api';
import './Feedback.css';

const Feedback = ({ onClose }) => {
  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    type: 'bug'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.subject.trim() || !formData.message.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const response = await axiosInstance.post('/feedback', null, {
        params: {
          subject: formData.subject,
          message: formData.message,
          type: formData.type
        }
      });

      if (response.data.status === 'success') {
        toast.success('Feedback submitted successfully! Thank you for helping us improve.');
        setFormData({ subject: '', message: '', type: 'bug' });
        setTimeout(() => onClose(), 1500);
      }
    } catch (error) {
      console.error('Feedback submission error:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <AnimatePresence>
      <motion.div
        className="feedback-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="feedback-modal"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="feedback-header">
            <h2>Report Feedback</h2>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>

          <form onSubmit={handleSubmit} className="feedback-form">
            <div className="form-group">
              <label htmlFor="type">Feedback Type</label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleChange}
                required
              >
                <option value="bug">BUG REPORT</option>
                <option value="feature">FEATURE REQUEST</option>
                <option value="general">GENERAL FEEDBACK</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="subject">Subject</label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                placeholder="Brief description of the issue"
                maxLength={100}
                required
              />
              <small>{formData.subject.length}/100</small>
            </div>

            <div className="form-group">
              <label htmlFor="message">Message</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                placeholder="Provide detailed information about the bug or feedback..."
                rows={6}
                maxLength={1000}
                required
              />
              <small>{formData.message.length}/1000</small>
            </div>

            <div className="feedback-actions">
              <button
                type="button"
                className="btn-cancel"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Feedback;
