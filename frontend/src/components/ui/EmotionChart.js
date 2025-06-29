import React, { memo, useMemo, useState, useCallback } from 'react';
import styled from 'styled-components';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ReferenceLine
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

// Styled components
const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
`;

const ChartHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
`;

const ChartTitle = styled.h3`
  margin: 0;
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
`;

const ChartTypeSelector = styled.select`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.sm};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ChartControls = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  align-items: center;
  flex-wrap: wrap;
`;

const PerformanceToggle = styled.button`
  padding: ${props => props.theme.spacing.xs};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.highPerformance 
    ? props.theme.colors.primary 
    : props.theme.colors.surface};
  color: ${props => props.highPerformance 
    ? 'white' 
    : props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.xs};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.highPerformance 
      ? props.theme.colors.primaryDark 
      : props.theme.colors.surfaceLight};
  }
`;

const EmotionSummary = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surfaceLight};
  border-radius: ${props => props.theme.borderRadius.lg};
`;

const EmotionItem = styled.div`
  text-align: center;
  
  .emoji {
    font-size: 1.5rem;
    display: block;
    margin-bottom: 4px;
  }
  
  .label {
    font-size: ${props => props.theme.typography.fontSize.xs};
    color: ${props => props.theme.colors.textSecondary};
    margin-bottom: 2px;
  }
  
  .value {
    font-size: ${props => props.theme.typography.fontSize.sm};
    font-weight: ${props => props.theme.typography.fontWeight.semibold};
    color: ${props => props.theme.colors.text};
  }
`;

const NoDataMessage = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  
  .icon {
    font-size: 3rem;
    margin-bottom: ${props => props.theme.spacing.md};
    opacity: 0.5;
  }
  
  .message {
    font-size: ${props => props.theme.typography.fontSize.lg};
    margin-bottom: ${props => props.theme.spacing.sm};
  }
  
  .description {
    font-size: ${props => props.theme.typography.fontSize.sm};
    max-width: 300px;
  }
`;

// Color schemes for emotions
const EMOTION_COLORS = {
  joy: '#FFD700',
  happiness: '#FF6B9D', 
  excitement: '#FF8C42',
  curiosity: '#6BCF7F',
  calm: '#4ECDC4',
  sadness: '#5DADE2',
  fear: '#BB8FCE',
  anger: '#F1948A',
  tiredness: '#85929E',
  neutral: '#BDC3C7'
};

const EMOTION_EMOJIS = {
  joy: '😊',
  happiness: '😄',
  excitement: '🤩',
  curiosity: '🤔',
  calm: '😌',
  sadness: '😢',
  fear: '😰',
  anger: '😠',
  tiredness: '😴',
  neutral: '😐'
};

const EMOTION_LABELS = {
  joy: 'فرح',
  happiness: 'سعادة', 
  excitement: 'حماس',
  curiosity: 'فضول',
  calm: 'هدوء',
  sadness: 'حزن',
  fear: 'خوف',
  anger: 'غضب',
  tiredness: 'تعب',
  neutral: 'طبيعي'
};

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        minWidth: '150px'
      }}>
        <p style={{ margin: 0, fontWeight: 'bold', marginBottom: '8px' }}>
          {label}
        </p>
        {payload.map((entry, index) => (
          <div key={index} style={{ 
            display: 'flex', 
            alignItems: 'center', 
            marginBottom: '4px',
            gap: '8px'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: entry.color
            }} />
            <span style={{ fontSize: '14px' }}>
              {EMOTION_LABELS[entry.dataKey] || entry.dataKey}: {entry.value}%
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// Custom legend component
const CustomLegend = ({ payload }) => (
  <div style={{ 
    display: 'flex', 
    flexWrap: 'wrap', 
    justifyContent: 'center', 
    gap: '16px',
    marginTop: '16px'
  }}>
    {payload.map((entry, index) => (
      <div key={index} style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '6px',
        fontSize: '12px'
      }}>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          backgroundColor: entry.color
        }} />
        <span>{EMOTION_LABELS[entry.dataKey] || entry.value}</span>
      </div>
    ))}
  </div>
);

