import { useState } from 'react';
import * as uploadApi from '../api/uploadApi';

export const useUpload = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileData, setFileData] = useState(null);

  const uploadFile = async (file) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadApi.uploadFile(file);
      setFileData(response);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Failed to upload file';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const previewFile = async (fileId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadApi.previewFile(fileId);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Failed to preview file';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const validateFile = async (fileId, taskType, targetColumn) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadApi.validateFile(fileId, taskType, targetColumn);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'File validation failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getTargetColumns = async (fileId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadApi.getTargetColumns(fileId);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Failed to get target columns';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    fileData,
    uploadFile,
    previewFile,
    validateFile,
    getTargetColumns,
  };
};