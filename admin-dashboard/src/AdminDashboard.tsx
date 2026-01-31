import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AIMLHealth from './components/AIMLHealth';
import ClinicalMonitoring from './components/ClinicalMonitoring';
import SystemHealth from './components/SystemHealth';
import SecurityMonitoring from './components/SecurityMonitoring';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

type TabType = 'overview' | 'ai_ml' | 'clinical' | 'system' | 'security';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs = [
    { id: 'overview' as TabType, name: 'Overview', icon: '📊' },
    { id: 'ai_ml' as TabType, name: 'AI/ML Health', icon: '🤖' },
    { id: 'clinical' as TabType, name: 'Clinical', icon: '🏥' },
    { id: 'system' as TabType, name: 'System', icon: '⚙️' },
    { id: 'security' as TabType, name: 'Security', icon: '🔐' },
  ];

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-3xl font-bold text-gray-900">
              🔧 NeuroPredict-AI Admin Dashboard
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Real-Time Clinical Decision Support System Monitoring
            </p>
          </div>
        </header>

        {/* Tabs */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm
                    ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'overview' && <OverviewTab />}
          {activeTab === 'ai_ml' && <AIMLHealth />}
          {activeTab === 'clinical' && <ClinicalMonitoring />}
          {activeTab === 'system' && <SystemHealth />}
          {activeTab === 'security' && <SecurityMonitoring />}
        </main>
      </div>
    </QueryClientProvider>
  );
}

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">📊 Dashboard Overview</h2>
        <p className="text-gray-600 mb-6">
          Welcome to the NeuroPredict-AI Real-Time Monitoring Dashboard. This comprehensive
          dashboard provides real-time insights into AI/ML health, clinical operations, system
          performance, and security compliance.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">AI/ML Health</h3>
            <p className="text-2xl font-bold text-blue-600 mt-2">Monitoring</p>
            <p className="text-xs text-gray-500 mt-1">
              Model drift, performance metrics, feature importance
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Clinical Monitoring</h3>
            <p className="text-2xl font-bold text-green-600 mt-2">Active</p>
            <p className="text-xs text-gray-500 mt-1">
              Longitudinal tracking, smart alerts, prediction queue
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">System Health</h3>
            <p className="text-2xl font-bold text-purple-600 mt-2">Operational</p>
            <p className="text-xs text-gray-500 mt-1">
              Latency, throughput, service status, error rates
            </p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Security & Compliance</h3>
            <p className="text-2xl font-bold text-red-600 mt-2">Secured</p>
            <p className="text-xs text-gray-500 mt-1">
              Audit logs, authentication monitoring, admin activity
            </p>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3">Key Features</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✅ Real-time WebSocket updates</li>
              <li>✅ AI/ML model drift detection</li>
              <li>✅ Clinical decision support alerts</li>
              <li>✅ System performance monitoring</li>
              <li>✅ Security compliance tracking</li>
              <li>✅ FDA/HIPAA audit logging</li>
            </ul>
          </div>
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3">Monitoring Capabilities</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>📈 Data drift and performance drift analysis</li>
              <li>📊 Confidence score distribution</li>
              <li>🔍 Feature importance explainability</li>
              <li>⚠️ Smart clinical alerts</li>
              <li>⚡ System latency and throughput</li>
              <li>🔐 Security event monitoring</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
