import React, { useState } from 'react';
import { useUpload } from '../hooks/useUpload';
import { useTraining } from '../hooks/useTraining';

export default function TrainButton({
  fileId,
  taskType,
  targetColumn,
  onTrainingComplete,
  disabled,
}) {
  const { validateFile } = useUpload();
  const { trainModel, isLoading, error } = useTraining();
  const [validationError, setValidationError] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState(null);

  const handleTrain = async () => {
    setValidationError(null);
    setTrainingProgress('Validating dataset...');

    try {
      // Validate first
      const validationResponse = await validateFile(fileId, taskType, targetColumn);

      if (!validationResponse?.is_valid) {
        setValidationError(validationResponse?.message || 'Dataset validation failed');
        return;
      }

      setTrainingProgress('Training model... This may take a moment.');

      // Train the model
      const trainingResponse = await trainModel(fileId, taskType, targetColumn);

      if (trainingResponse.model_id) {
        setTrainingProgress('Training complete!');

        const report = trainingResponse.report || {};
        const reportMetrics = report.metrics || {};
        const bestModel = report.best_model || trainingResponse.model_name || report.model_name || '';
        const algorithms = (report.all_models_cv_scores && Object.entries(report.all_models_cv_scores).map(([name, score]) => ({
          name,
          score,
        }))) || [];

        const metricsData = {
          model_id: trainingResponse.model_id,
          taskType,
          metrics: {
            ...reportMetrics,
            best_algorithm: bestModel,
            algorithms,
          },
          bestAlgorithm: bestModel,
          visualizations: report.visualizations || {},
        };

        onTrainingComplete(trainingResponse.model_id, metricsData);
      }
    } catch (err) {
      console.error('Training error:', err);
      setValidationError(err.message || 'Training failed');
      setTrainingProgress(null);
    }
  };

  const isDisabled = disabled || !fileId || !taskType || (taskType !== 'clustering' && !targetColumn);

  return (
    <div className="card">
      <h2 className="card-title">Train Model</h2>

      {validationError && (
        <div className="alert alert-danger">
          {validationError}
        </div>
      )}

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {trainingProgress && (
        <div className="alert alert-info" style={{ marginBottom: '16px' }}>
          {trainingProgress}
        </div>
      )}

      <div style={{ marginBottom: '12px', fontSize: '14px', color: '#6b7280' }}>
        {!fileId && <p>Upload a dataset to start training</p>}
        {fileId && !taskType && <p>Select a task type (Classification, Regression, or Clustering)</p>}
        {fileId && taskType && taskType !== 'clustering' && !targetColumn && (
          <p>Select a target column for {taskType}</p>
        )}
        {fileId && taskType && (taskType === 'clustering' || targetColumn) && (
          <p>✓ Ready to train</p>
        )}
      </div>

      <button
        className="btn btn-success btn-large btn-block"
        onClick={handleTrain}
        disabled={isDisabled || isLoading}
        style={{ marginTop: '16px' }}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            Training in progress...
          </>
        ) : (
          'Start Training'
        )}
      </button>

      <p className="text-muted" style={{ marginTop: '12px' }}>
        The model will be automatically evaluated on a test set (20% of your data)
      </p>
    </div>
  );
}