import React from 'react';
import FileUpload from '../components/FileUpload';

export default function Home({ onFileUpload }) {
  return (
    <div className="app-container">
      <div className="page-header">
        <div className="container">
          <h1>Machine Learning Pipeline</h1>
          <p>Upload your dataset and train powerful ML models with automated preprocessing and hyperparameter tuning</p>
        </div>
      </div>

      <div className="container">
        <div className="grid" style={{ width: '100%', padding: '0 20px' }}>
          <FileUpload onFileUpload={onFileUpload} />

          {/*
          <div className="card" style={{ backgroundColor: '#f0f9ff', borderColor: '#93c5fd' }}>
            <h2 className="card-title">📋 How it works</h2>
            <ol style={{ paddingLeft: '20px', margin: 0, fontSize: '14px', lineHeight: '1.8' }}>
              <li style={{ marginBottom: '8px' }}>
                <strong>Upload Dataset</strong> - CSV or XLSX format
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Select Task</strong> - Classification, Regression, or Clustering
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Choose Target</strong> - For supervised learning tasks
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Train Model</strong> - Automatic preprocessing & model selection
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Review Metrics</strong> - See detailed performance metrics
              </li>
              <li>
                <strong>Download Model</strong> - Save for future predictions
              </li>
            </ol>
          </div>

          <div className="card" style={{ backgroundColor: '#f0fdf4', borderColor: '#86efac' }}>
            <h2 className="card-title">✨ Features</h2>
            <ul style={{ paddingLeft: '20px', margin: 0, fontSize: '14px', lineHeight: '1.8' }}>
              <li style={{ marginBottom: '8px' }}>Automatic data preprocessing</li>
              <li style={{ marginBottom: '8px' }}>Multiple algorithm training</li>
              <li style={{ marginBottom: '8px' }}>Comprehensive metrics & visualizations</li>
              <li style={{ marginBottom: '8px' }}>Export models (Joblib/Pickle)</li>
              <li>Handles imbalanced data</li>
            </ul>
          </div>
          */}

        </div>
      </div>
    </div>
  );
}