import client from './client';

export const trainModel = async (fileId, taskType, targetColumn) => {
  try {
    const response = await client.post('/train', {
      file_id: fileId,
      task_type: taskType,
      target_column: targetColumn,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getAllModels = async () => {
  try {
    const response = await client.get('/models');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const downloadModel = async (modelId, format = 'joblib') => {
  try {
    const response = await client.get(`/model/${modelId}/download`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const deleteModel = async (modelId) => {
  try {
    const response = await client.delete(`/model/${modelId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const predictWithModel = async (modelId, data) => {
  try {
    const response = await client.post('/predict', {
      model_id: modelId,
      data,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const checkHealthStatus = async () => {
  try {
    const response = await client.get('/health');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};