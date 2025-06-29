import React, { memo, useMemo } from 'react';
import styled from 'styled-components';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';

// Styled components
const ChartWrapper = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
`;

const NoDataContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  
  .icon {
    font-size: 2.5rem;
    margin-bottom: ${props => props.theme.spacing.md};
    opacity: 0.5;
  }
  
  .message {
    font-size: ${props => props.theme.typography.fontSize.base};
    margin-bottom: ${props => props.theme.spacing.sm};
  }
  
  .description {
    font-size: ${props => props.theme.typography.fontSize.sm};
    max-width: 250px;
    opacity: 0.8;
  }
`;

// Color palette for charts
const CHART_COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00c49f',
  '#ffbb28', '#ff8042', '#8dd1e1', '#d084d0', '#ffb347'
];

// Custom tooltip component
const CustomTooltip = ({ active, payload, label, formatValue, valuePrefix, valueSuffix }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(255, 255, 255, 0.98)',
        border: '1px solid #e1e5e9',
        borderRadius: '8px',
        padding: '12px 16px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
        minWidth: '120px',
        backdropFilter: 'blur(8px)'
      }}>
        <p style={{ 
          margin: 0, 
          fontWeight: '600', 
          marginBottom: '8px',
          fontSize: '14px',
          color: '#2d3748'
        }}>
          {label}
        </p>
        {payload.map((entry, index) => (
          <div key={index} style={{ 
            display: 'flex', 
            alignItems: 'center', 
            marginBottom: index === payload.length - 1 ? 0 : '6px',
            gap: '8px'
          }}>
            <div style={{
              width: '10px',
              height: '10px',
              borderRadius: '2px',
              backgroundColor: entry.color,
              flexShrink: 0
            }} />
            <span style={{ 
              fontSize: '13px',
              color: '#4a5568'
            }}>
              {entry.name}: {valuePrefix}{formatValue ? formatValue(entry.value) : entry.value}{valueSuffix}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// Main Chart component
const Chart = memo(({
  data,
  type = 'line',
  height = 300,
  xDataKey = 'date',
  yDataKeys = ['value'],
  colors = CHART_COLORS,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  formatXAxis,
  formatYAxis,
  formatTooltip,
  valuePrefix = '',
  valueSuffix = '',
  smooth = true,
  strokeWidth = 2,
  fillOpacity = 0.6,
  animationDuration = 1000,
  margin = { top: 20, right: 30, left: 20, bottom: 20 },
  gradient = false,
  stack = false,
  ...props
}) => {
  // Validate and process data
  const processedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return null;
    }
    
    // Ensure data has required keys
    const hasXKey = data.some(item => item[xDataKey] !== undefined);
    const hasYKeys = yDataKeys.some(key => 
      data.some(item => item[key] !== undefined)
    );
    
    if (!hasXKey || !hasYKeys) {
      console.warn('Chart: Missing required data keys', { xDataKey, yDataKeys });
      return null;
    }
    
    return data;
  }, [data, xDataKey, yDataKeys]);

  // Memoized chart components
  const chartComponents = useMemo(() => {
    if (!processedData) return null;

    const commonProps = {
      data: processedData,
      margin,
      ...(props.onMouseEnter && { onMouseEnter: props.onMouseEnter }),
      ...(props.onMouseLeave && { onMouseLeave: props.onMouseLeave })
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={xDataKey}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatXAxis}
              axisLine={{ stroke: '#e5e7eb' }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatYAxis}
              axisLine={{ stroke: '#e5e7eb' }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            {showTooltip && (
              <Tooltip 
                content={<CustomTooltip 
                  formatValue={formatTooltip}
                  valuePrefix={valuePrefix}
                  valueSuffix={valueSuffix}
                />}
              />
            )}
            {showLegend && <Legend />}
            {yDataKeys.map((key, index) => (
              <Line
                key={key}
                type={smooth ? "monotone" : "linear"}
                dataKey={key}
                stroke={colors[index % colors.length]}
                strokeWidth={strokeWidth}
                dot={{ fill: colors[index % colors.length], strokeWidth: 1, r: 3 }}
                activeDot={{ r: 5, stroke: colors[index % colors.length], strokeWidth: 2 }}
                animationDuration={animationDuration}
              />
            ))}
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={xDataKey}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatXAxis}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatYAxis}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            {showTooltip && (
              <Tooltip 
                content={<CustomTooltip 
                  formatValue={formatTooltip}
                  valuePrefix={valuePrefix}
                  valueSuffix={valueSuffix}
                />}
              />
            )}
            {showLegend && <Legend />}
            {yDataKeys.map((key, index) => (
              <Area
                key={key}
                type={smooth ? "monotone" : "linear"}
                dataKey={key}
                stackId={stack ? "1" : undefined}
                stroke={colors[index % colors.length]}
                fill={gradient ? `url(#gradient-${index})` : colors[index % colors.length]}
                fillOpacity={fillOpacity}
                strokeWidth={strokeWidth}
                animationDuration={animationDuration}
              />
            ))}
            {gradient && (
              <defs>
                {yDataKeys.map((key, index) => (
                  <linearGradient key={`gradient-${index}`} id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={colors[index % colors.length]} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={colors[index % colors.length]} stopOpacity={0.1}/>
                  </linearGradient>
                ))}
              </defs>
            )}
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={xDataKey}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatXAxis}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatYAxis}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            {showTooltip && (
              <Tooltip 
                content={<CustomTooltip 
                  formatValue={formatTooltip}
                  valuePrefix={valuePrefix}
                  valueSuffix={valueSuffix}
                />}
              />
            )}
            {showLegend && <Legend />}
            {yDataKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={colors[index % colors.length]}
                radius={[2, 2, 0, 0]}
                animationDuration={animationDuration}
              />
            ))}
          </BarChart>
        );

      default:
        console.warn(`Unsupported chart type: ${type}`);
        return null;
    }
  }, [
    processedData, type, xDataKey, yDataKeys, colors, showGrid, showLegend, 
    showTooltip, formatXAxis, formatYAxis, formatTooltip, valuePrefix, 
    valueSuffix, smooth, strokeWidth, fillOpacity, animationDuration, 
    margin, gradient, stack, props
  ]);

  // Loading/Empty state
  if (!processedData) {
    return (
      <ChartWrapper style={{ height }}>
        <NoDataContainer>
          <div className="icon">📈</div>
          <div className="message">لا توجد بيانات متاحة</div>
          <div className="description">
            سيتم عرض الرسم البياني هنا عند توفر البيانات
          </div>
        </NoDataContainer>
      </ChartWrapper>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      style={{ height }}
    >
      <ChartWrapper style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartComponents}
        </ResponsiveContainer>
      </ChartWrapper>
    </motion.div>
  );
});

Chart.displayName = 'Chart';

// Chart component with common presets
export const ActivityChart = memo((props) => (
  <Chart
    type="area"
    gradient={true}
    smooth={true}
    valueSuffix=" دقيقة"
    formatXAxis={(value) => {
      const date = new Date(value);
      return `${date.getDate()}/${date.getMonth() + 1}`;
    }}
    colors={['#4ade80', '#3b82f6', '#f59e0b']}
    {...props}
  />
));

export const PerformanceChart = memo((props) => (
  <Chart
    type="line"
    smooth={true}
    valueSuffix="%"
    strokeWidth={3}
    colors={['#8b5cf6', '#ec4899', '#06b6d4']}
    {...props}
  />
));

export const ConversationChart = memo((props) => (
  <Chart
    type="bar"
    valueSuffix=" محادثة"
    colors={['#10b981', '#f59e0b', '#ef4444']}
    {...props}
  />
));

export default Chart; 