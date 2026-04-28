import React, { useRef, useState } from 'react';
import { useUpload } from '../hooks/useUpload';

export default function FileUpload({ onFileUpload }) {
  const { uploadFile, isLoading, error } = useUpload();
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleFileSelect = async (file) => {
    const validTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const isValidType = validTypes.includes(file.type) || file.name.endsWith('.csv') || file.name.endsWith('.xlsx');

    if (!isValidType) {
      alert('Please upload a CSV or XLSX file or XLS file.');
      return;
    }

    try {
      setFileName(file.name);
      const response = await uploadFile(file);
      onFileUpload(response.file_id, file.name);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="card">
      <h2 className="card-title">📁 Upload Dataset</h2>

      {error && (
        <div className="alert alert-danger">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div
        className={`file-upload-area ${dragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex="0"
        onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      >
        <div className="file-upload-icon">📤</div>
        <div className="file-upload-text">
          {isLoading ? 'Uploading...' : 'Drag and drop your file here'}
        </div>
        <div className="file-upload-subtext">
          or click to browse (CSV, XLSX, XLS)
        </div>

        {fileName && (
          <div style={{ marginTop: '12px', fontSize: '14px', color: '#16a34a', fontWeight: '500' }}>
            ✓ {fileName}
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        onChange={handleInputChange}
        accept=".csv,.xlsx,.xls"
        disabled={isLoading}
      />

      <p className="text-muted" style={{ marginTop: '12px' }}>
        Supported formats: CSV (.csv), Excel (.xlsx), Excel 97-2003 (.xls)
      </p>
    </div>
  );
}