// Enhanced Chart type components with performance optimization
const LineChartView = memo(({ data, emotions, highPerformance = true }) => {
  // Performance optimization: limit data points for large datasets
  const optimizedData = useMemo(() => {
    if (!data || data.length <= 50) return data;
    if (!highPerformance) return data;
    
    // Sample data for better performance with large datasets
    const step = Math.ceil(data.length / 50);
    return data.filter((_, index) => index % step === 0);
  }, [data, highPerformance]);

  const averageScore = useMemo(() => {
    if (!optimizedData || optimizedData.length === 0) return 50;
    
    const total = optimizedData.reduce((sum, item) => {
      const emotionSum = emotions.reduce((eSum, emotion) => eSum + (item[emotion] || 0), 0);
      return sum + emotionSum;
    }, 0);
    
    return Math.round(total / (optimizedData.length * emotions.length));
  }, [optimizedData, emotions]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart 
        data={optimizedData} 
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        syncId="emotionCharts" // Sync with other charts
      >
        <CartesianGrid 
          strokeDasharray="3 3" 
          stroke="#f0f0f0" 
          strokeOpacity={0.5}
        />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return `${date.getDate()}/${date.getMonth() + 1}`;
          }}
          interval="preserveStartEnd"
        />
        <YAxis 
          tick={{ fontSize: 12 }}
          domain={[0, 100]}
          tickFormatter={(value) => `${value}%`}
        />
        
        {/* Reference line for average */}
        <ReferenceLine 
          y={averageScore} 
          stroke="#94a3b8" 
          strokeDasharray="5 5"
          label={{ value: `متوسط: ${averageScore}%`, position: "insideTopRight" }}
        />
        
        <Tooltip content={<CustomTooltip />} />
        <Legend content={<CustomLegend />} />
        
        {emotions.map((emotion) => (
          <Line
            key={emotion}
            type="monotone"
            dataKey={emotion}
            stroke={EMOTION_COLORS[emotion]}
            strokeWidth={2}
            dot={highPerformance ? { fill: EMOTION_COLORS[emotion], strokeWidth: 2, r: 4 } : false}
            activeDot={{ r: 6, stroke: EMOTION_COLORS[emotion], strokeWidth: 2 }}
            connectNulls={false}
            animationDuration={highPerformance ? 800 : 400}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
});

const AreaChartView = memo(({ data, emotions }) => (
  <ResponsiveContainer width="100%" height={300}>
    <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
      <XAxis 
        dataKey="date" 
        tick={{ fontSize: 12 }}
        tickFormatter={(value) => {
          const date = new Date(value);
          return `${date.getDate()}/${date.getMonth() + 1}`;
        }}
      />
      <YAxis 
        tick={{ fontSize: 12 }}
        domain={[0, 100]}
        tickFormatter={(value) => `${value}%`}
      />
      <Tooltip content={<CustomTooltip />} />
      <Legend content={<CustomLegend />} />
      {emotions.map((emotion, index) => (
        <Area
          key={emotion}
          type="monotone"
          dataKey={emotion}
          stackId="1"
          stroke={EMOTION_COLORS[emotion]}
          fill={EMOTION_COLORS[emotion]}
          fillOpacity={0.6}
        />
      ))}
    </AreaChart>
  </ResponsiveContainer>
));

const PieChartView = memo(({ data, emotions }) => {
  const pieData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Calculate averages for pie chart
    const averages = {};
    emotions.forEach(emotion => {
      const sum = data.reduce((acc, day) => acc + (day[emotion] || 0), 0);
      averages[emotion] = sum / data.length;
    });
    
    return Object.entries(averages)
      .filter(([_, value]) => value > 0)
      .map(([emotion, value]) => ({
        name: EMOTION_LABELS[emotion],
        value: Math.round(value),
        emotion,
        fill: EMOTION_COLORS[emotion]
      }))
      .sort((a, b) => b.value - a.value);
  }, [data, emotions]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={pieData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          innerRadius={30}
          paddingAngle={2}
          label={({ name, value }) => `${name}: ${value}%`}
          labelLine={false}
        >
          {pieData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => [`${value}%`, 'النسبة']} />
      </PieChart>
    </ResponsiveContainer>
  );
});

const RadarChartView = memo(({ data, emotions }) => {
  const radarData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Calculate averages for radar chart
    const averages = {};
    emotions.forEach(emotion => {
      const sum = data.reduce((acc, day) => acc + (day[emotion] || 0), 0);
      averages[emotion] = sum / data.length;
    });
    
    return emotions.map(emotion => ({
      emotion: EMOTION_LABELS[emotion],
      value: Math.round(averages[emotion] || 0),
      fullMark: 100
    }));
  }, [data, emotions]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={radarData} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
        <PolarGrid />
        <PolarAngleAxis dataKey="emotion" tick={{ fontSize: 12 }} />
        <PolarRadiusAxis 
          angle={0}
          domain={[0, 100]}
          tick={{ fontSize: 10 }}
          tickCount={6}
        />
        <Radar
          name="المشاعر"
          dataKey="value"
          stroke="#8884d8"
          fill="#8884d8"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Tooltip formatter={(value) => [`${value}%`, 'النسبة']} />
      </RadarChart>
    </ResponsiveContainer>
  );
});

