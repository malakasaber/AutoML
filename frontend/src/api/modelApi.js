import client from './client';

export const downloadModelFile = async (modelId, format = 'joblib') => {
  try {
    const response = await client.get(`/model/${modelId}/download`, {
      params: { format },
      responseType: 'blob',
    });
    
    // Determine file extension based on format
    const extension = format === 'pickle' ? '.pkl' : '.joblib';
    const filename = `model_${modelId}${extension}`;
    
    // Create blob download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentElement.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return { success: true, filename };
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const deleteModelFile = async (modelId) => {
  try {
    const response = await client.delete(`/model/${modelId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getModelsList = async () => {
  try {
    const response = await client.get('/models');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};