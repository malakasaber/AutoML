import React, { useState } from 'react';
import * as modelApi from '../api/modelApi';

export default function ModelDownload({ modelId, onModelSaved }) {
  const [selectedFormat, setSelectedFormat] = useState('joblib');
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadComplete, setDownloadComplete] = useState(false);

  const handleDownload = async () => {
    if (!modelId) {
      setError('Model ID is missing');
      return;
    }

    setIsDownloading(true);
    setError(null);
    setDownloadComplete(false);

    try {
      await modelApi.downloadModelFile(modelId, selectedFormat);
      setDownloadComplete(true);

      if (onModelSaved) {
        onModelSaved({
          modelId,
          format: selectedFormat,
          timestamp: new Date().toISOString(),
        });
      }

      // Reset after 3 seconds
      setTimeout(() => setDownloadComplete(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to download model');
      console.error('Download error:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Save Model</h2>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {downloadComplete && (
        <div className="alert alert-success">
          ✓ Model downloaded successfully! Check your downloads folder.
        </div>
      )}

      <div className="form-group">
        <label>Choose serialization format:</label>
        <div className="radio-group">
          <div className="radio-item">
            <input
              type="radio"
              id="joblib"
              name="format"
              value="joblib"
              checked={selectedFormat === 'joblib'}
              onChange={(e) => setSelectedFormat(e.target.value)}
              disabled={isDownloading}
            />
            <label htmlFor="joblib">
              <strong>Joblib</strong> (Recommended)
            </label>
          </div>
          <p style={{ margin: 0, marginLeft: '26px', fontSize: '13px', color: '#6b7280' }}>
            Better for large models, preserves all Python objects
          </p>

          <div className="radio-item" style={{ marginTop: '12px' }}>
            <input
              type="radio"
              id="pickle"
              name="format"
              value="pickle"
              checked={selectedFormat === 'pickle'}
              onChange={(e) => setSelectedFormat(e.target.value)}
              disabled={isDownloading}
            />
            <label htmlFor="pickle">
              <strong>Pickle</strong> (Standard)
            </label>
          </div>
          <p style={{ margin: 0, marginLeft: '26px', fontSize: '13px', color: '#6b7280' }}>
            Standard Python serialization format
          </p>
        </div>
      </div>

      <button
        className="btn btn-primary btn-large btn-block"
        onClick={handleDownload}
        disabled={isDownloading || !modelId}
        style={{ marginTop: '16px' }}
      >
        {isDownloading ? (
          <>
            <span className="spinner"></span>
            Downloading...
          </>
        ) : (
          `Download as ${selectedFormat === 'joblib' ? '.joblib' : '.pkl'}`
        )}
      </button>

      <p className="text-muted" style={{ marginTop: '12px' }}>
        The model file includes the trained model and preprocessing pipeline
      </p>
    </div>
  );
}