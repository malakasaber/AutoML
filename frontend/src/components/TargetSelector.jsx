import React, { useEffect, useState } from 'react';
import { useUpload } from '../hooks/useUpload';

export default function TargetSelector({ fileId, taskType, selectedTarget, onTargetSelect, disabled }) {
  const { getTargetColumns, isLoading, error } = useUpload();
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (!fileId || taskType === 'clustering') return;
    loadTargetColumns();
    }, [fileId, taskType]);

  const loadTargetColumns = async () => {
    try {
        const response = await getTargetColumns(fileId);
        setColumns(response.suggestions || []);
    } catch (err) {
        console.error('Failed to load target columns:', err);
    }
    };

  // For clustering, no target column is needed
  if (taskType === 'clustering') {
    return (
      <div className="card">
        <h2 className="card-title">✓ Clustering Task</h2>
        <div className="alert alert-info">
          No target column needed for clustering. The model will group similar data points automatically.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title">Select Target Column</h2>

      {error && (
        <div className="alert alert-danger">
          Failed to load columns: {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex-center" style={{ padding: '32px' }}>
          <span className="loading">
            <span className="spinner"></span>
            Loading columns...
          </span>
        </div>
      ) : (
        <div className="form-group">
          <label htmlFor="target-select">
            Choose the target column {taskType === 'classification' ? '(discrete values)' : '(continuous values)'}
          </label>

          <div className="select-wrapper">
            <select
              id="target-select"
              value={selectedTarget || ''}
              onChange={(e) => onTargetSelect(e.target.value)}
              disabled={disabled || columns.length === 0}
            >
              <option value="">-- Select a column --</option>
              {columns.map(col => (
                <option key={col.column} value={col.column}>
                    {col.column} ({col.type}, {col.unique_values})
                </option>
                ))}
            </select>
          </div>

          {columns.length === 0 && (
            <p className="text-muted" style={{ marginTop: '8px' }}>
              No columns available in the dataset
            </p>
          )}

          {selectedTarget && (
            <div style={{ marginTop: '12px', fontSize: '13px', color: '#16a34a' }}>
              ✓ Target column selected: <strong>{selectedTarget}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
}