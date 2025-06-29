import { useState, useEffect, useCallback, useRef } from 'react';
import { apiUtils } from '../services/api';

// Custom hook for API queries with caching and loading states
export const useQuery = (queryKey, queryFn, options = {}) => {
  const {
    enabled = true,
    refetchOnWindowFocus = false,
    refetchInterval = null,
    staleTime = 5 * 60 * 1000, // 5 minutes
    cacheTime = 10 * 60 * 1000, // 10 minutes
    retry = 3,
    onSuccess,
    onError,
  } = options;

  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);
  const [lastFetch, setLastFetch] = useState(null);
  
  const retryCountRef = useRef(0);
  const abortControllerRef = useRef(null);
  const intervalRef = useRef(null);

  // Generate cache key
  const cacheKey = Array.isArray(queryKey) ? queryKey.join('-') : queryKey;

  // Get cached data
  const getCachedData = useCallback(() => {
    try {
      const cached = localStorage.getItem(`query-cache-${cacheKey}`);
      if (cached) {
        const { data: cachedData, timestamp } = JSON.parse(cached);
        const now = Date.now();
        
        // Check if cache is still valid
        if (now - timestamp < staleTime) {
          return cachedData;
        }
        
        // Remove expired cache
        localStorage.removeItem(`query-cache-${cacheKey}`);
      }
    } catch (error) {
      console.warn('Failed to get cached data:', error);
    }
    return null;
  }, [cacheKey, staleTime]);

  // Set cached data
  const setCachedData = useCallback((newData) => {
    try {
      const cacheItem = {
        data: newData,
        timestamp: Date.now(),
      };
      localStorage.setItem(`query-cache-${cacheKey}`, JSON.stringify(cacheItem));
      
      // Set cleanup timer
      setTimeout(() => {
        localStorage.removeItem(`query-cache-${cacheKey}`);
      }, cacheTime);
    } catch (error) {
      console.warn('Failed to cache data:', error);
    }
  }, [cacheKey, cacheTime]);

  // Execute query
  const executeQuery = useCallback(async (showLoader = true) => {
    if (!enabled) return;

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      if (showLoader && !data) {
        setIsLoading(true);
      }
      setIsFetching(true);
      setError(null);

      const result = await queryFn({
        signal: abortControllerRef.current.signal,
      });

      setData(result);
      setCachedData(result);
      setLastFetch(Date.now());
      retryCountRef.current = 0;

      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        return; // Request was cancelled
      }

      const errorMessage = apiUtils.formatError(err);
      setError(errorMessage);

      // Retry logic
      if (retryCountRef.current < retry) {
        retryCountRef.current += 1;
        setTimeout(() => {
          executeQuery(false);
        }, Math.pow(2, retryCountRef.current) * 1000); // Exponential backoff
      } else if (onError) {
        onError(err);
      }
    } finally {
      setIsLoading(false);
      setIsFetching(false);
    }
  }, [queryFn, enabled, data, retry, onSuccess, onError, setCachedData]);

  // Refetch function
  const refetch = useCallback(() => {
    return executeQuery(false);
  }, [executeQuery]);

  // Initial load
  useEffect(() => {
    if (!enabled) return;

    // Try to load from cache first
    const cachedData = getCachedData();
    if (cachedData) {
      setData(cachedData);
      setIsLoading(false);
      setLastFetch(Date.now());
    }

    // Execute query
    executeQuery();

    // Cleanup
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [enabled, executeQuery, getCachedData]);

  // Refetch interval
  useEffect(() => {
    if (refetchInterval && enabled) {
      intervalRef.current = setInterval(() => {
        executeQuery(false);
      }, refetchInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [refetchInterval, enabled, executeQuery]);

  // Refetch on window focus
  useEffect(() => {
    if (refetchOnWindowFocus && enabled) {
      const handleFocus = () => {
        // Only refetch if data is stale
        if (lastFetch && Date.now() - lastFetch > staleTime) {
          executeQuery(false);
        }
      };

      window.addEventListener('focus', handleFocus);
      return () => window.removeEventListener('focus', handleFocus);
    }
  }, [refetchOnWindowFocus, enabled, lastFetch, staleTime, executeQuery]);

  return {
    data,
    error,
    isLoading,
    isFetching,
    refetch,
    isStale: lastFetch ? Date.now() - lastFetch > staleTime : true,
  };
};

// Hook for mutations
export const useMutation = (mutationFn, options = {}) => {
  const { onSuccess, onError, onSettled } = options;
  
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const mutate = useCallback(async (variables) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await mutationFn(variables);
      setData(result);
      
      if (onSuccess) {
        onSuccess(result, variables);
      }
      
      return result;
    } catch (err) {
      const errorMessage = apiUtils.formatError(err);
      setError(errorMessage);
      
      if (onError) {
        onError(err, variables);
      }
      
      throw err;
    } finally {
      setIsLoading(false);
      
      if (onSettled) {
        onSettled(data, error);
      }
    }
  }, [mutationFn, onSuccess, onError, onSettled, data, error]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    error,
    isLoading,
    mutate,
    reset,
  };
};

// Utility hook for managing form states
export const useForm = (initialValues = {}, validationSchema = null) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setValue = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when value changes
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  }, [errors]);

  const setFieldTouched = useCallback((name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  }, []);

  const validateField = useCallback((name, value) => {
    if (!validationSchema) return null;

    try {
      validationSchema.validateSyncAt(name, { [name]: value });
      return null;
    } catch (error) {
      return error.message;
    }
  }, [validationSchema]);

  const validateForm = useCallback(() => {
    if (!validationSchema) return {};

    try {
      validationSchema.validateSync(values, { abortEarly: false });
      return {};
    } catch (error) {
      const validationErrors = {};
      error.inner.forEach(err => {
        if (err.path) {
          validationErrors[err.path] = err.message;
        }
      });
      return validationErrors;
    }
  }, [validationSchema, values]);

  const handleSubmit = useCallback((onSubmit) => {
    return async (e) => {
      e.preventDefault();
      setIsSubmitting(true);

      const formErrors = validateForm();
      if (Object.keys(formErrors).length > 0) {
        setErrors(formErrors);
        setIsSubmitting(false);
        return;
      }

      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        setIsSubmitting(false);
      }
    };
  }, [values, validateForm]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    setValue,
    setFieldTouched,
    validateField,
    handleSubmit,
    reset,
    isValid: Object.keys(validateForm()).length === 0,
  };
};

// Hook for managing pagination
export const usePagination = (initialPage = 1, initialLimit = 10) => {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);
  const [total, setTotal] = useState(0);

  const totalPages = Math.ceil(total / limit);
  const hasNextPage = page < totalPages;
  const hasPrevPage = page > 1;

  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setPage(prev => prev + 1);
    }
  }, [hasNextPage]);

  const prevPage = useCallback(() => {
    if (hasPrevPage) {
      setPage(prev => prev - 1);
    }
  }, [hasPrevPage]);

  const goToPage = useCallback((newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  }, [totalPages]);

  const changeLimit = useCallback((newLimit) => {
    setLimit(newLimit);
    setPage(1); // Reset to first page
  }, []);

  return {
    page,
    limit,
    total,
    totalPages,
    hasNextPage,
    hasPrevPage,
    setPage,
    setLimit,
    setTotal,
    nextPage,
    prevPage,
    goToPage,
    changeLimit,
  };
};

export default useQuery; 