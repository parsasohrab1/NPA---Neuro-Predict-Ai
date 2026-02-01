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

type TabType =
  | 'gauge'
  | 'disease'
  | 'disease_ranges'
  | 'probability'
  | 'ai_ml'
  | 'clinical'
  | 'data'
  | 'multimodal'
  | 'system'
  | 'security'
  | 'alarm'
  | 'graph'
  | '3d'
  | 'reporting'
  | 'checklist'
  | 'control'
  | 'databases';

const NAV_ITEMS: { id: TabType; label: string; group: string }[] = [
  { id: 'gauge', label: 'Overview', group: 'Main' },
  { id: 'disease', label: 'Disease Tracking', group: 'Main' },
  { id: 'disease_ranges', label: 'Risk Ranges', group: 'Disease' },
  { id: 'probability', label: 'Probability', group: 'Disease' },
  { id: 'data', label: 'Data', group: 'Data' },
  { id: 'multimodal', label: 'Multimodal', group: 'Data' },
  { id: 'system', label: 'System', group: 'System' },
  { id: 'ai_ml', label: 'AI/ML', group: 'System' },
  { id: 'clinical', label: 'Clinical', group: 'System' },
  { id: 'security', label: 'Security', group: 'System' },
];

const TAB_LABELS: Record<TabType, string> = {
  gauge: 'Overview',
  disease: 'Disease Tracking',
  disease_ranges: 'Risk Ranges',
  probability: 'Disease Probability',
  ai_ml: 'AI/ML Health',
  clinical: 'Clinical Monitoring',
  data: 'Data',
  multimodal: 'Multimodal Analysis',
  system: 'System Health',
  security: 'Security',
  alarm: 'Alarm Systems',
  graph: 'Graph Analysis',
  '3d': '3D Analysis',
  reporting: 'Reporting',
  checklist: 'Check List',
  control: 'Control',
  databases: 'Databases',
};

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('gauge');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const groups = Array.from(new Set(NAV_ITEMS.map((i) => i.group)));
  const renderContent = () => {
    if (activeTab === 'gauge') return <GaugeDisplayTab />;
    if (activeTab === 'disease') return <DiseaseTrackingDashboard />;
    if (activeTab === 'disease_ranges') return <DiseaseRanges />;
    if (activeTab === 'ai_ml') return <AIMLHealth />;
    if (activeTab === 'clinical') return <ClinicalMonitoring />;
    if (activeTab === 'data' || activeTab === 'databases') return <DataTab />;
    if (activeTab === 'multimodal') return <MultimodalAnalysis />;
    if (activeTab === 'probability') return <DiseaseProbability />;
    if (activeTab === 'system') return <SystemHealth />;
    if (activeTab === 'security') return <SecurityMonitoring />;
    if (['alarm', 'checklist', 'control'].includes(activeTab)) return <ClinicalMonitoring />;
    if (activeTab === 'graph') return <MultimodalAnalysis />;
    if (activeTab === '3d') return <DataTab />;
    if (activeTab === 'reporting') return <DiseaseProbability />;
    return <GaugeDisplayTab />;
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-slate-950 flex">
        {/* Sidebar */}
        <aside
          className={`
            flex flex-col bg-slate-900 border-r border-slate-700/80 shrink-0
            transition-all duration-300
            ${sidebarOpen ? 'w-56' : 'w-14'}
          `}
        >
          <div className="h-14 flex items-center px-4 border-b border-slate-700/80 shrink-0">
            <div className="font-semibold text-slate-100 text-base truncate">
              {sidebarOpen ? 'NeuroPredict' : 'NP'}
            </div>
          </div>
          <nav className="flex-1 py-4 overflow-y-auto">
            {sidebarOpen &&
              groups.map((group) => (
                <div key={group} className="mb-4">
                  <div className="px-4 py-1.5 text-xs font-medium text-slate-500 uppercase tracking-wider">
                    {group}
                  </div>
                  {NAV_ITEMS.filter((i) => i.group === group).map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`
                        w-full text-left px-4 py-2.5 text-sm font-medium transition-colors
                        ${activeTab === item.id
                          ? 'bg-emerald-600/20 text-emerald-400 border-l-2 border-emerald-500'
                          : 'text-slate-300 hover:bg-slate-800 hover:text-slate-100 border-l-2 border-transparent'}
                      `}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              ))}
          </nav>
          {sidebarOpen && (
            <div className="p-3 border-t border-slate-700/80 text-xs text-slate-500">
              Admin v1
            </div>
          )}
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col min-w-0">
          <header className="h-14 shrink-0 flex items-center justify-between px-6 border-b border-slate-700/80 bg-slate-900/30">
            <h1 className="text-lg font-semibold text-slate-100">
              {TAB_LABELS[activeTab] || 'Overview'}
            </h1>
            <button
              type="button"
              onClick={() => setSidebarOpen((o) => !o)}
              className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-colors"
              aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
          </header>

          <div className="flex-1 p-6 overflow-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}
