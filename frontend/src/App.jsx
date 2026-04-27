import React, { useState } from 'react';
import './styles/global.css';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';

function App() {
  const [appState, setAppState] = useState({
    currentStep: 'home', // 'home' or 'dashboard'
    fileId: null,
    fileName: null,
    taskType: null,
    targetColumn: null,
    validationStatus: null,
    modelId: null,
    metrics: null,
  });

  const handleFileUpload = (fileId, fileName) => {
    setAppState(prev => ({
      ...prev,
      fileId,
      fileName,
      currentStep: 'dashboard',
    }));
  };

  const handleTaskSelection = (taskType) => {
    setAppState(prev => ({
      ...prev,
      taskType,
    }));
  };

  const handleTargetSelection = (targetColumn) => {
    setAppState(prev => ({
      ...prev,
      targetColumn,
    }));
  };

  const handleValidation = (status) => {
    setAppState(prev => ({
      ...prev,
      validationStatus: status,
    }));
  };

  const handleTrainingComplete = (modelId, metrics) => {
    setAppState(prev => ({
      ...prev,
      modelId,
      metrics,
    }));
  };

  const handleReset = () => {
    setAppState({
      currentStep: 'home',
      fileId: null,
      fileName: null,
      taskType: null,
      targetColumn: null,
      validationStatus: null,
      modelId: null,
      metrics: null,
    });
  };

  return (
    <div className="app-container">
      {appState.currentStep === 'home' ? (
        <Home onFileUpload={handleFileUpload} />
      ) : (
        <Dashboard
          appState={appState}
          onTaskSelection={handleTaskSelection}
          onTargetSelection={handleTargetSelection}
          onValidation={handleValidation}
          onTrainingComplete={handleTrainingComplete}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

export default App;