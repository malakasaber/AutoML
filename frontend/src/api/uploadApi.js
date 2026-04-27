import client from './client';

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const previewFile = async (fileId) => {
  try {
    const response = await client.get(`/preview/${fileId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const validateFile = async (fileId, taskType, targetColumn) => {
  try {
    const response = await client.post('/validate', {
      file_id: fileId,
      task_type: taskType,
      target_column: targetColumn,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getTargetColumns = async (fileId) => {
  try {
    const response = await client.post('/target-columns', {
      file_id: fileId,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};