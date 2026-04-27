import React from 'react';
import { getTaskTypeName } from '../utils/formatters';

export default function TaskSelector({ selectedTask, onTaskSelect, disabled }) {
  const tasks = [
    {
      id: 'classification',
      name: 'Classification',
      description: 'Predict discrete categories',
      icon: '📊',
    },
    {
      id: 'regression',
      name: 'Regression',
      description: 'Predict continuous values',
      icon: '📈',
    },
    {
      id: 'clustering',
      name: 'Clustering',
      description: 'Group similar data points',
      icon: '🎯',
    },
  ];

  return (
    <div className="card">
      <h2 className="card-title">🎯 Select Task Type</h2>

      <div className="grid grid-3">
        {tasks.map(task => (
          <div
            key={task.id}
            className="task-option"
            style={{
              padding: '16px',
              border: `2px solid ${selectedTask === task.id ? '#2563eb' : '#e5e7eb'}`,
              borderRadius: '8px',
              cursor: disabled ? 'not-allowed' : 'pointer',
              backgroundColor: selectedTask === task.id ? 'rgba(37, 99, 235, 0.05)' : 'transparent',
              transition: 'all 0.3s ease',
              opacity: disabled ? 0.5 : 1,
            }}
            onClick={() => !disabled && onTaskSelect(task.id)}
            role="button"
            tabIndex="0"
            onKeyDown={(e) => e.key === 'Enter' && !disabled && onTaskSelect(task.id)}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>{task.icon}</div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>
              {task.name}
            </h3>
            <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
              {task.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}