import { useState, useEffect, useCallback, useRef } from 'react';
import { apiUtils } from '../services/api';

// Custom hook for API queries with caching and loading states
export const useQuery = (key, fetcher, options = {}) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const result = await fetcher();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };

    if (options.enabled !== false) {
      fetchData();
    }
  }, [key, options.enabled]);

  return { data, isLoading, error };
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