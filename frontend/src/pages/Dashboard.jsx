import React, { useState, useEffect } from 'react';
import DataPreview from '../components/DataPreview';
import TaskSelector from '../components/TaskSelector';
import TargetSelector from '../components/TargetSelector';
import TrainButton from '../components/TrainButton';
import MetricsDisplay from '../components/MetricsDisplay';
import ModelDownload from '../components/ModelDownload';
import { getTaskTypeName } from '../utils/formatters';

export default function Dashboard({
  appState,
  onTaskSelection,
  onTargetSelection,
  onValidation,
  onTrainingComplete,
  onReset,
}) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // Define workflow steps
  const steps = [
    { id: 1, label: 'Preview Data', status: appState.fileId ? 'completed' : 'pending' },
    { id: 2, label: 'Select Task', status: appState.taskType ? 'completed' : appState.fileId ? 'active' : 'pending' },
    { id: 3, label: 'Target Column', status: appState.targetColumn && appState.taskType !== 'clustering' ? 'completed' : (appState.taskType ? 'active' : 'pending') },
    { id: 4, label: 'Train Model', status: appState.metrics ? 'completed' : appState.targetColumn || appState.taskType === 'clustering' ? 'active' : 'pending' },
    { id: 5, label: 'Review Results', status: appState.modelId ? 'completed' : appState.metrics ? 'active' : 'pending' },
  ];

  useEffect(() => {
    // Update current step based on state
    if (appState.metrics) {
      setCurrentStepIndex(4);
    } else if (appState.targetColumn || appState.taskType === 'clustering') {
      setCurrentStepIndex(3);
    } else if (appState.taskType) {
      setCurrentStepIndex(2);
    } else if (appState.fileId) {
      setCurrentStepIndex(1);
    } else {
      setCurrentStepIndex(0);
    }
  }, [appState]);

  return (
    <div className="app-container">
      <div className="page-header">
        <div className="container">
          <div className="flex-between" style={{ marginBottom: '16px' }}>
            <div>
              <h1>🎯 ML Training Dashboard</h1>
              <p>Dataset: <strong>{appState.fileName}</strong></p>
            </div>
            <button className="btn btn-secondary" onClick={onReset}>
              ← Start Over
            </button>
          </div>
        </div>
      </div>

      <div className="container">
        {/* Step Indicator */}
        <div className="step-indicator" style={{ marginBottom: '32px' }}>
          {steps.map((step, idx) => (
            <div
              key={step.id}
              className={`step ${step.status === 'completed' ? 'completed' : step.status === 'active' ? 'active' : ''}`}
              onClick={() => {
                if (step.status === 'completed' || step.status === 'active') {
                  setCurrentStepIndex(idx);
                }
              }}
              style={{ cursor: step.status === 'completed' || step.status === 'active' ? 'pointer' : 'default' }}
            >
              <div className="step-circle">
                {step.status === 'completed' ? '✓' : step.id}
              </div>
              <div className="step-label">{step.label}</div>
            </div>
          ))}
        </div>

        {/* Step 1: Preview Data */}
        {appState.fileId && (
          <div className="grid mb-8">
            <DataPreview fileId={appState.fileId} />
          </div>
        )}

        {/* Step 2: Select Task Type */}
        <div className="mb-8">
          <TaskSelector
            selectedTask={appState.taskType}
            onTaskSelect={onTaskSelection}
            disabled={!appState.fileId}
          />
        </div>

        {/* Step 3: Select Target Column (if supervised learning) */}
        {appState.taskType && appState.taskType !== 'clustering' && (
          <div className="mb-8">
            <TargetSelector
              fileId={appState.fileId}
              taskType={appState.taskType}
              selectedTarget={appState.targetColumn}
              onTargetSelect={onTargetSelection}
              disabled={!appState.fileId}
            />
          </div>
        )}

        {appState.taskType === 'clustering' && (
          <div className="mb-8">
            <TargetSelector
              fileId={appState.fileId}
              taskType={appState.taskType}
              selectedTarget={null}
              onTargetSelect={() => {}}
              disabled={false}
            />
          </div>
        )}

        {/* Step 4: Train Model */}
        <div className="mb-8">
          <TrainButton
            fileId={appState.fileId}
            taskType={appState.taskType}
            targetColumn={appState.targetColumn}
            onTrainingComplete={onTrainingComplete}
            disabled={!appState.fileId || !appState.taskType}
          />
        </div>

        {/* Step 5: Results */}
        {appState.metrics && (
          <div className="grid gap-6">
            <MetricsDisplay metrics={appState.metrics.metrics} taskType={appState.taskType} />

            <ModelDownload
              modelId={appState.modelId}
              onModelSaved={(data) => {
                console.log('Model saved:', data);
              }}
            />

            <div className="card">
              <h2 className="card-title">📝 Summary</h2>

              <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '14px' }}>
                  <div>
                    <p style={{ color: '#6b7280', marginBottom: '4px' }}>Task Type</p>
                    <p style={{ fontWeight: '600' }}>{getTaskTypeName(appState.taskType)}</p>
                  </div>
                  {appState.targetColumn && (
                    <div>
                      <p style={{ color: '#6b7280', marginBottom: '4px' }}>Target Column</p>
                      <p style={{ fontWeight: '600' }}>{appState.targetColumn}</p>
                    </div>
                  )}
                  <div>
                    <p style={{ color: '#6b7280', marginBottom: '4px' }}>Best Algorithm</p>
                    <p style={{ fontWeight: '600' }}>
                      {appState.metrics.metrics.best_algorithm || appState.metrics.bestAlgorithm || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p style={{ color: '#6b7280', marginBottom: '4px' }}>Model ID</p>
                    <p style={{ fontWeight: '600', fontFamily: 'monospace', fontSize: '12px' }}>
                      {appState.modelId}
                    </p>
                  </div>
                </div>
              </div>

              <div className="alert alert-info">
                <strong>Next Steps:</strong> Download your model and use it for predictions on new data. The model includes all preprocessing steps applied during training.
              </div>
            </div>
          </div>
        )}

        {/* Empty state when no metrics yet */}
        {!appState.metrics && appState.taskType && (appState.targetColumn || appState.taskType === 'clustering') && (
          <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
            <p style={{ fontSize: '16px', color: '#6b7280' }}>
              Ready to train? Click the "Start Training" button above to begin the ML pipeline.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}