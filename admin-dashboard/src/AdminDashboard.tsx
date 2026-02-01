import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AIMLHealth from './components/AIMLHealth';
import ClinicalMonitoring from './components/ClinicalMonitoring';
import SystemHealth from './components/SystemHealth';
import SecurityMonitoring from './components/SecurityMonitoring';
import DiseaseRanges from './components/DiseaseRanges';
import DiseaseProbability from './components/DiseaseProbability';
import MultimodalAnalysis from './components/MultimodalAnalysis';
import DataTab from './components/DataTab';
import GaugeDisplayTab from './components/GaugeDisplayTab';
import DiseaseTrackingDashboard from './pages/DiseaseTrackingDashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

type TabType = 'display' | 'gauge' | 'realtime' | 'checklist' | 'alarm' | 'control' | 'graph' | '3d' | 'reporting' | 'clinical' | 'ai_ml' | 'disease' | 'disease_ranges' | 'probability' | 'multimodal' | 'data' | 'databases' | 'system' | 'security';

const DISPLAY_SUBTABS: { id: 'gauge' | 'realtime' | 'disease'; name: string }[] = [
  { id: 'gauge', name: 'Gauge' },
  { id: 'realtime', name: 'SENSOR' },
  { id: 'disease', name: 'REAL_TIME_M' },
];

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('display');
  const [displaySubTab, setDisplaySubTab] = useState<'gauge' | 'realtime' | 'disease'>('gauge');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-black flex text-white">
        {/* Left Sidebar - Green panel (turbine style) */}
        <aside
          className={`
          flex flex-col bg-lime-500/90 border-r border-lime-400/50
          transition-all duration-300 ease-out shrink-0
          ${sidebarOpen ? 'w-52' : 'w-16'}
        `}
        >
          <div className="p-3 border-b border-lime-400/50 shrink-0">
            <div className="font-bold text-lime-900 text-sm">NEUROPREDICT</div>
            <div className="text-xs text-lime-800 font-medium">Monitoring</div>
          </div>
          <nav className="flex-1 py-2 overflow-y-auto">
            {sidebarOpen && (
              <>
                <div className="px-3 py-1 text-[10px] uppercase text-lime-800 font-semibold">Display</div>
                {DISPLAY_SUBTABS.map((st) => (
                  <button
                    key={st.id}
                    onClick={() => { setActiveTab(st.id); setDisplaySubTab(st.id); }}
                    className={`w-full text-left px-3 py-2 text-sm font-medium transition-colors ${
                      displaySubTab === st.id ? 'bg-lime-600 text-white' : 'text-lime-900 hover:bg-lime-400'
                    }`}
                  >
                    {st.name}
                  </button>
                ))}
                <div className="px-3 py-1 text-[10px] uppercase text-lime-800 font-semibold mt-2">Modules</div>
                {[
                  { id: 'checklist', name: 'Check List' },
                  { id: 'alarm', name: 'Alarm Systems' },
                  { id: 'control', name: 'Control' },
                  { id: 'graph', name: 'Graph_Analysis' },
                  { id: '3d', name: '3D_Analysis_OP' },
                  { id: 'reporting', name: 'Reporting' },
                  { id: 'clinical', name: 'Connection' },
                  { id: 'data', name: 'Data Loggers' },
                  { id: 'databases', name: 'Databases' },
                  { id: 'ai_ml', name: 'AI/ML Health' },
                  { id: 'disease_ranges', name: 'Disease Tracking' },
                  { id: 'probability', name: 'Disease Probability' },
                  { id: 'multimodal', name: 'Multimodal' },
                  { id: 'system', name: 'System' },
                  { id: 'security', name: 'Security' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    className={`w-full text-left px-3 py-2 text-sm font-medium transition-colors ${
                      activeTab === tab.id ? 'bg-slate-800 text-white border-l-2 border-slate-500' : 'text-lime-900 hover:bg-lime-400'
                    }`}
                  >
                    {tab.name}
                  </button>
                ))}
              </>
            )}
          </nav>
          {sidebarOpen && (
            <div className="p-2 border-t border-lime-400/50 text-[10px] text-lime-800">
              Admin Dashboard v1
            </div>
          )}
        </aside>

        {/* Main Content - Dark background */}
        <main className="flex-1 flex flex-col min-w-0 bg-black">
          <header className="h-12 shrink-0 flex items-center justify-between px-4 border-b border-slate-800 bg-slate-900/50">
            <h1 className="text-sm font-semibold text-slate-200">
              {(activeTab === 'gauge' || activeTab === 'realtime' || (activeTab === 'display' && ['gauge','realtime'].includes(displaySubTab))) && 'Gauge / SENSOR Display'}
              {(activeTab === 'disease' || displaySubTab === 'disease') && 'Disease Tracking — REAL_TIME_M'}
              {activeTab === 'disease_ranges' && 'Disease Tracking'}
              {activeTab === 'ai_ml' && 'AI/ML Health'}
              {activeTab === 'clinical' && 'Connection'}
              {(activeTab === 'data' || activeTab === 'databases') && 'Data Loggers / Databases'}
              {activeTab === 'probability' && 'Disease Probability'}
              {activeTab === 'multimodal' && 'Multimodal Analysis'}
              {activeTab === 'system' && 'System'}
              {activeTab === 'security' && 'Security'}
              {activeTab === 'alarm' && 'Alarm Systems'}
              {activeTab === 'graph' && 'Graph Analysis'}
              {activeTab === '3d' && '3D Analysis'}
              {activeTab === 'reporting' && 'Reporting'}
              {activeTab === 'checklist' && 'Check List'}
              {activeTab === 'control' && 'Control'}
            </h1>
            <button
              type="button"
              onClick={() => setSidebarOpen((o) => !o)}
              className="p-1.5 rounded text-slate-400 hover:bg-slate-700 hover:text-white"
              aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
          </header>

          <div className="flex-1 p-4 lg:p-6 overflow-auto">
            {(activeTab === 'display' || activeTab === 'gauge' || displaySubTab === 'gauge') && <GaugeDisplayTab />}
            {(activeTab === 'realtime' || displaySubTab === 'realtime') && <GaugeDisplayTab />}
            {(activeTab === 'disease' || displaySubTab === 'disease') && <DiseaseTrackingDashboard />}
            {activeTab === 'disease_ranges' && <DiseaseRanges />}
            {activeTab === 'ai_ml' && <AIMLHealth />}
            {activeTab === 'clinical' && <ClinicalMonitoring />}
            {(activeTab === 'data' || activeTab === 'databases') && <DataTab />}
            {activeTab === 'multimodal' && <MultimodalAnalysis />}
            {activeTab === 'probability' && <DiseaseProbability />}
            {activeTab === 'system' && <SystemHealth />}
            {activeTab === 'security' && <SecurityMonitoring />}
            {(activeTab === 'alarm' || activeTab === 'checklist' || activeTab === 'control') && <ClinicalMonitoring />}
            {activeTab === 'graph' && <MultimodalAnalysis />}
            {activeTab === '3d' && <DataTab />}
            {activeTab === 'reporting' && <DiseaseProbability />}
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}
