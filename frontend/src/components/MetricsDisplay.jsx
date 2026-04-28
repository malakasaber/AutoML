import React from 'react';
import { formatPercent, formatDecimal, getTaskTypeName } from '../utils/formatters';

export default function MetricsDisplay({ metrics, visualizations = {}, taskType }) {
  if (!metrics) {
    return null;
  }

  const renderMetric = (label, value) => {
    if (value === null || value === undefined) return null;

    // Determine if it should be shown as percentage
    const isPercentage = ['accuracy', 'precision', 'recall', 'f1'].includes(label.toLowerCase());
    const displayValue = isPercentage ? formatPercent(value) : formatDecimal(value);

    return (
      <div
        key={label}
        style={{
          padding: '12px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
          {label}
        </div>
        <div
          style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2563eb',
          }}
        >
          {displayValue}
        </div>
      </div>
    );
  };

  const renderClassificationMetrics = () => {
    const { accuracy, precision, recall, f1_score, confusion_matrix } = metrics;

    return (
      <div>
        <div className="grid grid-4" style={{ marginBottom: '24px' }}>
          {renderMetric('Accuracy', accuracy)}
          {renderMetric('Precision', precision)}
          {renderMetric('Recall', recall)}
          {renderMetric('F1 Score', f1_score)}
        </div>

        {confusion_matrix && (
          <div style={{ marginTop: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Confusion Matrix
            </h3>
            <div className="table-wrapper">
              <table style={{ fontSize: '13px' }}>
                <thead>
                  <tr>
                    <th></th>
                    <th>Predicted Negative</th>
                    <th>Predicted Positive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Actual Negative</strong></td>
                    <td>{confusion_matrix[0]?.[0] || 'N/A'}</td>
                    <td>{confusion_matrix[0]?.[1] || 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Actual Positive</strong></td>
                    <td>{confusion_matrix[1]?.[0] || 'N/A'}</td>
                    <td>{confusion_matrix[1]?.[1] || 'N/A'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRegressionMetrics = () => {
    const { mae, mse, rmse, r2_score } = metrics;

    return (
      <div className="grid grid-4">
        {renderMetric('MAE', mae)}
        {renderMetric('MSE', mse)}
        {renderMetric('RMSE', rmse)}
        {renderMetric('R² Score', r2_score)}
      </div>
    );
  };

  const renderClusteringMetrics = () => {
    const { silhouette_score, n_clusters } = metrics;

    return (
      <div className="grid grid-3">
        {renderMetric('Silhouette Score', silhouette_score)}
        {renderMetric('Number of Clusters', n_clusters)}
      </div>
    );
  };

  const renderVisualizations = () => {
    const items = [];

    if (taskType === 'classification' && visualizations.confusion_matrix) {
      items.push(
        <div key="confusion_matrix" style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
            Confusion Matrix Visualization
          </h3>
          <div style={{ overflow: 'auto', borderRadius: '12px', border: '1px solid #e5e7eb', padding: '12px', backgroundColor: '#ffffff' }}>
            <img
              src={`data:image/png;base64,${visualizations.confusion_matrix}`}
              alt="Confusion Matrix"
              style={{ width: '100%', height: 'auto', display: 'block' }}
            />
          </div>
        </div>
      );
    }

    if (taskType === 'regression' && visualizations.actual_vs_pred) {
      items.push(
        <div key="actual_vs_pred" style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
            Actual vs Predicted Visualization
          </h3>
          <div style={{ overflow: 'auto', borderRadius: '12px', border: '1px solid #e5e7eb', padding: '12px', backgroundColor: '#ffffff' }}>
            <img
              src={`data:image/png;base64,${visualizations.actual_vs_pred}`}
              alt="Actual vs Predicted"
              style={{ width: '100%', height: 'auto', display: 'block' }}
            />
          </div>
        </div>
      );
    }

    if (taskType === 'clustering' && visualizations.silhouette) {
      items.push(
        <div key="silhouette" style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
            Silhouette Plot Visualization
          </h3>
          <div style={{ overflow: 'auto', borderRadius: '12px', border: '1px solid #e5e7eb', padding: '12px', backgroundColor: '#ffffff' }}>
            <img
              src={`data:image/png;base64,${visualizations.silhouette}`}
              alt="Silhouette Plot"
              style={{ width: '100%', height: 'auto', display: 'block' }}
            />
          </div>
        </div>
      );
    }

    return items.length > 0 ? items : null;
  };

  return (
    <div className="card">
      <h2 className="card-title">📊 Model Performance Metrics</h2>

      <div style={{ marginBottom: '16px', padding: '12px 16px', backgroundColor: 'rgba(37, 99, 235, 0.1)', borderRadius: '6px' }}>
        <p style={{ margin: 0, fontSize: '14px' }}>
          <strong>Task Type:</strong> {getTaskTypeName(taskType)} | <strong>Model:</strong> {metrics.best_algorithm || 'Best Model'}
        </p>
      </div>

      {taskType === 'classification' && renderClassificationMetrics()}
      {taskType === 'regression' && renderRegressionMetrics()}
      {taskType === 'clustering' && renderClusteringMetrics()}

      {metrics.algorithms && metrics.algorithms.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
            Trained Algorithms
          </h3>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Algorithm</th>
                  <th>Primary Metric</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {metrics.algorithms.map((algo, idx) => (
                  <tr key={idx}>
                    <td>{algo.name || algo}</td>
                    <td>{formatDecimal(algo.score || 0)}</td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          backgroundColor: algo.name === metrics.best_algorithm ? 'rgba(22, 163, 74, 0.1)' : 'rgba(107, 114, 128, 0.1)',
                          color: algo.name === metrics.best_algorithm ? '#15803d' : '#6b7280',
                        }}
                      >
                        {algo.name === metrics.best_algorithm ? '✓ Best' : 'Trained'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {renderVisualizations()}
    </div>
  );
}