// Main EmotionChart component with enhanced performance controls
const EmotionChart = memo(({
  data,
  title = "تحليل المشاعر",
  height = 300,
  showSummary = true,
  defaultChartType = "line",
  enablePerformanceMode = true
}) => {
  const [chartType, setChartType] = useState(defaultChartType);
  const [highPerformance, setHighPerformance] = useState(true);
  const [isInteracting, setIsInteracting] = useState(false);

  // Process and validate data
  const { processedData, availableEmotions, emotionSummary } = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return { processedData: null, availableEmotions: [], emotionSummary: {} };
    }

    // Extract available emotions from data
    const emotions = Object.keys(data[0] || {})
      .filter(key => key !== 'date' && key !== 'timestamp')
      .filter(key => EMOTION_COLORS[key]); // Only include recognized emotions

    // Calculate summary statistics
    const summary = {};
    emotions.forEach(emotion => {
      const values = data.map(d => d[emotion] || 0);
      const sum = values.reduce((acc, val) => acc + val, 0);
      const avg = sum / values.length;
      const max = Math.max(...values);
      
      summary[emotion] = {
        average: Math.round(avg),
        max: Math.round(max),
        trend: values.length > 1 ? (values[values.length - 1] - values[0] > 0 ? 'up' : 'down') : 'stable'
      };
    });

    return {
      processedData: data,
      availableEmotions: emotions,
      emotionSummary: summary
    };
  }, [data]);

  // Performance monitoring
  const performanceMetrics = useMemo(() => {
    if (!processedData) return null;
    
    return {
      dataPoints: processedData.length,
      emotions: availableEmotions.length,
      complexity: processedData.length * availableEmotions.length,
      recommended: processedData.length * availableEmotions.length < 1000 ? 'high' : 'low'
    };
  }, [processedData, availableEmotions]);

  // Interaction handlers for performance optimization
  const handleChartInteraction = useCallback((interacting) => {
    setIsInteracting(interacting);
  }, []);

  // Render chart based on type with performance considerations
  const renderChart = useCallback(() => {
    if (!processedData || availableEmotions.length === 0) {
      return (
        <NoDataMessage>
          <div className="icon">📊</div>
          <div className="message">لا توجد بيانات مشاعر متاحة</div>
          <div className="description">
            سيظهر تحليل المشاعر هنا بمجرد بدء الطفل في التفاعل مع دبدوب
          </div>
        </NoDataMessage>
      );
    }

    const chartProps = {
      data: processedData,
      emotions: availableEmotions,
      highPerformance: highPerformance && !isInteracting,
      onMouseEnter: () => handleChartInteraction(true),
      onMouseLeave: () => handleChartInteraction(false)
    };

    switch (chartType) {
      case 'area':
        return <AreaChartView {...chartProps} />;
      case 'pie':
        return <PieChartView {...chartProps} />;
      case 'radar':
        return <RadarChartView {...chartProps} />;
      default:
        return <LineChartView {...chartProps} />;
    }
  }, [processedData, availableEmotions, chartType, highPerformance, isInteracting, handleChartInteraction]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ChartContainer style={{ height }}>
        <ChartHeader>
          <ChartTitle>
            {title}
            {performanceMetrics && (
              <span style={{ 
                fontSize: '0.75rem', 
                color: '#6b7280', 
                fontWeight: 'normal',
                marginLeft: '8px'
              }}>
                ({performanceMetrics.dataPoints} نقطة)
              </span>
            )}
          </ChartTitle>
          
          {processedData && (
            <ChartControls>
              <ChartTypeSelector
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
              >
                <option value="line">خط بياني</option>
                <option value="area">مساحة مكدسة</option>
                <option value="pie">دائري</option>
                <option value="radar">رادار</option>
              </ChartTypeSelector>
              
              {enablePerformanceMode && performanceMetrics && (
                <PerformanceToggle
                  highPerformance={highPerformance}
                  onClick={() => setHighPerformance(!highPerformance)}
                  title={`الأداء: ${highPerformance ? 'عالي' : 'عادي'} (${performanceMetrics.complexity} عنصر)`}
                >
                  ⚡ {highPerformance ? 'عالي' : 'عادي'}
                </PerformanceToggle>
              )}
            </ChartControls>
          )}
        </ChartHeader>

        {showSummary && processedData && availableEmotions.length > 0 && (
          <EmotionSummary>
            {availableEmotions.slice(0, 6).map(emotion => (
              <EmotionItem key={emotion}>
                <span className="emoji">{EMOTION_EMOJIS[emotion]}</span>
                <div className="label">{EMOTION_LABELS[emotion]}</div>
                <div className="value">
                  {emotionSummary[emotion]?.average || 0}%
                  {emotionSummary[emotion]?.trend === 'up' ? ' ↗️' : 
                   emotionSummary[emotion]?.trend === 'down' ? ' ↘️' : ' ➡️'}
                </div>
              </EmotionItem>
            ))}
          </EmotionSummary>
        )}

        {renderChart()}
      </ChartContainer>
    </motion.div>
  );
});

EmotionChart.displayName = 'EmotionChart';

export default EmotionChart; 