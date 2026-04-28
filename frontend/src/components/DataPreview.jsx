import React, { useEffect, useState } from 'react';
import { useUpload } from '../hooks/useUpload';

export default function DataPreview({ fileId }) {
  const { previewFile, isLoading, error } = useUpload();
  const [previewData, setPreviewData] = useState(null);
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (fileId) {
      loadPreview();
    }
  }, [fileId]);

  const loadPreview = async () => {
    try {
      const response = await previewFile(fileId);
      setPreviewData(response.data || []);
      if (response.data && response.data.length > 0) {
        setColumns(Object.keys(response.data[0]));
      }
    } catch (err) {
      console.error('Failed to load preview:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <h2 className="card-title">Data Preview</h2>
        <div className="flex-center" style={{ padding: '32px' }}>
          <span className="loading">
            <span className="spinner"></span>
            Loading preview...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 className="card-title">Data Preview</h2>
        <div className="alert alert-danger">
          Failed to load preview: {error}
        </div>
      </div>
    );
  }

  if (!previewData || previewData.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Data Preview</h2>
        <div className="text-center text-muted">
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title">Data Preview</h2>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {columns.slice(0, 8).map(col => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previewData.slice(0, 5).map((row, idx) => (
              <tr key={idx}>
                {columns.slice(0, 8).map(col => (
                  <td key={`${idx}-${col}`}>
                    {typeof row[col] === 'number'
                      ? row[col].toFixed(2)
                      : String(row[col] || 'N/A').substring(0, 30)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-muted" style={{ marginTop: '12px' }}>
        Showing {Math.min(5, previewData.length)} of {previewData.length} rows,
        {columns.length > 8 ? ` showing first 8 of ${columns.length} columns` : ' all columns'}
      </p>
    </div>
  );
}