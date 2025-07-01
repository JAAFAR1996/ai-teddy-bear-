/**
 * Dashboard Container Component
 * 
 * Main container that orchestrates dashboard functionality
 * Separated from business logic following Clean Architecture
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useDashboardBusiness } from '../../../application/hooks/useDashboardBusiness';
import { DashboardView } from './DashboardView';
import { DashboardHeader } from './DashboardHeader';
import { DashboardStats } from './DashboardStats';
import { DashboardCharts } from './DashboardCharts';
import { DashboardActivities } from './DashboardActivities';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ErrorMessage } from '../../ui/ErrorMessage';
import { toast } from 'react-hot-toast';

export const DashboardContainer = ({ childId: propChildId }) => {
  // Local state for UI concerns only
  const [selectedChildId, setSelectedChildId] = useState(propChildId || null);
  const [timeRange, setTimeRange] = useState('7d');
  const [showPDFOptions, setShowPDFOptions] = useState(false);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  // Business logic through custom hook
  const {
    // Data
    children,
    dashboardData,
    analyticsData,
    notifications,
    
    // Loading states
    isLoading,
    childrenLoading,
    dashboardLoading,
    analyticsLoading,
    
    // Error states
    error,
    
    // Actions
    selectChild,
    refreshDashboard,
    exportPDF,
    
    // Connection status
    isConnected,
    unreadCount
  } = useDashboardBusiness(selectedChildId, timeRange);

  // UI Event handlers
  const handleChildSelect = useCallback((childId) => {
    setSelectedChildId(childId);
    selectChild(childId);
  }, [selectChild]);

  const handleTimeRangeChange = useCallback((newRange) => {
    setTimeRange(newRange);
  }, []);

  const handlePDFExport = useCallback(async (options) => {
    setPdfGenerating(true);
    try {
      await exportPDF({ ...options, childId: selectedChildId });
      toast.success('تم تصدير التقرير بنجاح');
    } catch (error) {
      toast.error('فشل في تصدير التقرير');
    } finally {
      setPdfGenerating(false);
      setShowPDFOptions(false);
    }
  }, [selectedChildId, exportPDF]);

  const handleRefresh = useCallback(async () => {
    try {
      await refreshDashboard();
      toast.success('تم تحديث البيانات');
    } catch (error) {
      toast.error('فشل في تحديث البيانات');
    }
  }, [refreshDashboard]);

  // Handle child selection from URL or prop changes
  useEffect(() => {
    if (propChildId && propChildId !== selectedChildId) {
      setSelectedChildId(propChildId);
      selectChild(propChildId);
    }
  }, [propChildId, selectedChildId, selectChild]);

  // Auto-select first child if none selected
  useEffect(() => {
    if (children && children.length > 0 && !selectedChildId) {
      const firstChild = children[0];
      setSelectedChildId(firstChild.id);
      selectChild(firstChild.id);
    }
  }, [children, selectedChildId, selectChild]);

  // Show loading if children are still loading
  if (childrenLoading && !children) {
    return <LoadingSpinner message="جاري تحميل بيانات الأطفال..." />;
  }

  // Show error if failed to load children
  if (error && !children) {
    return (
      <ErrorMessage 
        message="فشل في تحميل بيانات الأطفال"
        onRetry={handleRefresh}
      />
    );
  }

  // Show message if no children found
  if (children && children.length === 0) {
    return (
      <ErrorMessage 
        message="لم يتم العثور على أطفال مسجلين"
        description="يرجى إضافة طفل أولاً لعرض لوحة التحكم"
      />
    );
  }

  return (
    <DashboardView
      // Data props
      children={children}
      selectedChildId={selectedChildId}
      dashboardData={dashboardData}
      analyticsData={analyticsData}
      timeRange={timeRange}
      
      // UI state props
      showPDFOptions={showPDFOptions}
      pdfGenerating={pdfGenerating}
      
      // Loading states
      isLoading={isLoading}
      dashboardLoading={dashboardLoading}
      analyticsLoading={analyticsLoading}
      
      // Connection status
      isConnected={isConnected}
      unreadCount={unreadCount}
      notifications={notifications}
      
      // Event handlers
      onChildSelect={handleChildSelect}
      onTimeRangeChange={handleTimeRangeChange}
      onPDFExport={handlePDFExport}
      onRefresh={handleRefresh}
      onShowPDFOptions={setShowPDFOptions}
      
      // Error handling
      error={error}
    />
  );
}; 