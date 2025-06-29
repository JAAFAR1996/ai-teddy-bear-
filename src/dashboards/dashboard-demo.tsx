// ===================================================================
// 🧸 AI Teddy Bear - Real-time Dashboard Demo
// Enterprise Analytics Dashboard Demonstration
// Analytics Team Lead: Senior Data Engineer
// Date: January 2025
// ===================================================================

import React, { useState, useEffect } from 'react';

interface DashboardDemoProps {
  theme?: 'light' | 'dark';
  autoRefresh?: boolean;
}

interface MockMetrics {
  safetyScore: number;
  activeConversations: number;
  conversationGrowth: number;
  avgResponseTime: number;
  systemHealth: number;
  healthyServices: number;
  warningServices: number;
  criticalServices: number;
  totalServices: number;
  uptime: string;
  childrenProtected: number;
  complianceRate: number;
  violationsDetected: number;
  autoResolvedIssues: number;
}

const DashboardDemo: React.FC<DashboardDemoProps> = ({ 
  theme = 'light', 
  autoRefresh = true 
}) => {
  const [metrics, setMetrics] = useState<MockMetrics>({
    safetyScore: 98.5,
    activeConversations: 1247,
    conversationGrowth: 12.3,
    avgResponseTime: 185,
    systemHealth: 96.8,
    healthyServices: 28,
    warningServices: 2,
    criticalServices: 0,
    totalServices: 30,
    uptime: '99.95%',
    childrenProtected: 1250,
    complianceRate: 99.2,
    violationsDetected: 3,
    autoResolvedIssues: 12
  });

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [alerts] = useState([
    {
      id: 1,
      severity: 'warning' as const,
      title: 'High Response Time',
      message: 'AI response time exceeded 2 seconds in EU region',
      timestamp: new Date(Date.now() - 300000)
    },
    {
      id: 2,
      severity: 'info' as const,
      title: 'System Update',
      message: 'Security patch deployed successfully',
      timestamp: new Date(Date.now() - 1800000)
    }
  ]);

  // Simulate real-time data updates
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        safetyScore: Math.max(95, Math.min(100, prev.safetyScore + (Math.random() - 0.5) * 0.5)),
        activeConversations: Math.max(800, Math.min(1500, prev.activeConversations + Math.floor((Math.random() - 0.5) * 20))),
        avgResponseTime: Math.max(120, Math.min(500, prev.avgResponseTime + Math.floor((Math.random() - 0.5) * 30))),
        systemHealth: Math.max(90, Math.min(100, prev.systemHealth + (Math.random() - 0.5) * 0.3))
      }));
      setLastUpdated(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getStatusColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return 'text-green-600 bg-green-100';
    if (value >= thresholds.warning) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getResponseTimeColor = (time: number) => {
    if (time < 200) return 'text-green-600 bg-green-100';
    if (time < 500) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className={`min-h-screen p-6 ${theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-gray-50'}`}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🧸 AI Teddy Bear - Executive Dashboard
            </h1>
            <p className="text-gray-600">
              Real-time monitoring and analytics • Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-semibold">
              Overall Health: {metrics.systemHealth.toFixed(1)}%
            </div>
            <div className={`px-3 py-1 rounded-md text-sm ${autoRefresh ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
              {autoRefresh ? '🔄 Live' : '⏸️ Paused'}
            </div>
          </div>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Child Safety Score */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Child Safety Score</p>
              <p className={`text-3xl font-bold ${getStatusColor(metrics.safetyScore, { good: 95, warning: 85 })}`}>
                {metrics.safetyScore.toFixed(1)}%
              </p>
            </div>
            <div className="text-4xl">🛡️</div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>Target: &gt;95%</span>
            </div>
          </div>
        </div>

        {/* Active Conversations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Conversations</p>
              <p className="text-3xl font-bold text-blue-600">
                {metrics.activeConversations.toLocaleString()}
              </p>
            </div>
            <div className="text-4xl">💬</div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-green-600">
              <span>↗️ +{metrics.conversationGrowth.toFixed(1)}% from yesterday</span>
            </div>
          </div>
        </div>

        {/* AI Response Time */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">AI Response Time</p>
              <p className={`text-3xl font-bold ${getResponseTimeColor(metrics.avgResponseTime)}`}>
                {metrics.avgResponseTime}ms
              </p>
            </div>
            <div className="text-4xl">⚡</div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>Target: &lt;500ms</span>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className={`text-3xl font-bold ${getStatusColor(metrics.systemHealth, { good: 95, warning: 85 })}`}>
                {metrics.systemHealth.toFixed(1)}%
              </p>
            </div>
            <div className="text-4xl">🖥️</div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm text-gray-600">
              <span>{metrics.healthyServices}/{metrics.totalServices} services healthy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Child Safety & Compliance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            👶 Child Safety & Compliance
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Children Protected</span>
              <span className="font-semibold text-green-600">{metrics.childrenProtected.toLocaleString()}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">COPPA Compliance Rate</span>
              <span className="font-semibold text-green-600">{metrics.complianceRate}%</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Violations Detected</span>
              <span className="font-semibold text-yellow-600">{metrics.violationsDetected}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Auto-resolved Issues</span>
              <span className="font-semibold text-blue-600">{metrics.autoResolvedIssues}</span>
            </div>
          </div>

          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center text-green-800">
              <div className="text-2xl mr-2">✅</div>
              <div>
                <div className="font-semibold">All Safety Checks Passed</div>
                <div className="text-sm">Zero critical violations in the last 24 hours</div>
              </div>
            </div>
          </div>
        </div>

        {/* System Performance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            📊 System Performance
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">System Uptime</span>
              <span className="font-semibold text-green-600">{metrics.uptime}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Healthy Services</span>
              <span className="font-semibold text-green-600">{metrics.healthyServices}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Warning Services</span>
              <span className="font-semibold text-yellow-600">{metrics.warningServices}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Critical Services</span>
              <span className="font-semibold text-red-600">{metrics.criticalServices}</span>
            </div>
          </div>

          {/* Service Status Visualization */}
          <div className="mt-6">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm text-gray-600">Service Health Distribution</span>
            </div>
            <div className="flex h-4 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="bg-green-500" 
                style={{ width: `${(metrics.healthyServices / metrics.totalServices) * 100}%` }}
              ></div>
              <div 
                className="bg-yellow-500" 
                style={{ width: `${(metrics.warningServices / metrics.totalServices) * 100}%` }}
              ></div>
              <div 
                className="bg-red-500" 
                style={{ width: `${(metrics.criticalServices / metrics.totalServices) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Alerts */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-xl font-semibold mb-4 flex items-center">
          🚨 Real-time Alerts
        </h3>
        
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <div className="text-4xl mb-2">✅</div>
              <div>No active alerts</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map(alert => (
              <div 
                key={alert.id}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'critical' 
                    ? 'bg-red-50 border-red-500' 
                    : alert.severity === 'warning'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className={`font-semibold ${
                      alert.severity === 'critical' 
                        ? 'text-red-800' 
                        : alert.severity === 'warning'
                        ? 'text-yellow-800'
                        : 'text-blue-800'
                    }`}>
                      {alert.title}
                    </div>
                    <div className="text-gray-600 mt-1">{alert.message}</div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {alert.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">⚡ Quick Actions</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📊 Generate Report
          </button>
          <button className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            🔄 Refresh Data
          </button>
          <button className="px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
            🚨 View All Alerts
          </button>
          <button className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            ⚙️ System Settings
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-gray-200 text-center text-gray-500">
        <p>🧸 AI Teddy Bear Analytics Dashboard • Built with ❤️ by Analytics Team</p>
        <p className="text-sm mt-1">
          Real-time monitoring • Auto-refresh: {autoRefresh ? 'Enabled' : 'Disabled'} • 
          Data as of {lastUpdated.toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default DashboardDemo; 