import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, PredictRequest, RecommendRequest, ChatRequest } from '@/lib/api';

// Hook for health check
export const useBackendHealth = () => {
  return useQuery({
    queryKey: ['backend-health'],
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 30000, // Check every 30 seconds
  });
};

// Hook for predictions
export const useBackendPredict = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: PredictRequest) => apiClient.predict(data),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
  });
};

// Hook for recommendations
export const useBackendRecommend = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: RecommendRequest) => apiClient.recommend(data),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};

// Hook for chat
export const useBackendChat = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ChatRequest) => apiClient.chat(data),
    onSuccess: () => {
      // Invalidate chat sessions
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
    },
  });
};

// Hook for model information
export const useModelInfo = (modelType: string) => {
  return useQuery({
    queryKey: ['model-info', modelType],
    queryFn: () => apiClient.getModelInfo(modelType),
    enabled: !!modelType,
  });
};

// Hook for all models
export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.getModels(),
  });
};

// Hook for cache statistics
export const useCacheStats = () => {
  return useQuery({
    queryKey: ['cache-stats'],
    queryFn: () => apiClient.getCacheStats(),
    refetchInterval: 60000, // Check every minute
  });
};

// Hook for training status
export const useTrainingStatus = () => {
  return useQuery({
    queryKey: ['training-status'],
    queryFn: () => apiClient.getTrainingStatus(),
    refetchInterval: 30000, // Check every 30 seconds
  });
};

// Hook for retraining models
export const useRetrainModel = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (modelType: string) => apiClient.retrainModel(modelType),
    onSuccess: () => {
      // Invalidate model-related queries
      queryClient.invalidateQueries({ queryKey: ['models'] });
      queryClient.invalidateQueries({ queryKey: ['model-info'] });
      queryClient.invalidateQueries({ queryKey: ['training-status'] });
    },
  });
};

// Hook for retraining all models
export const useRetrainAllModels = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiClient.retrainAllModels(),
    onSuccess: () => {
      // Invalidate all model-related queries
      queryClient.invalidateQueries({ queryKey: ['models'] });
      queryClient.invalidateQueries({ queryKey: ['model-info'] });
      queryClient.invalidateQueries({ queryKey: ['training-status'] });
    },
  });
};

// Hook for predictions history
export const usePredictionsHistory = (limit: number = 100) => {
  return useQuery({
    queryKey: ['predictions-history', limit],
    queryFn: () => apiClient.getPredictions(limit),
  });
};

// Hook for chat sessions
export const useChatSessions = (limit: number = 50) => {
  return useQuery({
    queryKey: ['chat-sessions', limit],
    queryFn: () => apiClient.getChatSessions(limit),
  });
};

// Hook for specific chat session
export const useChatSession = (sessionId: string) => {
  return useQuery({
    queryKey: ['chat-session', sessionId],
    queryFn: () => apiClient.getChatSession(sessionId),
    enabled: !!sessionId,
  });
};

// Hook for reloading models
export const useReloadModel = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (modelType: string) => apiClient.reloadModel(modelType),
    onSuccess: () => {
      // Invalidate model-related queries
      queryClient.invalidateQueries({ queryKey: ['models'] });
      queryClient.invalidateQueries({ queryKey: ['model-info'] });
    },
  });
};

// Hook for invalidating cache
export const useInvalidateCache = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (modelType: string) => apiClient.invalidateCache(modelType),
    onSuccess: () => {
      // Invalidate cache stats
      queryClient.invalidateQueries({ queryKey: ['cache-stats'] });
    },
  });
};
