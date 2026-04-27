/**
 * Format large numbers with appropriate suffixes
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return 'N/A';
  if (typeof num !== 'number') return String(num);

  if (Math.abs(num) >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M';
  } else if (Math.abs(num) >= 1000) {
    return (num / 1000).toFixed(2) + 'K';
  }
  return num.toFixed(2);
};

/**
 * Format decimal numbers with precision
 */
export const formatDecimal = (num, precision = 4) => {
  if (num === null || num === undefined) return 'N/A';
  if (typeof num !== 'number') return String(num);
  return num.toFixed(precision);
};

/**
 * Format percentage values
 */
export const formatPercent = (num) => {
  if (num === null || num === undefined) return 'N/A';
  return `${(num * 100).toFixed(2)}%`;
};

/**
 * Format file size in human-readable format
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format date to readable format
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
};

/**
 * Get metric color based on value and metric type
 */
export const getMetricColor = (metric, value) => {
  const metricLower = metric.toLowerCase();

  // Higher is better metrics
  if (['accuracy', 'precision', 'recall', 'f1', 'r2', 'silhouette'].includes(metricLower)) {
    if (value >= 0.8) return '#16a34a'; // success
    if (value >= 0.6) return '#f59e0b'; // warning
    return '#ef4444'; // danger
  }

  // Lower is better metrics
  if (['mae', 'mse', 'rmse', 'loss'].includes(metricLower)) {
    if (value <= 0.2) return '#16a34a'; // success
    if (value <= 0.5) return '#f59e0b'; // warning
    return '#ef4444'; // danger
  }

  return '#2563eb'; // default
};

/**
 * Parse confusion matrix data for visualization
 */
export const parseConfusionMatrix = (data) => {
  if (!Array.isArray(data)) return [];
  return data.map(row => (Array.isArray(row) ? row : [row]));
};

/**
 * Get task type display name
 */
export const getTaskTypeName = (taskType) => {
  const names = {
    classification: 'Classification',
    regression: 'Regression',
    clustering: 'Clustering',
  };
  return names[taskType] || taskType;
};

/**
 * Validate email format
 */
export const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Debounce function for handling rapid function calls
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Convert array of objects to CSV format
 */
export const convertToCSV = (data) => {
  if (!Array.isArray(data) || data.length === 0) return '';

  const headers = Object.keys(data[0]);
  const rows = data.map(obj => headers.map(header => obj[header]).join(','));
  return [headers.join(','), ...rows].join('\n');
};