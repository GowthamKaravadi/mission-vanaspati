/**
 * Formats internal disease class names into user-friendly display names.
 * 
 * Examples:
 *   "Pepper_bell___Bacterial_spot" → "Pepper Bell - Bacterial Spot"
 *   "Tomato___Late_blight" → "Tomato - Late Blight"
 *   "Corn___maize__Common_rust_" → "Corn (Maize) - Common Rust"
 *   "Apple___healthy" → "Apple - Healthy"
 */

export const formatClassName = (className) => {
  if (!className) return '';
  
  let formatted = className;
  
  // Handle "maize" subcategory: Corn___maize__Disease → Corn (Maize) - Disease
  if (formatted.includes('___maize__')) {
    formatted = formatted.replace('___maize__', ' (Maize) - ');
  }
  // Handle "including_sour" for cherries: Cherry___including_sour__Disease → Cherry (Sour) - Disease
  else if (formatted.includes('___including_sour__')) {
    formatted = formatted.replace('___including_sour__', ' (Sour) - ');
  }
  // Standard format: Plant___Disease → Plant - Disease
  else {
    formatted = formatted.replace(/___/g, ' - ');
  }
  
  // Replace underscores with spaces
  formatted = formatted.replace(/_/g, ' ');
  
  // Remove trailing/leading spaces
  formatted = formatted.trim();
  
  // Remove trailing dashes or spaces
  formatted = formatted.replace(/\s*-\s*$/, '');
  
  // Capitalize first letter of each word
  formatted = formatted
    .split(' ')
    .map(word => {
      if (word.length === 0) return word;
      // Keep parentheses intact
      if (word.startsWith('(')) {
        return '(' + word.slice(1, 2).toUpperCase() + word.slice(2).toLowerCase();
      }
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
  
  // Fix common abbreviations and proper nouns
  formatted = formatted
    .replace(/\bYlcv\b/gi, 'YLCV')
    .replace(/\bTmv\b/gi, 'TMV')
    .replace(/\bCmv\b/gi, 'CMV');
  
  return formatted;
};

/**
 * Extracts just the plant name from the class name.
 * "Tomato___Late_blight" → "Tomato"
 */
export const getPlantName = (className) => {
  if (!className) return '';
  const parts = className.split('___');
  return parts[0].replace(/_/g, ' ').trim();
};

/**
 * Extracts just the disease/condition name from the class name.
 * "Tomato___Late_blight" → "Late Blight"
 */
export const getDiseaseName = (className) => {
  if (!className) return '';
  const parts = className.split('___');
  if (parts.length < 2) return 'Unknown';
  
  let disease = parts[1];
  
  // Handle maize subcategory
  if (disease.startsWith('maize__')) {
    disease = disease.replace('maize__', '');
  }
  // Handle sour cherry subcategory
  if (disease.startsWith('including_sour__')) {
    disease = disease.replace('including_sour__', '');
  }
  
  return disease
    .replace(/_/g, ' ')
    .trim()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

export default formatClassName;
