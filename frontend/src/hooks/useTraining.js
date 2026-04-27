import { useState } from 'react';
import * as trainApi from '../api/trainApi';

export const useTraining = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trainingData, setTrainingData] = useState(null);

  const trainModel = async (fileId, taskType, targetColumn) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await trainApi.trainModel(fileId, taskType, targetColumn);
      setTrainingData(response);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Model training failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const predictWithModel = async (modelId, data) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await trainApi.predictWithModel(modelId, data);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Prediction failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getAllModels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await trainApi.getAllModels();
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch models';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteModel = async (modelId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await trainApi.deleteModel(modelId);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete model';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    trainingData,
    trainModel,
    predictWithModel,
    getAllModels,
    deleteModel,
  };
};