import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { FiUpload, FiAlertTriangle } from 'react-icons/fi';
import './Dashboard.css';

const ImageUpload = ({ mode, onFilesSelected }) => {
  const [previews, setPreviews] = useState([]);

  const validateImage = (file) => {
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error(`${file.name} is too large. Max size is 10MB.`);
      return false;
    }

    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      toast.error(`${file.name} is not a valid image format. Use JPG or PNG.`);
      return false;
    }

    return true;
  };

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(({ file, errors }) => {
        errors.forEach(error => {
          if (error.code === 'file-too-large') {
            toast.error(`${file.name} is too large`);
          } else if (error.code === 'file-invalid-type') {
            toast.error(`${file.name} is not a valid image`);
          }
        });
      });
    }

    // Validate accepted files
    const validFiles = acceptedFiles.filter(validateImage);
    
    if (validFiles.length === 0) return;

    const newPreviews = validFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36)
    }));
    
    if (mode === 'single') {
      setPreviews([newPreviews[0]]);
      onFilesSelected([newPreviews[0].file]);
    } else {
      setPreviews(prev => [...prev, ...newPreviews]);
      onFilesSelected([...previews.map(p => p.file), ...newPreviews.map(p => p.file)]);
    }
  }, [mode, onFilesSelected, previews]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpeg', '.jpg'],
      'image/png': ['.png']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: mode === 'batch'
  });

  const removeImage = (id) => {
    const newPreviews = previews.filter(p => p.id !== id);
    setPreviews(newPreviews);
    onFilesSelected(newPreviews.map(p => p.file));
  };

  const clearAll = () => {
    previews.forEach(p => URL.revokeObjectURL(p.preview));
    setPreviews([]);
    onFilesSelected([]);
  };

  return (
    <div className="upload-container">
      {previews.length === 0 ? (
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          <div className="upload-icon"><FiUpload /></div>
          <h3>
            {isDragActive ? 'Drop the images here' : 
             mode === 'single' ? 'Upload Plant Image' : 'Upload Plant Images'}
          </h3>
          <p>Drag and drop or click to select</p>
          <span className="file-types">Supported: JPG, PNG (Max 10MB)</span>
          <span className="file-warning"><FiAlertTriangle /> Please upload only plant leaf images</span>
        </div>
      ) : (
        <>
          {mode === 'batch' && previews.length > 0 && (
            <div className="batch-header">
              <h3>{previews.length} image(s) selected</h3>
              <button onClick={clearAll} className="btn-clear">Clear All</button>
            </div>
          )}
          
          <div className={mode === 'single' ? 'preview-single' : 'preview-grid'}>
            {previews.map((item) => (
              <div key={item.id} className="preview-item">
                <img src={item.preview} alt="Preview" />
                <button 
                  onClick={() => removeImage(item.id)} 
                  className="btn-remove"
                  aria-label="Remove image"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          {mode === 'batch' && (
            <div {...getRootProps()} className="dropzone-small">
              <input {...getInputProps()} />
              <p>+ Add more images</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ImageUpload;
